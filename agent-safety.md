---
description: Operational safety guidance for Master wallets, Agent wallets, and automated trading systems.
icon: shield-check
---

# Agent Safety

AFX separates account control from day-to-day trading by using two wallet roles.

| Wallet | Use it for | Do not use it for |
| --- | --- | --- |
| Master wallet | Holding funds, approving Agents, revoking Agents, account withdrawals | Automated trading runtimes, bots, CI jobs, or hosted agent environments |
| Agent wallet | Placing/canceling orders, setting leverage, margin mode, and other authorized trading actions | Account withdrawals or long-lived custody of user funds |

{% hint style="warning" %}
Never place the Master private key in an automated trading process. The Master wallet controls funds and Agent authorization.
{% endhint %}

## Recommended Runtime Model

1. Create a dedicated Agent wallet for each bot or strategy.
2. Approve the Agent from the Master wallet with the shortest practical validity period.
3. Store only the Agent private key in the trading runtime.
4. Query product metadata before choosing symbols, product codes, leverage, precision, or order size.
5. Keep an operational runbook for canceling orders and revoking the Agent.

## Revoke an Agent

Use revocation when rotating keys, stopping a strategy, or responding to suspected key exposure.

```python
from afx import AfxClient

client = AfxClient.from_env(testnet=True)
client.exchange.revoke_agent(agent_name="my-bot")
```

Under the hood, revocation submits an `approveAgent` action with the zero address:

```json
{
  "type": "approveAgent",
  "agentAddress": "0x0000000000000000000000000000000000000000",
  "validitySeconds": 0
}
```

## Rotate an Agent Key

1. Stop the old bot process.
2. Revoke the old Agent.
3. Create a new Agent wallet.
4. Approve the new Agent from the Master wallet.
5. Restart the bot with only the new Agent key.
6. Verify account state, open orders, and positions before resuming normal sizing.

## Vault Operations

Vault actions are not the same risk class as ordinary order placement.

| Operation area | Safety note |
| --- | --- |
| Trading on the Master account | Agent actions can change market exposure but cannot withdraw account funds to an external address. |
| Vault-context actions | A vault-authorized Agent may affect vault balances, ownership, withdrawal flow, or vault lifecycle depending on the action. |
| Account withdrawals | Master-signed operation. Keep this outside automated trading infrastructure. |

Before granting automated access to vault workflows, review the exact operation and confirm the intended authority boundary for that vault.

## Testnet First

Run new agents on testnet before mainnet:

1. Claim testnet funds.
2. Approve an Agent wallet.
3. Query `GET /info/public/product-meta`.
4. Place a small limit order away from market.
5. Cancel the order.
6. Revoke or rotate the Agent if the environment was temporary.
