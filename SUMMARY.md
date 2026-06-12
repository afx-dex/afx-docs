# Table of contents

* [API Reference](index.md)
* [Quick Start](quickstart.md)
* [Exchange API](exchange/README.md)
  * ```yaml
    props:
      models: true
      downloadLink: false
    type: builtin:openapi
    dependencies:
      spec:
        ref:
          kind: openapi
          spec: exchange
    ```
* [Info API](info/README.md)
  * ```yaml
    props:
      models: true
      downloadLink: false
    type: builtin:openapi
    dependencies:
      spec:
        ref:
          kind: openapi
          spec: info
    ```
* [WebSocket](websocket/README.md)
  * ```yaml
    props:
      models: true
      downloadLink: false
    type: builtin:openapi
    dependencies:
      spec:
        ref:
          kind: openapi
          spec: websocket
    ```
* [Signing](signing.md)
* [Python SDK](sdk.md)
* [Agent Artifacts](agent-artifacts.md)
