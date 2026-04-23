# Table of contents

* [FOR DEVELOPERS](api-overview.md)
  * [API](afx-api/api-overview/README.md)
    * [Quick Start](afx-api/api-overview/quickstart.md)
    * [Exchange API](afx-api/api-overview/exchange/README.md)
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
    * [Info API](afx-api/api-overview/info/README.md)
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
    * [WebSocket](afx-api/api-overview/websocket/README.md)
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
    * [Signing](afx-api/api-overview/signing.md)
    * [SDK & Protobuf](afx-api/api-overview/sdk.md)
