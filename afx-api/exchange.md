---
description: Trading operations — place/cancel orders, set leverage, manage vaults.
icon: arrow-right-arrow-left
---

# Exchange API

All trading operations go through a single endpoint:

```
POST /api/v1/exchange
```

The `action.type` field determines which operation to execute. Every request requires an EIP-712 signature. See [Authentication](signing.md) for signing details.

{% hint style="info" %}
The OpenAPI spec for this endpoint is available at `openapi/exchange.yaml`. Upload it to GitBook to render the interactive API reference on this page.
{% endhint %}
