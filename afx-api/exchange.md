---
description: Trading operations — place/cancel orders, set leverage, manage vaults.
icon: arrow-right-arrow-left
---

# Exchange API

All trading operations go through a single endpoint:

```
POST /api/v1/exchange
```

The `action.type` field determines which operation to execute. Every request requires an EIP-712 signature.

{% hint style="info" %}
Upload `openapi/exchange.yaml` to GitBook as an OpenAPI spec to render the interactive API reference below.
{% endhint %}

<!-- After uploading exchange.yaml, replace these with actual openapi blocks:

{% openapi src="openapi/exchange.yaml" path="/exchange/placeOrder" method="post" %}
{% endopenapi %}

{% openapi src="openapi/exchange.yaml" path="/exchange/cancelOrder" method="post" %}
{% endopenapi %}

...etc for each endpoint
-->
