# Data classification

Classes are `PUBLIC_SOURCE`, `PUBLIC_DERIVED`, `INTERNAL`, `CONFIDENTIAL`, `SECRET`, `HARDWARE_CONTROL`, `AUTHORITATIVE_EVIDENCE`, and `RECONSTRUCTIBLE`.

Every cloud-bound object carries object ID, project ID, board revision, classification, owner, tenant, source, content hash, redaction state, encryption state, retention policy, cloud permission, and approval record.

Policy summary: public classes are allowed; reconstructible data is allowed only when policy permits; internal data requires redaction or approval; confidential data requires local redaction, client-side encryption, and explicit approval; secret and hardware-control data are denied before serialization; authoritative evidence may sync only as encrypted evidence and may not mutate authority in cloud.
