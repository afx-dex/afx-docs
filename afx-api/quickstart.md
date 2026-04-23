---
description: Place your first trade on Phemex DEX in 5 minutes.
icon: rocket
---

# Quick Start

{% hint style="info" %}
This guide uses the **Testnet** environment. All operations are free — use `faucetClaim` to get test funds.
{% endhint %}

## Prerequisites

Two Ethereum wallets are required:

{% columns %}
{% column %}
### Master Wallet

Controls funds and permissions.

Used to sign `approveAgent`, `withdraw`, and `usdSend`.
{% endcolumn %}

{% column %}
### Agent Wallet

Handles day-to-day trading.

Used to sign `placeOrder`, `cancelOrder`, `setLeverage`, etc.
{% endcolumn %}
{% endcolumns %}

You can generate both from any Ethereum-compatible library (ethers.js, eth-account, MetaMask, etc.).

## Install SDK

{% tabs %}
{% tab title="Python" %}
```bash
pip install eth-account requests websockets
```

Download [`dex_client.py`](sdk/dex_client.py) to your project directory.
{% endtab %}

{% tab title="JavaScript" %}
```bash
npm install ethers protobufjs ws
```

Download [`dex_client.mjs`](sdk/dex_client.mjs) and [`dex.proto`](sdk/dex.proto) to your project directory.
{% endtab %}
{% endtabs %}

## First Trade

{% stepper %}
{% step %}
### Initialize the client

{% tabs %}
{% tab title="Python" %}
```python
from dex_client import DexClient

client = DexClient(
    master_key="0xYOUR_MASTER_PRIVATE_KEY",
    agent_key="0xYOUR_AGENT_PRIVATE_KEY",
    testnet=True,
)
```
{% endtab %}

{% tab title="JavaScript" %}
```javascript
import { DexClient } from "./dex_client.mjs";

const client = await DexClient.create({
  masterKey: "0xYOUR_MASTER_PRIVATE_KEY",
  agentKey:  "0xYOUR_AGENT_PRIVATE_KEY",
  testnet:   true,
});
```
{% endtab %}
{% endtabs %}
{% endstep %}

{% step %}
### Claim testnet funds

Get 500 USDC from the testnet faucet. Signed by the **Master** wallet.

{% tabs %}
{% tab title="Python" %}
```python
result = client.faucet_claim()
print(result)  # {"code": 0, "message": "success", ...}
```
{% endtab %}

{% tab title="JavaScript" %}
```javascript
const result = await client.faucetClaim();
console.log(result);  // { code: 0, message: "success", ... }
```
{% endtab %}
{% endtabs %}
{% endstep %}

{% step %}
### Authorize the agent wallet

The Master wallet grants the Agent wallet permission to trade. This only needs to be done once.

{% tabs %}
{% tab title="Python" %}
```python
result = client.approve_agent(agent_name="my-bot")
print(result)
```
{% endtab %}

{% tab title="JavaScript" %}
```javascript
const result = await client.approveAgent({ agentName: "my-bot" });
console.log(result);
```
{% endtab %}
{% endtabs %}
{% endstep %}

{% step %}
### Query available symbols

{% tabs %}
{% tab title="Python" %}
```python
products = client.get_products()
for p in products["data"]["perpProducts"][:3]:
    print(f"{p['symbol']} (code: {p['code']}, leverage: {p['maxLeverage']}x)")
```
{% endtab %}

{% tab title="JavaScript" %}
```javascript
const products = await client.getProducts();
products.data.perpProducts.slice(0, 3).forEach(p =>
  console.log(`${p.symbol} (code: ${p.code}, leverage: ${p.maxLeverage}x)`)
);
```
{% endtab %}
{% endtabs %}

| Symbol | Code | Max Leverage |
| ------ | ---- | ------------ |
| BTCUSDC | 1 | 100x |
| ETHUSDC | 2 | 100x |
| SOLUSDC | 3 | 50x |
{% endstep %}

{% step %}
### Place a limit order

Signed by the **Agent** wallet. This places a buy order far below market price so it won't fill immediately.

{% tabs %}
{% tab title="Python" %}
```python
result = client.place_order(
    symbol_code=1,       # BTCUSDC
    px="50000.0",        # limit price
    qty="0.001",         # quantity in BTC
    side="BUY",
    ord_type="LIMIT",
    tif="GTC",           # Good Till Cancelled
)
print(f"txHash: {result['data']['txHash']}")
```
{% endtab %}

{% tab title="JavaScript" %}
```javascript
const result = await client.placeOrder({
  symbolCode: 1,       // BTCUSDC
  px: "50000.0",       // limit price
  qty: "0.001",        // quantity in BTC
  side: "BUY",
  ordType: "LIMIT",
  tif: "GTC",          // Good Till Cancelled
});
console.log(`txHash: ${result.data.txHash}`);
```
{% endtab %}
{% endtabs %}

{% hint style="success" %}
You've placed your first order! The transaction is submitted to the blockchain and confirmed within seconds.
{% endhint %}
{% endstep %}
{% endstepper %}

## Subscribe to Market Data

Connect to real-time orderbook updates via WebSocket.

{% tabs %}
{% tab title="Python" %}
```python
import asyncio

def on_orderbook(msg):
    book = msg["data"]["book"]
    print(f"Best bid: {book['bids'][0]}, Best ask: {book['asks'][0]}")
    return False  # return False to stop after first message

asyncio.run(client.subscribe(
    {"type": "orderBook", "symbol": "BTCUSDC", "depth": 5},
    on_orderbook,
    timeout=10,
))
```
{% endtab %}

{% tab title="JavaScript" %}
```javascript
await client.subscribe(
  { type: "orderBook", symbol: "BTCUSDC", depth: 5 },
  (msg) => {
    const book = msg.data.book;
    console.log(`Best bid: ${book.bids[0]}, Best ask: ${book.asks[0]}`);
    return false;
  },
  { timeout: 10000 },
);
```
{% endtab %}
{% endtabs %}

## What's Next

<table data-view="cards">
    <thead>
        <tr>
            <th>Title</th>
            <th>Description</th>
            <th data-card-target data-type="content-ref">Target</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Authentication</strong></td>
            <td>How EIP-712 signing works — Agent vs Master wallet.</td>
            <td><a href="authentication.md">Authentication</a></td>
        </tr>
        <tr>
            <td><strong>Exchange API</strong></td>
            <td>All trading operations — orders, leverage, vaults.</td>
            <td><a href="exchange.md">Exchange API</a></td>
        </tr>
        <tr>
            <td><strong>Info API</strong></td>
            <td>Query account, orders, positions, market data.</td>
            <td><a href="info.md">Info API</a></td>
        </tr>
        <tr>
            <td><strong>WebSocket</strong></td>
            <td>Real-time orderbook, kline, ticker, and account events.</td>
            <td><a href="websocket.md">WebSocket</a></td>
        </tr>
    </tbody>
</table>
