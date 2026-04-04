"""ClickBank Marketer Agent

Lightweight, extensible agent scaffold to discover ClickBank products,
generate hoplinks, create SEO content via OpenAI, and send email campaigns
via an ESP API (stubs provided). Designed as the new main python agent for
affiliate marketing workflows. Keep credentials and API keys in environment
variables or the repo's config.

Usage (CLI):
  python clickbank_marketer_agent.py discover "weight loss" --max 20
  python clickbank_marketer_agent.py create-content --product-id 123
  python clickbank_marketer_agent.py gen-hoplink --vendor vendorname
  python clickbank_marketer_agent.py send-email --subject "New review" --body-file post.html
"""
from __future__ import annotations

import os
import json
import argparse
import logging
import time
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup

try:
    import openai
except Exception:
    openai = None

LOG = logging.getLogger("clickbank_marketer")
logging.basicConfig(level=logging.INFO)


class ClickBankMarketer:
    """Agent that encapsulates discovery, hoplink management, content creation,
    email automation and basic analytics hooks for ClickBank affiliate work.

    Environment variables used (examples):
    - CLICKBANK_AFFILIATE_URL : template like "http://AFFILIATE.{vendor}.hop.clickbank.net"
    - OPENAI_API_KEY : OpenAI API key (optional but recommended for content)
    - GODADDY_EMAIL_API_KEY : (optional) GoDaddy Email Marketing API key
    - CLICKBANK_QUICKSTATS_API : (optional) ClickBank Quickstats endpoint or token
    """

    def __init__(self, affiliate_template: Optional[str] = None):
        self.affiliate_template = (
            affiliate_template or os.environ.get("CLICKBANK_AFFILIATE_URL")
        )
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        if openai and self.openai_key:
            openai.api_key = self.openai_key

    # --------------------- Product discovery ---------------------
    def discover_products(self, query: str, max_results: int = 20) -> List[Dict]:
        """Scrape ClickBank marketplace search results for a query.

        This is a best-effort scraper; if an official API is available, prefer it.
        Returns a list of product dicts with minimal fields.
        """
        LOG.info("Discovering products for query=%s", query)
        url = f"https://www.clickbank.com/marketplace"
        params = {"search": query}
        try:
            r = requests.get(url, params=params, timeout=15)
            r.raise_for_status()
        except Exception as e:
            LOG.error("Marketplace request failed: %s", e)
            return []

        soup = BeautifulSoup(r.text, "html.parser")
        results: List[Dict] = []

        # Basic scraping heuristics: find product list containers
        for item in soup.select(".productCard")[:max_results]:
            title_el = item.select_one(".productCard-title")
            vendor_el = item.select_one(".productCard-vendor")
            desc_el = item.select_one(".productCard-description")

            product = {
                "name": title_el.get_text(strip=True) if title_el else "",
                "vendor": vendor_el.get_text(strip=True) if vendor_el else "",
                "description": desc_el.get_text(strip=True) if desc_el else "",
            }
            results.append(product)

        LOG.info("Found %d product summaries", len(results))
        return results

    # --------------------- Hoplink generation ---------------------
    def generate_hoplink(self, vendor_alias: str, tid: Optional[str] = None) -> str:
        """Generate a hoplink from the affiliate template.

        The template should contain a `{vendor}` token or be a format string.
        If only the raw base is available, this method will attempt a safe replace.
        """
        if not self.affiliate_template:
            raise RuntimeError("CLICKBANK_AFFILIATE_URL not configured")

        if "{vendor}" in self.affiliate_template:
            hop = self.affiliate_template.format(vendor=vendor_alias)
        else:
            hop = self.affiliate_template.replace("VENDOR", vendor_alias)

        if tid:
            sep = "?" if "?" not in hop else "&"
            hop = f"{hop}{sep}tid={tid}"

        return hop

    # --------------------- Content creation ---------------------
    def create_seo_content(
        self, product: Dict, keywords: List[str], length: int = 800
    ) -> str:
        """Create SEO-optimized article draft using OpenAI.

        Falls back to a simple template if OpenAI key or package is not present.
        """
        prompt = (
            f"Write an SEO-optimized {length}-word blog post about {product.get('name')}\n"
            f"Include headings, short paragraphs, and a call-to-action with the affiliate link.\n"
            f"Target keywords: {', '.join(keywords)}.\n"
            f"Product description: {product.get('description', '')}\n"
        )

        if openai and self.openai_key:
            try:
                # Use ChatCompletion when available; fall back to Completion API
                if hasattr(openai, "ChatCompletion"):
                    resp = openai.ChatCompletion.create(
                        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=min(4096, length * 5),
                    )
                    content = resp["choices"][0]["message"]["content"]
                else:
                    resp = openai.Completion.create(
                        model=os.environ.get("OPENAI_MODEL", "text-davinci-003"),
                        prompt=prompt,
                        max_tokens=min(4096, length * 5),
                    )
                    content = resp["choices"][0]["text"]
                return content
            except Exception as e:
                LOG.warning("OpenAI call failed, falling back: %s", e)

        # Fallback template
        title = f"{product.get('name')} Review"
        body = f"{title}\n\n"
        body += f"{product.get('description', '')}\n\n"
        body += "Why this product may help you:\n- Benefit 1\n- Benefit 2\n\n"
        body += "Call to action: Try it now via my link."
        return body

    # --------------------- Email campaign (ESP integration) ---------------------
    def send_email_campaign(
        self, subject: str, html_body: str, list_id: Optional[str] = None
    ) -> Dict:
        """Send an email campaign via GoDaddy Email Marketing API (example).

        This implementation is a minimal POST wrapper. Adjust according to the
        ESP's actual API specification. Keep API keys in env `GODADDY_EMAIL_API_KEY`.
        """
        # Prefer GoDaddy if configured, otherwise fallback to SendGrid if available.
        api_key = os.environ.get("GODADDY_EMAIL_API_KEY")
        if api_key:
            endpoint = os.environ.get(
                "GODADDY_EMAIL_API_URL",
                "https://api.godaddy.com/v1/email/campaigns",
            )
            payload = {
                "subject": subject,
                "html": html_body,
                "list_id": list_id,
            }
            headers = {"Authorization": f"sso-key {api_key}", "Content-Type": "application/json"}
            try:
                r = requests.post(endpoint, json=payload, headers=headers, timeout=20)
                r.raise_for_status()
                return r.json()
            except Exception as e:
                LOG.error("GoDaddy email send failed: %s", e)

        sendgrid_key = os.environ.get("SENDGRID_API_KEY")
        from_email = os.environ.get("EMAIL_FROM") or os.environ.get("SENDGRID_FROM")
        if sendgrid_key and from_email:
            sg_endpoint = "https://api.sendgrid.com/v3/mail/send"
            payload = {
                "personalizations": [{"to": [{"email": list_id or from_email}], "subject": subject}],
                "from": {"email": from_email},
                "content": [{"type": "text/html", "value": html_body}],
            }
            headers = {"Authorization": f"Bearer {sendgrid_key}", "Content-Type": "application/json"}
            try:
                r = requests.post(sg_endpoint, json=payload, headers=headers, timeout=20)
                r.raise_for_status()
                return {"status": "sent", "provider": "sendgrid", "code": r.status_code}
            except Exception as e:
                LOG.error("SendGrid send failed: %s", e)

        LOG.warning("No ESP API key configured (GoDaddy or SendGrid) — skipping send")
        return {"status": "skipped", "reason": "no_esp_key"}

    # --------------------- Analytics & tracking ---------------------
    def fetch_clickbank_quickstats(self, start_date: str, end_date: str) -> Dict:
        """Fetch ClickBank Quickstats using configured credentials.

        Supports multiple auth modes controlled via environment variables:
        - CLICKBANK_QUICKSTATS_AUTH_TYPE: 'token' | 'basic' | 'none' (default 'none')
        - CLICKBANK_QUICKSTATS_URL: custom endpoint if needed
        - CLICKBANK_QUICKSTATS_TOKEN: Bearer token when auth_type='token'
        - CLICKBANK_QUICKSTATS_BASIC: username:password when auth_type='basic'

        Returns parsed JSON from the Quickstats endpoint or an empty dict on failure.
        """
        auth_type = os.environ.get("CLICKBANK_QUICKSTATS_AUTH_TYPE", "none").lower()
        endpoint = os.environ.get("CLICKBANK_QUICKSTATS_URL", "https://api.clickbank.com/quickstats")
        params = {"start": start_date, "end": end_date}

        headers = {"Accept": "application/json"}

        # Prepare auth
        auth = None
        if auth_type == "token":
            token = os.environ.get("CLICKBANK_QUICKSTATS_TOKEN")
            if not token:
                LOG.warning("CLICKBANK_QUICKSTATS_AUTH_TYPE=token but no token provided")
                return {}
            headers["Authorization"] = f"Bearer {token}"
        elif auth_type == "basic":
            basic = os.environ.get("CLICKBANK_QUICKSTATS_BASIC")
            if not basic or ":" not in basic:
                LOG.warning("CLICKBANK_QUICKSTATS_AUTH_TYPE=basic but no basic credentials provided")
                return {}
            user, pwd = basic.split(":", 1)
            auth = (user, pwd)
        elif auth_type == "none":
            LOG.info("No ClickBank Quickstats auth configured; attempting unauthenticated request")
        else:
            LOG.warning("Unknown CLICKBANK_QUICKSTATS_AUTH_TYPE=%s", auth_type)
            return {}

        # Simple retry/backoff
        attempts = 3
        backoff = 1.0
        for attempt in range(1, attempts + 1):
            try:
                resp = requests.get(endpoint, params=params, headers=headers, auth=auth, timeout=25)
                resp.raise_for_status()
                # Try to decode JSON; if response is CSV or text, return raw text under 'raw'
                try:
                    return resp.json()
                except ValueError:
                    LOG.info("Quickstats returned non-JSON payload; returning raw text")
                    return {"raw": resp.text}
            except requests.HTTPError as e:
                LOG.error("Quickstats HTTP error (attempt %d/%d): %s", attempt, attempts, e)
            except Exception as e:
                LOG.error("Quickstats request failed (attempt %d/%d): %s", attempt, attempts, e)

            time.sleep(backoff)
            backoff *= 2

        LOG.error("Quickstats fetch failed after %d attempts", attempts)
        return {}


def _build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ClickBankMarketer")
    sub = parser.add_subparsers(dest="cmd")

    d = sub.add_parser("discover")
    d.add_argument("query")
    d.add_argument("--max", type=int, default=10)

    g = sub.add_parser("gen-hoplink")
    g.add_argument("vendor")
    g.add_argument("--tid", default=None)

    c = sub.add_parser("create-content")
    c.add_argument("--product-json", help="path to product JSON file (or - for stdin)")
    c.add_argument("--keywords", help="comma-separated keywords", default="affiliate,review")
    c.add_argument("--length", type=int, default=800)

    e = sub.add_parser("send-email")
    e.add_argument("--subject")
    e.add_argument("--body-file")
    e.add_argument("--list-id", default=None)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_cli()
    args = parser.parse_args(argv)
    agent = ClickBankMarketer()

    if args.cmd == "discover":
        prods = agent.discover_products(args.query, max_results=args.max)
        print(json.dumps(prods, indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "gen-hoplink":
        hop = agent.generate_hoplink(args.vendor, tid=args.tid)
        print(hop)
        return 0

    if args.cmd == "create-content":
        if not args.product_json:
            LOG.error("--product-json is required")
            return 2
        raw = None
        if args.product_json == "-":
            import sys

            raw = json.load(sys.stdin)
        else:
            with open(args.product_json, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
        keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
        out = agent.create_seo_content(raw, keywords, length=args.length)
        print(out)
        return 0

    if args.cmd == "send-email":
        if not args.body_file or not args.subject:
            LOG.error("--subject and --body-file are required")
            return 2
        with open(args.body_file, "r", encoding="utf-8") as fh:
            html = fh.read()
        res = agent.send_email_campaign(args.subject, html, list_id=args.list_id)
        print(json.dumps(res, indent=2))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main())
