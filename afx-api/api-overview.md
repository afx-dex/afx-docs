---
description: Programmatic interface for perpetual contract trading on the Phemex DEX.
icon: brackets-curly
layout:
  width: wide
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# API

Phemex DEX is a fully on-chain perpetual futures exchange. No API keys required — all requests are authenticated via EIP-712 signatures from Ethereum wallets.

<a href="quickstart.md" class="button primary">Quick Start — First Trade in 5 Minutes</a>

## Base URLs

| Environment | Exchange API | Info API | WebSocket |
| ----------- | ------------ | -------- | --------- |
| **Mainnet** | `https://api10.afx.xyz/api/v1/exchange` | `https://api10.afx.xyz/info/...` | `wss://ws10.afx.xyz/ws/dex` |
| **Testnet** | `https://api10-testnet.afx.xyz/api/v1/exchange` | `https://api10-testnet.afx.xyz/info/...` | `wss://ws10-testnet.afx.xyz/ws/dex` |

{% hint style="info" %}
Start with the **Testnet** environment. Use `faucetClaim` to get free test funds.
{% endhint %}

## API Categories

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
            <td><strong>Exchange API</strong></td>
            <td>POST /api/v1/exchange — Place/cancel orders, set leverage, vault management. Requires EIP-712 signature.</td>
            <td><a href="exchange.md">Exchange API</a></td>
        </tr>
        <tr>
            <td><strong>Info API</strong></td>
            <td>GET /info/... — Query account, orders, positions, trades, kline, funding rate. No signature required.</td>
            <td><a href="info.md">Info API</a></td>
        </tr>
        <tr>
            <td><strong>WebSocket</strong></td>
            <td>Real-time orderbook, kline, ticker, trades, and account state updates via persistent connection.</td>
            <td><a href="websocket.md">WebSocket</a></td>
        </tr>
    </tbody>
</table>

## Authentication

{% columns %}
{% column %}
### Master Wallet

Controls funds and permissions.

Signs: `approveAgent`, `withdraw`, `usdSend`

Domain: `SignTransaction`
{% endcolumn %}

{% column %}
### Agent Wallet

Authorized by Master for daily trading.

Signs: `placeOrder`, `cancelOrder`, `setLeverage`, and all other trading operations.

Domain: `Exchange`
{% endcolumn %}
{% endcolumns %}

See [Authentication](signing.md) for the full EIP-712 signing specification.

## Common Response Format

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

<details>
<summary>Error Codes</summary>

| Code | Description |
| ---- | ----------- |
| `0` | Success |
| `40201` | Unsupported action type |
| `40204` | Signature verification failed |
| `40207` | Invalid nonce |
| `40208` | Request expired |
| `40220` | Rate limit exceeded |
| `40230` | Blockchain call failed |
| `40231` | Transaction broadcast failed |
| `40280` | Action disabled (emergency) |
| `40281` | Address banned |

</details>

## Available Symbols

Query `GET /info/public/product-meta` for the full list.

| Symbol | Code | Max Leverage | Settlement |
| ------ | ---- | ------------ | ---------- |
| BTCUSDC | 1 | 100x | USDC |
| ETHUSDC | 2 | 100x | USDC |
| SOLUSDC | 3 | 50x | USDC |
| XRPUSDC | 4 | 50x | USDC |

## Rate Limits

| Dimension | Limit |
| --------- | ----- |
| Per address per action | Configurable per action type |
| WebSocket connections per IP | 10 |
| WebSocket subscriptions per connection | 50 |
| WebSocket messages per second | 50 |
