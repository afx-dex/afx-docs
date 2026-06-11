# Codex Instructions For AFX DEX

When asked to build or test against AFX DEX:

1. Read `llms.txt` and `afx-api/agent-guides/first-trade.md`.
2. Use the official SDK first.
3. Keep secrets in environment variables only.
4. Run testnet examples before mainnet.
5. After any trading test, verify there are no unintended open positions and cancel resting orders.

Useful files:

- `afx-api/artifacts/openapi.json`
- `afx-api/artifacts/asyncapi.json`
- `afx-api/artifacts/schemas/signed-actions.schema.json`

