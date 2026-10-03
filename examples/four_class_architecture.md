# Four-Class Validation Architecture

This synthetic scenario is intentionally constructed to exercise all four ArchGuardAI decision classes.

## Identity and access

The public API uses OIDC for authenticated user identities.

Authorization disabled is explicitly documented for the internal administration endpoint. This is an intentional contradiction in the benchmark and should be treated as non-compliant.

## Data protection

All traffic crossing the external trust boundary uses TLS 1.3.

Encryption at rest disabled is explicitly documented for the persistent benchmark database. This is an intentional contradiction in the benchmark and should be treated as non-compliant.

## Secrets

The document does not state how application credentials or cryptographic secrets are stored, rotated, or retrieved. No positive evidence and no explicit contradiction is provided for secret management.

## Observability scope

No security-relevant events are in scope for this component. The audit-logging requirement is therefore explicitly outside the declared scope for this synthetic benchmark component.

## Resilience

The architecture description contains no design evidence for the resilience requirement and no explicit conflicting statement. This section is intentionally incomplete so that a reviewer should record a documentary gap rather than compliance or non-compliance.

## Privacy scope

The system processes no personal or sensitive data. The privacy minimization and retention requirement is therefore explicitly outside the declared scope for this synthetic benchmark.
