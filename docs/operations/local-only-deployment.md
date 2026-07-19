# LOCAL_ONLY deployment

`LOCAL_ONLY` is the default profile. It uses local database, local artifact store, local inference, local reports, and local backups. Cloud providers are disabled; optional cloud controls should be disabled in UI rather than blocking local engineering workflows.

Run `make local-only-test` to prove the cloud provider is disabled and cloud jobs cannot be queued.
