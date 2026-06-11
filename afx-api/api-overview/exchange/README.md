---
description: Trading operations — place, replace, bracket, and cancel orders; set leverage; manage vaults.
icon: arrow-right-arrow-left
---

# Exchange API

All trading operations go through a single endpoint:

```
POST /api/v1/exchange
```

The `action.type` field determines which operation to execute. Every request requires an EIP-712 signature. See [Authentication](../signing.md) for signing details.

## Python SDK Examples

The official SDK repository includes runnable examples for common Exchange actions:

* Orders: [place_order.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/place_order.py), [place_tp_sl_orders.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/place_tp_sl_orders.py), [replace_order.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/replace_order.py), [place_bracket_order.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/place_bracket_order.py), [cancel_order.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/cancel_order.py), [cancel_all.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/cancel_all.py)
* Authorization: [faucet_claim.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/faucet_claim.py), [approve_agent.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/approve_agent.py), [revoke_agent.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/revoke_agent.py)
* Account settings: [set_leverage.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/set_leverage.py), [set_margin_mode.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/set_margin_mode.py), [assign_pos_margin.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/assign_pos_margin.py)
* Funds and vaults: [withdraw.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/withdraw.py), [vault_deposit.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/vault_deposit.py), [vault_withdraw.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/vault_withdraw.py), [bind_referral.py](https://github.com/afx-dex/afx-python-sdk/blob/main/examples/exchange/bind_referral.py)

## Agent Revocation

Use `revoke_agent.py` or `client.exchange.revoke_agent(...)` to revoke the currently approved Agent wallet. The SDK submits an `approveAgent` action with the zero address and `validitySeconds=0`.

Revocation is a **Master wallet** operation. Keep it available in operational runbooks so automated trading access can be disabled quickly.
