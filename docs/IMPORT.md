# Import the workflows into n8n

Two ways. Either is fine.

## A. Command line (no UI)

```bash
n8n import:workflow --input=workflows/01-email-triage.json
n8n import:workflow --input=workflows/02-lead-enrichment-dedupe.json
n8n import:workflow --input=workflows/03-refund-approval-gate.json
```

Each workflow already carries a stable `id`, so importing is idempotent by name.
If you re-import the same id, n8n reports a constraint error — that is expected;
delete the old one first or import under a new id.

## B. From the n8n UI

1. Open your n8n instance.
2. **Workflows → Import from File**, pick a `.json` in `workflows/`.
3. Open the workflow, add your credentials, and set the env vars (see `ENV.md`).

## After import

- **Workflow 01 (email triage):** activate it and POST to
  `https://<your-n8n>/webhook/email-triage` with
  `{"subject": "...", "text": "...", "from": "..."}`.
- **Workflow 02 (lead enrichment):** needs a Google Sheets credential pointing at
  the sheet in `SHEET_ID`, with a tab named `Leads` and an `email` column.
- **Workflow 03 (refund gate):** keep `AUTO_APPROVE_MAX=0` at first; every refund
  will go to Slack for a human decision.

## Validate before importing

```bash
python scripts/validate_workflows.py
```

Checks node integrity, connection targets, orphan nodes, and that every `$env.*`
used is declared. Exit code is non-zero on any problem, so it works in CI.
