"""R Unlimited LLC marketing workflow example.

This example clones the agent pattern demos to create a bespoke collection of
agents tailored to R Unlimited LLC's marketing and communications needs. The
workflow introduces:

* ``r_unlimited_orchestrator`` – the high-level planner that triages requests
  across social, communications, analytics, and outbound channels.
* ``social_campaign_agent`` – prepares Meta Business Suite campaigns and hands
  structured HTTP plans to ``caller_agent`` for execution.
* ``email_outreach_agent`` – drafts newsletter and drip campaign content for
  community building and fundraising.
* ``affiliate_relations_agent`` – manages partner promotions, ensuring the
  correct affiliate links and talking points are surfaced.
* ``analytics_insights_agent`` – synthesises performance learnings for the
  leadership team and provides follow-up actions.
* ``caller_agent`` – the dedicated HTTP/REST integrator that turns agent
  requests into API-ready payloads while keeping credentials in environment
  variables.

The example focuses on planning and coordination. The tools defined here only
produce plans – they **do not** send any real traffic. Replace their
implementations with your own API clients when you integrate with production
services.
"""

from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel, Field

from agents import Agent, Runner, function_tool

# --- Shared business context -------------------------------------------------

MISSION_STATEMENT = (
    "At R-Unlimited LLC we empower communities through digital experiences that "
    "advance health, wellness, and motivational storytelling."
)

AFFILIATE_CHANNELS = [
    "GoDaddy Web Sales",
    "Meta Business placements",
    "WarriorPlus listings",
    "AI Partners and tooling bundles",
    "Bristol community media properties",
    "Systeme.io funnels and newsletters",
]

SIGNATURE_VOICE = (
    "You write with empathy, action-oriented phrasing, and clear calls to "
    "engage with our cancer-awareness mission."
)

META_BUSINESS_TOKEN_ENV = "META_BUSINESS_ACCESS_TOKEN"
META_BUSINESS_ACCOUNT_ENV = "META_BUSINESS_ACCOUNT_ID"


# --- Tool definitions --------------------------------------------------------


class MetaBusinessPostPlan(BaseModel):
    """Plan for calling the Meta Graph API to publish a post or ad."""

    page_id: str = Field(..., description="Target Facebook Page ID")
    endpoint: str = Field(
        ...,
        description="Relative Graph API endpoint for the publish action.",
        examples=["/feed", "/ads"],
    )
    payload: dict[str, Any] = Field(..., description="JSON body to send to the API.")
    access_token_env: str = Field(
        default=META_BUSINESS_TOKEN_ENV,
        description="Environment variable that stores the long-lived token.",
    )
    notes: str = Field(
        default="",
        description="Operational guidance for the HTTP executor.",
    )


class HeaderInput(BaseModel):
    """Structured header entry to keep the tool schema strict."""

    name: str = Field(..., description="Header name such as Authorization or X-Request-ID.")
    value: str = Field(..., description="Header value as a string.")


class JsonBodyEntry(BaseModel):
    """Key-value pair for composing JSON request bodies."""

    key: str = Field(..., description="JSON field name.")
    value: Any = Field(..., description="Value for the JSON field.")


@function_tool
def build_meta_business_post_plan(
    objective: str,
    message: str,
    cta: str,
    page_id: str | None = None,
    link: str | None = None,
    media_url: str | None = None,
) -> MetaBusinessPostPlan:
    """Return a structured plan for the Meta Business Suite Graph API."""

    resolved_page_id = page_id or os.environ.get(META_BUSINESS_ACCOUNT_ENV, "<missing-page-id>")
    payload: dict[str, Any] = {
        "message": message,
        "objective": objective,
        "call_to_action": {"type": cta},
    }
    if link:
        payload["link"] = link
    if media_url:
        payload.setdefault("attached_media", []).append({"media_fbid": media_url})

    notes = (
        "Use the caller agent to POST this payload to the Graph API. Confirm "
        "the access token stored in the environment variable before executing."
    )

    return MetaBusinessPostPlan(
        page_id=resolved_page_id,
        endpoint="/feed",
        payload=payload,
        notes=notes,
    )


class HttpRequestPlan(BaseModel):
    """Describe an outbound HTTP call that the caller agent should execute."""

    method: str = Field(..., description="HTTP verb such as GET, POST, or PATCH.")
    url: str = Field(..., description="Fully-qualified URL for the request.")
    headers: dict[str, str] = Field(default_factory=dict, description="Request headers.")
    json_body: dict[str, Any] | None = Field(
        default=None,
        description="Optional JSON body.",
    )
    sensitive_env_vars: list[str] = Field(
        default_factory=list,
        description="Environment variables that must be loaded before running the call.",
    )
    remarks: str = Field(
        default="",
        description="Implementation instructions for engineers executing the plan.",
    )


@function_tool
def draft_http_request(
    method: str,
    url: str,
    *,
    requires_auth: bool = False,
    json_body: list[JsonBodyEntry] | None = None,
    extra_headers: list[HeaderInput] | None = None,
    auth_env: str | None = None,
    description: str = "",
) -> HttpRequestPlan:
    """Create a generic HTTP request blueprint for the caller agent."""

    headers = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update({entry.name: entry.value for entry in extra_headers})

    sensitive_env_vars: list[str] = []
    if requires_auth:
        if auth_env:
            sensitive_env_vars.append(auth_env)
        else:
            sensitive_env_vars.append("API_BEARER_TOKEN")

    json_payload: dict[str, Any] | None = None
    if json_body:
        json_payload = {entry.key: entry.value for entry in json_body}

    remarks = description or "Execute via the caller agent using your preferred HTTP client."

    return HttpRequestPlan(
        method=method.upper(),
        url=url,
        headers=headers,
        json_body=json_payload,
        sensitive_env_vars=sensitive_env_vars,
        remarks=remarks,
    )


# --- Agent definitions -------------------------------------------------------

shared_partner_brief = (
    "Key partner properties include: "
    "GoDaddy Web Sales, Systeme.io funnels, Bristol community portals, "
    "WarriorPlus affiliate feeds, and AI-focused learning platforms. "
    "Whenever you reference a partner, include the call-to-action URL if known, "
    "and remind the caller agent to resolve final redirect URLs via HTTP plans."
)


def _communication_base_instructions(channel_description: str) -> str:
    return (
        f"You are the {channel_description} specialist for R Unlimited LLC. "
        f"Stay aligned with the mission statement: {MISSION_STATEMENT} "
        f"and maintain the signature voice: {SIGNATURE_VOICE} {shared_partner_brief}"
    )


social_campaign_agent = Agent(
    name="social_campaign_agent",
    instructions=(
        "You design Meta Business Suite organic posts and ads for R Unlimited LLC. "
        "Produce campaign briefs that highlight health & wellness narratives, include "
        "platform-specific hashtags, and respect community guidelines. "
        "When execution is required, call the build_meta_business_post_plan tool to "
        "produce a publish-ready payload, then hand off to the caller agent."
    ),
    tools=[build_meta_business_post_plan],
    handoffs=[],
)


email_outreach_agent = Agent(
    name="email_outreach_agent",
    instructions=(
        _communication_base_instructions("email marketing and newsletter")
        + " Draft subject lines, preview text, and modular newsletter sections. "
        "Include personalization hooks and direct readers to our GoDaddy-hosted "
        "sites for conversions."
    ),
    handoffs=[social_campaign_agent],
)


affiliate_relations_agent = Agent(
    name="affiliate_relations_agent",
    instructions=(
        _communication_base_instructions("affiliate partner enablement")
        + " Build promotional talking points for each affiliate channel, ensure "
        "the correct referral parameters are highlighted, and outline follow-up "
        "tasks for the caller agent to verify destination URLs."
    ),
    handoffs=[social_campaign_agent],
)


analytics_insights_agent = Agent(
    name="analytics_insights_agent",
    instructions=(
        _communication_base_instructions("analytics and reporting")
        + " Summarise campaign performance insights, propose experiments, and "
        "highlight any data gaps that require API pulls from Meta, Systeme.io, or "
        "Stripe dashboards. When data retrieval is necessary, request the caller "
        "agent to draft HTTP calls using the draft_http_request tool."
    ),
    handoffs=[],
)


caller_agent = Agent(
    name="caller_agent",
    instructions=(
        "You translate campaign plans into executable HTTP requests. Verify that "
        "all sensitive credentials are sourced from environment variables (never "
        "hard-coded). Generate step-by-step execution notes and list the exact "
        "commands for engineers to run with curl or Postman collections."
    ),
    tools=[draft_http_request],
)


r_unlimited_orchestrator = Agent(
    name="r_unlimited_orchestrator",
    instructions=(
        "You are the lead marketing operations agent for R Unlimited LLC. "
        "Triage incoming requests, develop an execution roadmap, and delegate to "
        "specialists as needed. Always ensure messaging reflects our mission "
        "statement and includes clear calls to action. Coordinate with the "
        "social_campaign_agent for Meta Business work, the email_outreach_agent "
        "for newsletters, the affiliate_relations_agent for partner updates, the "
        "analytics_insights_agent for reporting, and the caller_agent for HTTP "
        "integrations. Provide the user with a concise summary of outcomes and "
        "next steps."
    ),
    handoffs=[
        social_campaign_agent,
        email_outreach_agent,
        affiliate_relations_agent,
        analytics_insights_agent,
        caller_agent,
    ],
)


# --- Example entry point -----------------------------------------------------


def _build_sample_prompt() -> str:
    partner_list = "\n - ".join(AFFILIATE_CHANNELS)
    return (
        "Plan a weekend social push promoting our cancer awareness webinar. "
        "Use the following partner outlets and highlight the wellness toolkit "
        "giveaway:\n - "
        + partner_list
        + ". Provide at least one Meta Business campaign plan and any supporting "
        "communications we should schedule."
    )


async def main() -> None:
    """Run a single-orchestrator example for manual testing."""

    user_prompt = _build_sample_prompt()
    print("[input]", user_prompt)
    result = await Runner.run(r_unlimited_orchestrator, user_prompt)
    print("\n[output]\n")
    print(result.final_output)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
