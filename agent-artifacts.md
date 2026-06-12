---
description: Machine-readable files and AI-agent entry points for AFX DEX.
icon: robot
---

# Agent Artifacts

AFX DEX publishes machine-readable artifacts for coding agents, SDK generators, API clients, and AI-agent trading workflows.

## API Artifacts

| Artifact | Repo path | Public raw URL |
| --- | --- | --- |
| Combined REST OpenAPI | `artifacts/openapi.json` | `https://raw.githubusercontent.com/afx-dex/afx-docs/main/artifacts/openapi.json` |
| Info API OpenAPI | `artifacts/openapi-info.json` | `https://raw.githubusercontent.com/afx-dex/afx-docs/main/artifacts/openapi-info.json` |
| Exchange API OpenAPI | `artifacts/openapi-exchange.json` | `https://raw.githubusercontent.com/afx-dex/afx-docs/main/artifacts/openapi-exchange.json` |
| WebSocket AsyncAPI | `artifacts/asyncapi.json` | `https://raw.githubusercontent.com/afx-dex/afx-docs/main/artifacts/asyncapi.json` |
| Signed exchange envelope schema | `artifacts/schemas/signed-action-envelope.schema.json` | `https://raw.githubusercontent.com/afx-dex/afx-docs/main/artifacts/schemas/signed-action-envelope.schema.json` |
| Signed action payload schemas | `artifacts/schemas/signed-actions.schema.json` | `https://raw.githubusercontent.com/afx-dex/afx-docs/main/artifacts/schemas/signed-actions.schema.json` |

## AI Agent Entry Points

| Agent | Repo path | Public raw URL |
| --- | --- | --- |
| General | `AGENTS.md` | `https://raw.githubusercontent.com/afx-dex/afx-docs/main/AGENTS.md` |
| Codex | `CODEX.md` | `https://raw.githubusercontent.com/afx-dex/afx-docs/main/CODEX.md` |
| Claude Code | `CLAUDE.md` | `https://raw.githubusercontent.com/afx-dex/afx-docs/main/CLAUDE.md` |
| OpenClaw | `OPENCLAW.md` | `https://raw.githubusercontent.com/afx-dex/afx-docs/main/OPENCLAW.md` |
| LLM index | `llms.txt` | `https://raw.githubusercontent.com/afx-dex/afx-docs/main/llms.txt` |
| Full LLM context | `llms-full.txt` | `https://raw.githubusercontent.com/afx-dex/afx-docs/main/llms-full.txt` |
| Paste-ready first trade task | `agent-guides/first-trade.md` | `https://raw.githubusercontent.com/afx-dex/afx-docs/main/agent-guides/first-trade.md` |
| Agent safety guide | `agent-safety.md` | `https://raw.githubusercontent.com/afx-dex/afx-docs/main/agent-safety.md` |

## Recommended Agent Flow

1. Read `llms.txt`.
2. Use the official Python or JavaScript SDK.
3. Run the first trade guide on testnet.
4. Query product metadata before choosing symbols, leverage, or quantities.
5. Keep the Master private key out of trading runtimes.
6. Cancel test orders and verify no unintended position remains.
7. Revoke or rotate temporary Agent keys.
