---
description: Machine-readable files and AI-agent entry points for AFX DEX.
icon: robot
---

# Agent Artifacts

AFX DEX publishes machine-readable artifacts for coding agents, SDK generators, API clients, and AI-agent trading workflows.

## API Artifacts

| Artifact | Path |
| --- | --- |
| Combined REST OpenAPI | `artifacts/openapi.json` |
| Info API OpenAPI | `artifacts/openapi-info.json` |
| Exchange API OpenAPI | `artifacts/openapi-exchange.json` |
| WebSocket AsyncAPI | `artifacts/asyncapi.json` |
| Signed exchange envelope schema | `artifacts/schemas/signed-action-envelope.schema.json` |
| Signed action payload schemas | `artifacts/schemas/signed-actions.schema.json` |

## AI Agent Entry Points

| Agent | Path |
| --- | --- |
| General | `AGENTS.md` |
| Codex | `CODEX.md` |
| Claude Code | `CLAUDE.md` |
| OpenClaw | `OPENCLAW.md` |
| LLM index | `llms.txt` |
| Full LLM context | `llms-full.txt` |
| Paste-ready first trade task | `agent-guides/first-trade.md` |

## Recommended Agent Flow

1. Read `llms.txt`.
2. Use the official Python or JavaScript SDK.
3. Run the first trade guide on testnet.
4. Query product metadata before choosing symbols, leverage, or quantities.
5. Cancel test orders and verify no unintended position remains.
