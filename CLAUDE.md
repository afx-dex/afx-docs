# Claude Code Instructions For AFX DEX

Use this repository as the source of truth for AFX DEX integration work.

- Read `llms.txt` first.
- Use `afx-api/agent-guides/first-trade.md` as the first runnable task.
- Prefer the Python or JavaScript SDK over raw protobuf and EIP-712 implementation.
- Do not expose private keys in logs, commits, screenshots, or issue comments.
- Use testnet unless the user explicitly asks for mainnet.
- Clean up orders after integration tests.

