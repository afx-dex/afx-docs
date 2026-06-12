# Canonical First Trade For Coding Agents

Paste this task into Codex, Claude Code, OpenClaw, or another coding agent.

## Task

Build and run the smallest safe AFX DEX testnet trading script using the official Python SDK.

## Requirements

- Do not print private keys.
- Load keys only from `AFX_MASTER_PRIVATE_KEY` and `AFX_AGENT_PRIVATE_KEY`.
- Use testnet.
- Claim faucet funds.
- Approve the agent wallet.
- Query products and find BTCUSDC by symbol.
- Place one small limit buy order far below market.
- Cancel the order.
- Print a short result summary: product code, approve result code, place tx hash, cancel tx hash.

## Implementation

```bash
git clone https://github.com/afx-dex/afx-python-sdk.git
cd afx-python-sdk
python3 -m pip install -e .
```

Create `first_trade.py`:

```python
from afx import AfxClient


def require_ok(name, response):
    if response.get("code") != 0:
        raise RuntimeError(f"{name} failed: {response}")
    return response


client = AfxClient.from_env(testnet=True)

faucet = require_ok("faucet_claim", client.exchange.faucet_claim())
approve = require_ok(
    "approve_agent",
    client.exchange.approve_agent(
        agent_name="afx-agent-first-trade",
        validity_seconds=604800,
    ),
)

products = require_ok("get_products", client.info.get_products())
btc = next(
    product
    for product in products["data"]["perpProducts"]
    if product["symbol"] == "BTCUSDC"
)
symbol_code = int(btc["code"])

place = require_ok(
    "place_order",
    client.exchange.place_order(
        symbol_code=symbol_code,
        px="50000",
        qty="0.001",
        side="BUY",
        ord_type="LIMIT",
        tif="GTC",
    ),
)

cancel = require_ok(
    "cancel_all",
    client.exchange.cancel_all(symbol_code=symbol_code),
)

print(
    {
        "symbolCode": symbol_code,
        "faucetCode": faucet.get("code"),
        "approveCode": approve.get("code"),
        "placeTxHash": place.get("data", {}).get("txHash"),
        "cancelTxHash": cancel.get("data", {}).get("txHash"),
    }
)
```

Run:

```bash
python3 first_trade.py
```

