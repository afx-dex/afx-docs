---
description: Download SDK client libraries and protobuf definitions.
icon: download
---

# SDK & Protobuf

## Protobuf Definition

{% file src="sdk/dex.proto" %}
All message and enum definitions for Agent-signed actions.
{% endfile %}

{% hint style="warning" %}
The Python SDK depends on the compiled protobuf module `dex_pb2.py`. You must compile it before using the SDK.
{% endhint %}

### Compile

{% tabs %}
{% tab title="Python" %}
```bash
# Install protobuf compiler and Python package
pip install protobuf grpcio-tools

# Compile dex.proto → dex_pb2.py (place in same directory as dex_client.py)
python -m grpc_tools.protoc --python_out=. --proto_path=. dex.proto
```
{% endtab %}

{% tab title="JavaScript" %}
```bash
# protobufjs loads .proto files at runtime — no compilation needed
# Just keep dex.proto in the same directory as dex_client.mjs
```
{% endtab %}
{% endtabs %}

---

## Python SDK

{% file src="sdk/dex_client.py" %}
Python client with EIP-712 signing, protobuf serialization, and HTTP/WebSocket support.
{% endfile %}

**Dependencies:**
```bash
pip install eth-account requests websockets protobuf
```

**File structure:**
```
your-project/
├── dex.proto          # download from above
├── dex_pb2.py         # compiled from dex.proto
└── dex_client.py      # download from above
```

---

## JavaScript SDK

{% file src="sdk/dex_client.mjs" %}
ES module client for Node.js. Uses protobufjs + ethers.js.
{% endfile %}

**Dependencies:**
```bash
npm install ethers protobufjs ws
```

**File structure:**
```
your-project/
├── dex.proto          # download from above
└── dex_client.mjs     # download from above
```

---

## Quick Verify

{% stepper %}
{% step %}
### Setup

```bash
# Download all files into one directory, then:
pip install eth-account requests websockets protobuf
python -m grpc_tools.protoc --python_out=. --proto_path=. dex.proto
```
{% endstep %}

{% step %}
### Run

```bash
python dex_client.py
```

This generates random wallets, claims testnet funds, approves an agent, places an order, and subscribes to WebSocket — all in one run.
{% endstep %}

{% step %}
### Expected output

```
Master: 0x...
Agent:  0x...

1. faucetClaim: {"code": 0, "message": "success", ...}
2. approveAgent: {"code": 0, "message": "success", ...}
3. placeOrder: {"code": 0, "message": "success", ...}

4. WebSocket orderBook:
   received: {"channel": "orderBook", ...}

All tests done.
```
{% endstep %}
{% endstepper %}
