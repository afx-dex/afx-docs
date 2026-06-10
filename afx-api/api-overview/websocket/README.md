---
description: Real-time market data and account updates via WebSocket.
icon: bolt
---

# WebSocket

Persistent connection for real-time orderbook, kline, ticker, trades, and account state updates.

| Environment | URL |
| ----------- | --- |
| Mainnet | `wss://ws10.afx.xyz/ws/dex` |
| Testnet | `wss://ws10-testnet.afx.xyz/ws/dex` |

## Python SDK Examples

The official SDK repository includes runnable WebSocket examples:

* [subscribe.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/websocket/subscribe.py)
* [subscribe_order_book.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/websocket/subscribe_order_book.py)
* [subscribe_ticker.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/websocket/subscribe_ticker.py)
* [subscribe_account_state.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/websocket/subscribe_account_state.py)
