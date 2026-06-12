# AFX DEX Agent Instructions

This repository is optimized for coding agents that need to build against AFX DEX.

## Start Here

1. Read `llms.txt`.
2. Use `afx-api/agent-guides/first-trade.md` for the canonical first trade task.
3. Use `afx-api/artifacts/openapi.json` for REST endpoints.
4. Use `afx-api/artifacts/asyncapi.json` for WebSocket channels.
5. Use the official SDKs unless the user explicitly asks for raw signing.

## Rules

- Never print or commit private keys.
- Prefer testnet for first runs.
- Use current millisecond timestamps for `nonce`.
- Use Unix seconds for `withdrawSequence`.
- Do not use display-only order types in requests.
- Query product metadata before choosing product codes, leverage, or quantity.
- Cancel test orders after placing them.

## Official SDKs

- Python: `https://github.com/afx-dex/afx-python-sdk`
- JavaScript: `https://github.com/afx-dex/afx-js-sdk`

