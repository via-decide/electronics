# Local-first cloud boundary

Default deployment is `LOCAL_ONLY`: no cloud jobs, telemetry, synchronization, or provider calls. Optional cloud services sit behind a policy/classification gate, local redaction, client-side authenticated encryption, schema-validated result handling, deterministic validation, and human review.

Profiles: `LOCAL_ONLY`, `HYBRID_OPT_IN`, and `MANAGED_TEAM`. Hardware authority, private evidence, authoritative audit, firmware keys, firmware binaries, diagnostics, measurements, validators, and confirmations remain local in every profile.

Cloud services are limited to public-source retrieval, optional OCR/parsing, optional candidate AI review, encrypted sync/backup, collaboration metadata, and signed software/ruleset/model distribution. Cloud results are candidate-only and cannot set confirmed component, official fact, electrical approval, repair verified, bench verified, or firmware authorization states.

Hardware separation invariant: `CloudService ∩ HardwareCapabilities = ∅` for GPIO, JTAG, SWD, programmer, relays, scopes, logic analyzers, serial write, storage program/erase, and firmware flash.
