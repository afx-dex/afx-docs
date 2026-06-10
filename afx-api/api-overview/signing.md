---
description: EIP-712 structured signing for Agent and Master wallet operations.
icon: key
---

# Signing

AFX DEX uses [EIP-712](https://eips.ethereum.org/EIPS/eip-712) structured signatures for authentication. No API keys or sessions — every Exchange request is signed by an Ethereum wallet.

{% columns %}
{% column %}
#### Agent Signature

Used for most trading operations. The Agent wallet signs a hash derived from the **protobuf-serialized** action payload.

**Domain:** `Exchange`

**Operations:** `placeOrder`, `cancelOrder`, `cancelAll`, `setLeverage`, `setMarginMode`, `assignPosMargin`, `bindReferral`, all vault operations.
{% endcolumn %}

{% column %}
#### Master Signature

Used for privileged operations. The Master wallet signs the action fields **directly** as EIP-712 message — no protobuf involved.

**Domain:** `SignTransaction`

**Operations:** `approveAgent`, `withdraw`, `faucetClaim`.
{% endcolumn %}
{% endcolumns %}

***

## Agent Signing Process

{% stepper %}
{% step %}
#### Serialize action to Protobuf

Encode the action fields using the corresponding protobuf message (e.g. `MsgPlaceOrders` for placeOrder).

* JSON camelCase fields map to protobuf snake\_case
* Enum values use **integers** (e.g. `LIMIT` = `1`)
* Zero values are omitted per proto3 rules
{% endstep %}

{% step %}
#### Compute connectionId

```
connectionId = keccak256(
    proto_bytes
    + bytes(vaultAddress)              // strip 0x, decode hex. empty if null
    + little_endian_uint64(nonce)       // 8 bytes, millisecond timestamp
    + little_endian_uint64(expiryAfter) // 8 bytes, Unix timestamp milliseconds; null → 0
)
```

`nonce` is a `uint64` request nonce. Use the current Unix timestamp in milliseconds (for example `Date.now()` or `int(time.time() * 1000)`) and do not reuse the same nonce for another signed request.

`expiryAfter` is a `uint64` Unix timestamp in milliseconds. The request expires after this timestamp. Use `null` in the request body, and `0` inside the signature payload, when the request should not expire.
{% endstep %}

{% step %}
#### Sign EIP-712

```json
{
  "types": {
    "EIP712Domain": [
      { "name": "name",              "type": "string"  },
      { "name": "version",           "type": "string"  },
      { "name": "chainId",           "type": "uint256" },
      { "name": "verifyingContract", "type": "address" }
    ],
    "Agent": [
      { "name": "source",       "type": "string"  },
      { "name": "connectionId", "type": "bytes32" }
    ]
  },
  "primaryType": "Agent",
  "domain": {
    "name":              "Exchange",
    "version":           "1",
    "chainId":           421614,
    "verifyingContract": "0x0100000000000000000000000000000000000001"
  },
  "message": {
    "source":       "b",
    "connectionId": "0x<step2_result>"
  }
}
```

| Field               | Value                               |
| ------------------- | ----------------------------------- |
| `source`            | `"a"` = Mainnet, `"b"` = Testnet    |
| `chainId`           | Mainnet: `42161`, Testnet: `421614` |
| `verifyingContract` | `0x0100000000000000000000000000000000000001` |
{% endstep %}
{% endstepper %}

For Python applications, use the official [`afx-python-sdk`](https://github.com/afx-dex/afx-python-sdk). The SDK handles protobuf serialization, `connectionId` calculation, and EIP-712 signing internally.

```python
from afx import AfxClient

client = AfxClient.from_env(testnet=True)

# Agent-signed operations just work -- SDK handles signing internally.
result = client.exchange.place_order(
    symbol_code=1,
    px="40000",
    qty="0.5",
    side="BUY",
)
```

***

## Master Signing Process

Master wallet signs the action fields **directly** as an EIP-712 message. No protobuf serialization.

Each action has its own EIP-712 type definition. Common domain:

```json
{
  "name":              "SignTransaction",
  "version":           "1",
  "chainId":           421614,
  "verifyingContract": "0x0100000000000000000000000000000000000001"
}
```

### approveAgent

```json
{
  "ApproveAgent": [
    { "name": "dexChain",     "type": "string"  },
    { "name": "agentAddress", "type": "address" },
    { "name": "agentName",    "type": "string"  },
    { "name": "validitySeconds", "type": "uint64" },
    { "name": "nonce",        "type": "uint64"  },
    { "name": "expiryAfter",  "type": "uint64"  }
  ]
}
```

`validitySeconds` is the agent authorization duration in seconds. `0` means the authorization is valid for 7 days; maximum 365 days.

### withdraw

```json
{
  "Withdraw": [
    { "name": "dexChain",    "type": "string"  },
    { "name": "destination", "type": "address" },
    { "name": "amount",      "type": "string"  },
    { "name": "nonce",       "type": "uint64"  },
    { "name": "expiryAfter", "type": "uint64"  }
  ]
}
```

For withdrawals, use a longer `expiryAfter` window, such as current Unix time in milliseconds + 3,600,000. This gives the withdrawal enough time to pass signature verification and broadcast.

### faucetClaim (Testnet only)

```json
{
  "TestnetFaucetClaim": [
    { "name": "dexChain", "type": "string" }
  ]
}
```

Message: `{ "dexChain": "Testnet" }`, chainId fixed `421614`.

{% hint style="warning" %}
`nonce` and `expiryAfter` come from the outer request fields, not the action body. `nonce` should be the current millisecond timestamp and must not be reused. `expiryAfter` is a Unix timestamp in milliseconds; when it is `null`, use `0` in the signature.
{% endhint %}

{% hint style="info" %}
Signature `r` and `s` values must be zero-padded to exactly 32 bytes (64 hex characters). For example in Python: `"0x" + format(signed.r, "064x")`
{% endhint %}
