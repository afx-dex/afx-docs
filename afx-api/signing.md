---
description: EIP-712 structured signing for Agent and Master wallet operations.
icon: key
---

# Signing

Phemex DEX uses [EIP-712](https://eips.ethereum.org/EIPS/eip-712) structured signatures for authentication. No API keys or sessions — every Exchange request is signed by an Ethereum wallet.

{% columns %}
{% column %}
### Agent Signature

Used for most trading operations. The Agent wallet signs a hash derived from the **protobuf-serialized** action payload.

**Domain:** `Exchange`

**Operations:** `placeOrder`, `cancelOrder`, `cancelAll`, `setLeverage`, `setMarginMode`, `assignPosMargin`, `bindReferral`, all vault operations.
{% endcolumn %}

{% column %}
### Master Signature

Used for privileged operations. The Master wallet signs the action fields **directly** as EIP-712 message — no protobuf involved.

**Domain:** `SignTransaction`

**Operations:** `approveAgent`, `withdraw`, `usdSend`, `faucetClaim`.
{% endcolumn %}
{% endcolumns %}

---

## Agent Signing Process

{% stepper %}
{% step %}
### Serialize action to Protobuf

Encode the action fields using the corresponding protobuf message (e.g. `MsgPlaceOrders` for placeOrder).

- JSON camelCase fields map to protobuf snake\_case
- Enum values use **integers** (e.g. `LIMIT` = `1`)
- Zero values are omitted per proto3 rules
{% endstep %}

{% step %}
### Compute connectionId

```
connectionId = keccak256(
    proto_bytes
    + bytes(vaultAddress)              // strip 0x, decode hex. empty if null
    + little_endian_uint64(nonce)       // 8 bytes
    + little_endian_uint64(expiryAfter) // 8 bytes, null → 0
)
```
{% endstep %}

{% step %}
### Sign EIP-712

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
    "verifyingContract": "0x0000000000000000000000000000000000000000"
  },
  "message": {
    "source":       "b",
    "connectionId": "0x<step2_result>"
  }
}
```

| Field | Value |
| ----- | ----- |
| `source` | `"a"` = Mainnet, `"b"` = Testnet |
| `chainId` | Mainnet: `42161`, Testnet: `421614` |
| `verifyingContract` | Always zero address |
{% endstep %}
{% endstepper %}

{% tabs %}
{% tab title="Python" %}
```python
from dex_client import DexClient

client = DexClient(
    master_key="0x...", agent_key="0x...", testnet=True,
)

# Agent-signed operations just work — SDK handles signing internally
result = client.place_order(symbol_code=1, px="40000", qty="0.5", side="BUY")
```
{% endtab %}

{% tab title="JavaScript" %}
```javascript
import { DexClient } from "./dex_client.mjs";

const client = await DexClient.create({
  masterKey: "0x...", agentKey: "0x...", testnet: true,
});

// Agent-signed operations just work — SDK handles signing internally
const result = await client.placeOrder({ symbolCode: 1, px: "40000", qty: "0.5", side: "BUY" });
```
{% endtab %}
{% endtabs %}

---

## Master Signing Process

Master wallet signs the action fields **directly** as an EIP-712 message. No protobuf serialization.

Each action has its own EIP-712 type definition. Common domain:

```json
{
  "name":              "SignTransaction",
  "version":           "1",
  "chainId":           421614,
  "verifyingContract": "0x0000000000000000000000000000000000000000"
}
```

### approveAgent

```json
{
  "ApproveAgent": [
    { "name": "dexChain",     "type": "string"  },
    { "name": "agentAddress", "type": "address" },
    { "name": "agentName",    "type": "string"  },
    { "name": "nonce",        "type": "uint64"  },
    { "name": "expiryAfter",  "type": "uint64"  }
  ]
}
```

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

### usdSend

```json
{
  "UsdTransfer": [
    { "name": "dexChain",    "type": "string"  },
    { "name": "to",          "type": "address" },
    { "name": "amount",      "type": "string"  },
    { "name": "nonce",       "type": "uint64"  },
    { "name": "expiryAfter", "type": "uint64"  }
  ]
}
```

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
`nonce` and `expiryAfter` come from the outer request fields, not the action body. When `expiryAfter` is `null`, use `0` in the signature.
{% endhint %}

{% hint style="info" %}
Signature `r` and `s` values must be zero-padded to exactly 32 bytes (64 hex characters). For example in Python: `"0x" + format(signed.r, "064x")`
{% endhint %}
