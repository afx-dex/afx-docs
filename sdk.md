---
description: Install the official AFX Python SDK and run examples.
icon: download
---

# Python SDK

The official Python SDK is maintained in [`afx-dex/afx-python-sdk`](https://github.com/afx-dex/afx-python-sdk).

Use this project instead of downloading standalone SDK files from the docs. The SDK includes the generated protobuf module under `afx.protos`, so users do not need to download `dex.proto`, generate `dex_pb2.py`, or keep a local `dex_client.py`.

## Install

```bash
git clone https://github.com/afx-dex/afx-python-sdk.git
cd afx-python-sdk
python3 -m pip install -e .
```

## Configure Wallets

Private keys are loaded only from environment variables:

```bash
export AFX_MASTER_PRIVATE_KEY="0xYOUR_MASTER_PRIVATE_KEY"
export AFX_AGENT_PRIVATE_KEY="0xYOUR_AGENT_PRIVATE_KEY"
```

## Client Layout

```python
from afx import AfxClient

client = AfxClient.from_env(testnet=True)

products = client.info.get_products()
order = client.exchange.place_order(
    symbol_code=1,
    px="50000",
    qty="0.001",
    side="BUY",
    ord_type="LIMIT",
    tif="GTC",
)
```

Trading actions are under `client.exchange`, read-only queries are under `client.info`, and WebSocket helpers are under `client.websocket`.

For order requests, pass active order types such as `"LIMIT"` or `"MARKET"`. The proto default `"NONE"` and display-only `OrdType` values such as `"MARKET_LIQ_SELLOFF"`, `"LIMIT_LIQ_SELLOFF"`, `"ADL"`, and `"LIQUIDATION"` may appear in query or stream data, but they must not be used in order requests.

## Examples

Every public SDK feature has an example under the SDK repository's `examples/` directory:

```bash
python3 examples/info/get_products.py
python3 examples/exchange/place_order.py
python3 examples/exchange/replace_order.py
python3 examples/exchange/place_bracket_order.py
python3 examples/websocket/subscribe_ticker.py
```

### Example Index

**Info queries**

* [get_products.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/info/get_products.py)
* [get_wallet.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/info/get_wallet.py)
* [get_orders.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/info/get_orders.py)
* [get_positions.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/info/get_positions.py)
* [get_kline.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/info/get_kline.py)
* [get_agents.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/info/get_agents.py)
* [get_active_agent.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/info/get_active_agent.py)
* [get_funding_rate_current.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/info/get_funding_rate_current.py)

**Exchange actions**


* [faucet_claim.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/faucet_claim.py)
* [approve_agent.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/approve_agent.py)
* [revoke_agent.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/revoke_agent.py)
* [place_order.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/place_order.py)
* [place_tp_sl_orders.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/place_tp_sl_orders.py)
* [replace_order.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/replace_order.py)
* [place_bracket_order.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/place_bracket_order.py)
* [cancel_order.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/cancel_order.py)
* [cancel_all.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/cancel_all.py)
* [set_leverage.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/set_leverage.py)
* [set_margin_mode.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/set_margin_mode.py)
* [assign_pos_margin.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/assign_pos_margin.py)
* [withdraw.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/withdraw.py)
* [vault_deposit.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/vault_deposit.py)
* [vault_withdraw.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/vault_withdraw.py)
* [bind_referral.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/bind_referral.py)

**WebSocket and advanced usage**

* [subscribe.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/websocket/subscribe.py)
* [subscribe_order_book.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/websocket/subscribe_order_book.py)
* [subscribe_ticker.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/websocket/subscribe_ticker.py)
* [subscribe_account_state.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/websocket/subscribe_account_state.py)
* [multiple_wallets.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/advanced/multiple_wallets.py)

## Verify

```bash
python3 -m unittest discover -s tests -v
```

The SDK tests cover signing helpers, protobuf serialization, client behavior, and example imports.
