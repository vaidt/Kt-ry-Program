# Delegation records

Store one completed JSON record per delegated task here, named `ASIG-DEL-NNNN.json`.

Start from `docs/templates/project-delegation.template.json` and validate it against `schemas/project-delegation.schema.json`. Replace all placeholders. The template is deliberately marked `BLOCKED` with `implementation_authorized: false`; copying it does not grant execution authority.

Only records in this directory are evaluated by the integration workflow. The absence of records yields `NO_RECORDS`, not an approval. Never put credentials, tokens, private keys, or secret-bearing raw logs in a record.
