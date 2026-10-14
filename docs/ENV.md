# n8n — Environment variables for this pack

Copy to `.env` (n8n reads it with `N8N_ENV_FEATURE=1` or export in your shell /
docker-compose). None are committed.

## LLM (pick one; the Groq nodes are preconfigured)

    GROQ_API_KEY=gsk_...            # used by workflows 01 and 02

## Slack (incoming webhooks — one per channel)

    SLACK_WEBHOOK_SALES=https://hooks.slack.com/services/...
    SLACK_WEBHOOK_SUPPORT=https://hooks.slack.com/services/...
    SLACK_WEBHOOK_TRIAGE=https://hooks.slack.com/services/...
    SLACK_WEBHOOK_APPROVALS=https://hooks.slack.com/services/...

## Google Sheets (workflow 02)

    SHEET_ID=1AbC...                # the spreadsheet id from its URL

## Payments (workflow 03)

    STRIPE_API_KEY=sk_...           # test key is fine
    STRIPE_API_URL=https://api.stripe.com
    AUTO_APPROVE_MAX=0              # refunds above this need human approval; 0 = always ask

## Notes

- `AUTO_APPROVE_MAX=0` is the safe default: every refund is parked for a human.
  Raise it only once you trust the flow.
- The workflows never hardcode a key; they read `$env.*`, and the validator
  (`scripts/validate_workflows.py`) fails if a used env var is not declared in the
  workflow's `meta.requires`.
