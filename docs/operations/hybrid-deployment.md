# HYBRID_OPT_IN and MANAGED_TEAM deployment

`HYBRID_OPT_IN` keeps authoritative data local while permitting explicit per-job cloud uploads after classification, policy decision, redaction, approval, encryption when required, and audit. `MANAGED_TEAM` adds organization authentication, role-based access, collaboration metadata, encrypted artifact sync, and cloud job queues while preserving local hardware authority.

Configure only HTTPS provider endpoints on the allowlist. Do not upload plaintext keys or unencrypted private evidence. Verify downloaded releases, rulesets, model manifests, benchmark packs, and migrations locally before activation.
