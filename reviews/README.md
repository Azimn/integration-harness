# Review Artifacts

Substantive experiments place machine-readable adversarial review records in this directory as JSON files.

A review artifact must use schema version 1 and contain `experiment_id`, `implementation_revision`, `reviewer_role`, `verdict`, and an `objections` array. Each objection contains an identifier, severity, status, claim, evidence, and disposition.

Supported verdicts are `pass`, `revise`, and `fail`. Supported severities are `low`, `medium`, and `high`. Supported objection states are `open`, `resolved`, and `rejected`.

A review cannot pass while a high-severity objection remains open. CI enforces this rule through `integration_harness.validation`.
