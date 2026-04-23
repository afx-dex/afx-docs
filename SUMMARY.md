# Table of contents

* [afx-docs](api-overview.md)
* [afx-api](afx-api/README.md)
  * [Table of contents](afx-api/SUMMARY.md)
  * [API](afx-api/api-overview.md)
  * [Quick Start](afx-api/quickstart.md)
  * [Exchange API](afx-api/exchange/README.md)
    * ```yaml
      type: builtin:openapi
      props:
        models: true
        downloadLink: false
      dependencies:
        spec:
          ref:
            kind: openapi
            spec: exchange
      ```
  * [Info API](afx-api/info/README.md)
    * ```yaml
      type: builtin:openapi
      props:
        models: true
        downloadLink: false
      dependencies:
        spec:
          ref:
            kind: openapi
            spec: info
      ```
  * [WebSocket](afx-api/websocket/README.md)
    * ```yaml
      type: builtin:openapi
      props:
        models: true
        downloadLink: false
      dependencies:
        spec:
          ref:
            kind: openapi
            spec: websocket
      ```
  * [SDK & Protobuf](afx-api/sdk.md)
  * [Signing](afx-api/signing.md)
