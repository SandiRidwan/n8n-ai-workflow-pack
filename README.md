<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Orbitron&weight=900&size=32&duration=3000&pause=1000&color=EA4B71&center=true&vCenter=true&width=980&height=70&lines=N8N+AI+WORKFLOW+PACK" alt="n8n AI Workflow Pack" />

![n8n](https://img.shields.io/badge/n8n-2.x-EA4B71?style=for-the-badge&logo=n8n&logoColor=white)
![Workflows](https://img.shields.io/badge/workflows-3_importable-2E7D32?style=for-the-badge)
![No code](https://img.shields.io/badge/import-ready_to_use-0F766E?style=for-the-badge)
![Tests](https://img.shields.io/badge/tests-9_passing-2E7D32?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-0D1117?style=for-the-badge)

</div>

---

## ⚡ What this is

**Three importable n8n workflows that wire an LLM into a real business process —
safely.** Not "call ChatGPT and log the answer", but the patterns that decide
whether an automation survives production:

- **validate before you spend** — a malformed payload is rejected *before* the LLM call
- **fail to a human, not to a wrong answer** — if the model returns junk, the item
  goes to a review queue, never down a confident wrong path
- **dedupe before you write** — no second CRM record, no wasted enrichment
- **fail closed on sensitive actions** — a refund above your limit is *parked for
  approval*, never auto-executed

```bash
git clone https://github.com/SandiRidwan/n8n-ai-workflow-pack
python scripts/validate_workflows.py            # checks all three, exits non-zero on any problem

n8n import:workflow --input=workflows/01-email-triage.json
n8n import:workflow --input=workflows/02-lead-enrichment-dedupe.json
n8n import:workflow --input=workflows/03-refund-approval-gate.json
```

Verified to import into **n8n 2.32**.

---

## 📦 The three workflows

| # | Workflow | What it does | The safe part |
|---|---|---|---|
| 01 | **Email triage & routing** | webhook → validate → LLM classify → route to Slack | malformed email rejected pre-LLM; an LLM failure routes to a **human queue**, not a wrong channel |
| 02 | **Lead enrichment + dedupe** | form → validate → **duplicate guard** → LLM enrich (ICP score) → sheet | dedupe runs *before* the LLM and the write; a failed enrich yields `needs_review`, not a fake score |
| 03 | **Refund approval gate** | request → validate → **policy** → Slack approve/reject → refund → audit | refunds above `AUTO_APPROVE_MAX` are **parked, never refunded**; every request writes an audit row |

Every workflow ships a **real error path**, a `meta.description` explaining the
design, a `meta.requires` list of env vars, and a validator that enforces both.

---

## 🛡️ Why these are worth importing

Most AI-automation templates on the internet skip the hard parts. This pack is
built around them:

| The failure everyone hits | How these handle it |
|---|---|
| LLM returns invalid JSON → workflow crashes or acts on garbage | every LLM node is followed by a **parse + guard** node that falls back to a human/neutral path |
| Duplicate records on retry | an explicit **duplicate guard** before any write |
| "It refunded $4,000 automatically" | an **approval gate** that fails closed; the threshold is env-configurable |
| Silent breakage | every branch is connected and the validator proves it |
| Secrets hardcoded in exports | only `$env.*`; the validator fails if a used var is undeclared |

---

## 🧪 Quality — 9 tests, and a validator you can reuse

`scripts/validate_workflows.py` checks a workflow **before** you import it:

```
OK    01-email-triage.json
OK    02-lead-enrichment-dedupe.json
OK    03-refund-approval-gate.json
3 file(s), 0 error(s)
```

It catches: missing top-level keys, duplicate node names (which silently break
connections), connections to nodes that do not exist, orphan nodes, HTTP nodes
with no URL, and **env vars used but not declared**. Exit code is non-zero on any
problem, so it drops into CI.

The 9 tests prove the validator *actually catches* each of those — a validator
that never fails is worse than none.

```
PASS  valid workflow passes
PASS  missing top-level key detected
PASS  duplicate node names detected
PASS  connection to unknown node detected
PASS  orphan node detected
PASS  HTTP node without url detected
PASS  undeclared $env var flagged
PASS  declared $env var allowed
PASS  all three real workflows are valid
```

---

## 📁 Structure

```
n8n-ai-workflow-pack/
├── workflows/
│   ├── 01-email-triage.json
│   ├── 02-lead-enrichment-dedupe.json
│   └── 03-refund-approval-gate.json
├── scripts/validate_workflows.py   # reusable pre-import validator
├── tests/test_validator.py         # 9 tests proving the validator works
├── docs/ENV.md                     # the env vars, and what is safe by default
└── docs/IMPORT.md                  # import steps (CLI + UI)
```

---

## 🚀 Quick Start

```bash
pip install -r requirements.txt        # just pytest, for the validator tests
python scripts/validate_workflows.py    # sanity-check before importing

# import (CLI)
n8n import:workflow --input=workflows/01-email-triage.json

# set env vars (see docs/ENV.md), then activate in the n8n UI
```

Minimum env to run workflow 01: `GROQ_API_KEY` + the three `SLACK_WEBHOOK_*` vars.
`AUTO_APPROVE_MAX=0` (the default) means *every* refund needs a human.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Automation** | n8n (webhook, code, HTTP, IF, Switch, Google Sheets nodes) |
| **LLM** | Groq (OpenAI-compatible) with `response_format: json_object` |
| **Safety** | pre-LLM validation, parse+guard, duplicate guard, approval gate, fail-closed |
| **Tooling** | a Python validator you can point at any n8n workflow export |

---

## ⚠️ Limitations (honest)

- **The LLM nodes target Groq** out of the box (fast + cheap). Swap the URL/model
  for OpenAI/Anthropic/Gemini — the shape is identical.
- **Slack buttons show intent, not full round-trip.** Workflow 03 posts
  approve/reject buttons and parks the request; wiring the button callback to a
  second webhook that performs the refund is the next step (documented, not faked).
- **The validator checks structure and env, not business logic.** It cannot tell
  you your ICP prompt is good — only that the workflow is wired correctly.
- **Tested against n8n 2.32.** Older majors may differ in node `typeVersion`.

---

## 👤 Author

<div align="center">

**Sandi Ridwan** — AI Automation · n8n & LLM Workflows · Python

📍 Palu, Central Sulawesi, Indonesia

[![Upwork](https://img.shields.io/badge/Upwork-Hire_Me-EA4B71?style=for-the-badge&logo=upwork&logoColor=white)](https://www.upwork.com/freelancers/~011f6d0fbb4a372974)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/sandi-ridwan)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/SandiRidwan)

</div>

## 📄 License

MIT — code and workflow JSON.
