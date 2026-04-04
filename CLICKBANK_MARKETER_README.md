# ClickBank Marketer Agent

This repository file provides a lightweight agent for ClickBank affiliate marketing workflows.

Quickstart

- Install dependencies:

```bash
pip install -r requirements.txt
```

- Required environment variables (examples):
  - `CLICKBANK_AFFILIATE_URL` – template like `http://AFFILIATE.{vendor}.hop.clickbank.net`
  - `OPENAI_API_KEY` – for content generation (optional)
  - `GODADDY_EMAIL_API_KEY` – for GoDaddy Email Marketing integration (optional)

Additional ClickBank Quickstats integration vars:

- `CLICKBANK_QUICKSTATS_AUTH_TYPE` – one of `token`, `basic`, or `none` (default `none`).
- `CLICKBANK_QUICKSTATS_URL` – optional custom Quickstats endpoint (default `https://api.clickbank.com/quickstats`).
- `CLICKBANK_QUICKSTATS_TOKEN` – Bearer token when `auth_type=token`.
- `CLICKBANK_QUICKSTATS_BASIC` – Basic auth credentials in the form `username:password` when `auth_type=basic`.

Examples:

```bash
export CLICKBANK_QUICKSTATS_AUTH_TYPE=token
export CLICKBANK_QUICKSTATS_TOKEN="your_real_token_here"
python clickbank_marketer_agent.py # then call fetch_clickbank_quickstats
```

- Example CLI commands:

```bash
python clickbank_marketer_agent.py discover "weight loss" --max 10
python clickbank_marketer_agent.py gen-hoplink vendorname --tid campaign1
python clickbank_marketer_agent.py create-content --product-json product.json --keywords "weight loss, supplement"
python clickbank_marketer_agent.py send-email --subject "New review" --body-file post.html --list-id mylist
```

Notes

- The agent includes scraping heuristics for the ClickBank marketplace; prefer an official API if available.
- OpenAI usage requires `OPENAI_API_KEY`; content generation falls back to a template if unavailable.
- Email sending is a minimal wrapper around an ESP API (example uses GoDaddy headers); adapt to your provider.
- Keep sensitive keys out of source control and use the repo's existing config patterns.

This file is a companion to `clickbank_marketer_agent.py` implemented in the repository root.
