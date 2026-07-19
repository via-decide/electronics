# Cloud boundary threat model

Primary risks are bulk private-project upload, prompt injection causing lab actions, provider compromise, plaintext exposure despite TLS, unexpected redirects to internal networks, cloud output treated as authoritative engineering fact, and object-ID-only authorization bypass.

Mitigations include default local-only mode, provider adapters, endpoint allowlists, private/loopback/link-local/metadata blocking, deterministic local redaction, client-side authenticated encryption with associated-data binding, append-only audit, object-level authorization, candidate-only result gates, and absence of hardware capabilities in cloud services.
