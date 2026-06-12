# AFX API Reference

This repository is the GitBook-synced source for the AFX DEX API Reference.

## Canonical Documentation

- Public API Reference: https://afx-docs.gitbook.io/afx/api-reference
- Quick Start: https://afx-docs.gitbook.io/afx/api-reference/quickstart
- Exchange API: https://afx-docs.gitbook.io/afx/api-reference/exchange
- Info API: https://afx-docs.gitbook.io/afx/api-reference/info
- WebSocket API: https://afx-docs.gitbook.io/afx/api-reference/websocket
- Python SDK: https://afx-docs.gitbook.io/afx/api-reference/sdk

## Source Files

- GitBook entry page: `index.md`
- Table of contents: `SUMMARY.md`
- Quick start: `quickstart.md`
- Signing guide: `signing.md`
- SDK guide: `sdk.md`
- OpenAPI specs: `openapi/`
- Machine-readable artifacts: `artifacts/`
- Agent guide: `agent-guides/first-trade.md`

## AI And Agent Entry Points

- LLM index: [`llms.txt`](https://raw.githubusercontent.com/afx-dex/afx-docs/main/llms.txt)
- Full LLM context: [`llms-full.txt`](https://raw.githubusercontent.com/afx-dex/afx-docs/main/llms-full.txt)
- General agent instructions: [`AGENTS.md`](https://raw.githubusercontent.com/afx-dex/afx-docs/main/AGENTS.md)
- Codex instructions: [`CODEX.md`](https://raw.githubusercontent.com/afx-dex/afx-docs/main/CODEX.md)
- Claude Code instructions: [`CLAUDE.md`](https://raw.githubusercontent.com/afx-dex/afx-docs/main/CLAUDE.md)
- OpenClaw instructions: [`OPENCLAW.md`](https://raw.githubusercontent.com/afx-dex/afx-docs/main/OPENCLAW.md)

## Machine-Readable Artifacts

- Combined REST OpenAPI: [`artifacts/openapi.json`](https://raw.githubusercontent.com/afx-dex/afx-docs/main/artifacts/openapi.json)
- Exchange API OpenAPI: [`artifacts/openapi-exchange.json`](https://raw.githubusercontent.com/afx-dex/afx-docs/main/artifacts/openapi-exchange.json)
- Info API OpenAPI: [`artifacts/openapi-info.json`](https://raw.githubusercontent.com/afx-dex/afx-docs/main/artifacts/openapi-info.json)
- WebSocket AsyncAPI: [`artifacts/asyncapi.json`](https://raw.githubusercontent.com/afx-dex/afx-docs/main/artifacts/asyncapi.json)

For integrations, query `GET /info/public/product-meta` before hardcoding symbols, product codes, leverage, or precision.
