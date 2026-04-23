---
description: Download SDK client libraries and protobuf definitions.
icon: download
---

# SDK & Protobuf

## Python SDK

{% file src="sdk/dex_client.py" %}
Self-contained Python client. No protobuf codegen needed — uses built-in encoder.
{% endfile %}

**Dependencies:**
```bash
pip install eth-account requests websockets
```

## JavaScript SDK

{% file src="sdk/dex_client.mjs" %}
ES module client for Node.js. Requires protobufjs for protobuf serialization.
{% endfile %}

**Dependencies:**
```bash
npm install ethers protobufjs ws
```

## Protobuf Definition

{% file src="sdk/dex.proto" %}
All message and enum definitions for Agent-signed actions. Use with protoc or protobufjs.
{% endfile %}

<details>
<summary>Compile protobuf (optional — Python SDK has built-in encoder)</summary>

**Python:**
```bash
pip install protobuf grpcio-tools
python -m grpc_tools.protoc --python_out=. --proto_path=. dex.proto
```

**JavaScript:**
```bash
# protobufjs loads .proto files at runtime — no compilation needed
```
</details>

## Quick Verify

Run the Python SDK directly to verify everything works:

```bash
python dex_client.py
```

This generates random wallets, claims testnet funds, approves an agent, places an order, and subscribes to WebSocket — all in one run.
