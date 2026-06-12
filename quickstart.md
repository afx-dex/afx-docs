---
description: Place your first trade on AFX DEX in 5 minutes.
icon: rocket
---

# Quick Start

{% hint style="info" %}
This guide uses the **Testnet** environment. All operations are free -- use `faucet_claim` to get test funds.
{% endhint %}

## Prerequisites

Two Ethereum wallets are required:

{% columns %}
{% column %}
**Master Wallet**

Controls funds and permissions.

Used to sign `approveAgent` and `withdraw`.
{% endcolumn %}

{% column %}
**Agent Wallet**

Handles day-to-day trading.

Used to sign `placeOrder`, `replaceOrder`, `placeBracketOrder`, `cancelOrder`, `setLeverage`, etc.
{% endcolumn %}
{% endcolumns %}

Store private keys in environment variables. The Python SDK loads keys from the environment and does not accept private keys in public client constructors.

```bash
export AFX_MASTER_PRIVATE_KEY="0xYOUR_MASTER_PRIVATE_KEY"
export AFX_AGENT_PRIVATE_KEY="0xYOUR_AGENT_PRIVATE_KEY"
```

{% hint style="info" %}
On mainnet, the minimum deposit is 10 USDC and the minimum withdrawal is 2 USDC. Testnet examples use faucet funds instead of real deposits.
{% endhint %}

## Install Python SDK

The official Python SDK is maintained in [`afx-dex/afx-python-sdk`](https://github.com/afx-dex/afx-python-sdk). Do not download `dex_client.py`, `dex.proto`, or `dex_pb2.py` from these docs.

```bash
git clone https://github.com/afx-dex/afx-python-sdk.git
cd afx-python-sdk
python3 -m pip install -e .
```

The SDK vendors the generated protobuf module under `afx.protos`, so no manual protobuf compilation is required.

Runnable examples for this flow:

* [faucet_claim.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/faucet_claim.py)
* [approve_agent.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/approve_agent.py)
* [get_products.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/info/get_products.py)
* [place_order.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/place_order.py)
* [replace_order.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/replace_order.py)
* [place_bracket_order.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/place_bracket_order.py)
* [subscribe_order_book.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/websocket/subscribe_order_book.py)

## First Trade

{% stepper %}
{% step %}
**Initialize the client**

```python
from afx import AfxClient

client = AfxClient.from_env(testnet=True)
```
{% endstep %}

{% step %}
**Claim testnet funds**

Get 500 USDC from the testnet faucet. Signed by the **Master** wallet.

```python
result = client.exchange.faucet_claim()
print(result)  # {"code": 0, "message": "success", ...}
```
{% endstep %}

{% step %}
**Authorize the agent wallet**

The Master wallet grants the Agent wallet permission to trade until the authorization expires.

```python
result = client.exchange.approve_agent(
    agent_name="my-bot",
    validity_seconds=604800,
)
print(result)
```
{% endstep %}

{% step %}
**Query available symbols**

```python
products = client.info.get_products()
for p in products["data"]["perpProducts"][:3]:
    print(f"{p['symbol']} (code: {p['code']}, leverage: {p['maxLeverage']}x)")
```

Use the returned `code` value when placing orders. Do not hardcode product codes or leverage values from examples, because markets and risk parameters can change.
{% endstep %}

{% step %}
**Place a limit order**

Signed by the **Agent** wallet. This places a buy order far below market price so it won't fill immediately.

```python
btc = next(p for p in products["data"]["perpProducts"] if p["symbol"] == "BTCUSDC")

result = client.exchange.place_order(
    symbol_code=int(btc["code"]),
    px="50000.0",      # limit price
    qty="0.001",       # quantity in BTC
    side="BUY",
    ord_type="LIMIT",
    tif="GTC",         # Good Till Cancelled
)
print(f"txHash: {result['data']['txHash']}")
```

{% hint style="success" %}
You've placed your first order! The transaction is submitted to the blockchain and confirmed within seconds.
{% endhint %}
{% endstep %}
{% endstepper %}

## Subscribe to Market Data

Connect to real-time orderbook updates via WebSocket.

```python
import asyncio

async def main():
    message = await client.websocket.subscribe_order_book(
        symbol="BTCUSDC",
        depth=5,
        timeout=10,
    )
    book = message["data"]["book"]
    print(f"Best bid: {book['bids'][0]}, Best ask: {book['asks'][0]}")

asyncio.run(main())
```

## What's Next

<table data-view="cards"><thead><tr><th>Title</th><th>Description</th><th data-card-target data-type="content-ref">Target</th></tr></thead><tbody><tr><td><strong>Python SDK</strong></td><td>Install the SDK and run the official examples.</td><td><a href="sdk.md">sdk.md</a></td></tr><tr><td><strong>Authentication</strong></td><td>How EIP-712 signing works -- Agent vs Master wallet.</td><td><a href="signing.md">signing.md</a></td></tr><tr><td><strong>Exchange API</strong></td><td>All trading operations -- orders, leverage, vaults.</td><td><a href="exchange/">exchange</a></td></tr><tr><td><strong>Info API</strong></td><td>Query account, orders, positions, market data.</td><td><a href="info/">info</a></td></tr><tr><td><strong>WebSocket</strong></td><td>Real-time orderbook, kline, ticker, and account events.</td><td><a href="websocket/">websocket</a></td></tr></tbody></table>
