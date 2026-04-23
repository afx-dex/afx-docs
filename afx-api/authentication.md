---
description: EIP-712 structured signing for Agent and Master wallet operations.
icon: key
---

# Authentication

{% hint style="info" %}
Upload `openapi/signing.yaml` to GitBook as an OpenAPI spec, then reference it below.
{% endhint %}

{% openapi src="openapi/signing.yaml" path="/signing/agent" method="post" %}
{% endopenapi %}

{% openapi src="openapi/signing.yaml" path="/signing/master" method="post" %}
{% endopenapi %}
