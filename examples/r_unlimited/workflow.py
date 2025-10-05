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

import asyncio
import os
from typing import Any

import httpx
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


GRAPH_API_BASE_URL = "https://graph.facebook.com/v19.0"


class MetaBusinessPostResult(BaseModel):
    """Response payload returned after calling the Meta Graph API."""

    page_id: str = Field(..., description="Target Facebook Page ID")
    endpoint: str = Field(..., description="Graph API endpoint used for publishing.")
    status_code: int = Field(..., description="HTTP status code returned by Meta.")
    response_body: dict[str, Any] = Field(
        default_factory=dict,
        description="Decoded JSON body from the Graph API response.",
    )
    notes: str = Field(
        default="",
        description="Operational details for auditing and follow-up actions.",
    )


class HeaderInput(BaseModel):
    """Structured header entry to keep the tool schema strict."""

    name: str = Field(..., description="Header name such as Authorization or X-Request-ID.")
    value: str = Field(..., description="Header value as a string.")


class JsonBodyEntry(BaseModel):
    """Key-value pair for composing JSON request bodies."""

    key: str = Field(..., description="JSON field name.")
    value: Any = Field(..., description="Value for the JSON field.")


async def _post_to_meta(
    endpoint: str,
    payload: dict[str, Any],
    *,
    page_id: str,
    access_token: str,
    timeout: float = 15.0,
) -> httpx.Response:
    """Send a POST request to the Meta Graph API and return the raw response."""

    url = f"{GRAPH_API_BASE_URL}/{page_id}{endpoint}"
    params = {"access_token": access_token}
    async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as client:
        response = await client.post(url, params=params, json=payload)
        return response


@function_tool
async def publish_meta_business_post(
    objective: str,
    message: str,
    cta: str,
    page_id: str | None = None,
    link: str | None = None,
    media_url: str | None = None,
) -> MetaBusinessPostResult:
    """Publish a post via the Meta Business Suite Graph API."""

    resolved_page_id = page_id or os.environ.get(META_BUSINESS_ACCOUNT_ENV)
    if not resolved_page_id:
        raise ValueError(
            "Meta Business Page ID is required. Provide page_id or set "
            f"{META_BUSINESS_ACCOUNT_ENV}."
        )

    access_token = os.environ.get(META_BUSINESS_TOKEN_ENV)
    if not access_token:
        raise ValueError(
            "Meta Business access token not found in the environment. Set "
            f"{META_BUSINESS_TOKEN_ENV} before publishing."
        )

    payload: dict[str, Any] = {
        "message": message,
        "objective": objective,
        "call_to_action": {"type": cta},
    }
    if link:
        payload["link"] = link
    if media_url:
        payload.setdefault("attached_media", []).append({"media_fbid": media_url})

    response = await _post_to_meta(
        endpoint="/feed",
        payload=payload,
        page_id=resolved_page_id,
        access_token=access_token,
    )

    notes = "Meta Graph API invoked via publish_meta_business_post."

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            "Meta Graph API call failed",
        ) from exc

    body: dict[str, Any]
    try:
        body = response.json()
    except ValueError:
        body = {"raw": response.text}

    return MetaBusinessPostResult(
        page_id=resolved_page_id,
        endpoint="/feed",
        status_code=response.status_code,
        response_body=body,
        notes=notes,
    )


class HttpRequestResult(BaseModel):
    """Structured response returned by the caller agent HTTP executor."""

    method: str = Field(..., description="HTTP verb executed.")
    url: str = Field(..., description="URL requested.")
    status_code: int = Field(..., description="HTTP status code returned.")
    response_headers: dict[str, str] = Field(
        default_factory=dict,
        description="Response headers with sensitive values removed.",
    )
    response_body: dict[str, Any] | None = Field(
        default=None,
        description="Decoded JSON body when available.",
    )
    text_preview: str = Field(
        default="",
        description="Truncated text body when JSON decoding fails.",
    )
    attempts: int = Field(
        default=1,
        description="Number of attempts made (includes retries).",
    )
    notes: str = Field(
        default="",
        description="Operational notes and follow-up guidance.",
    )


@function_tool
async def execute_http_request(
    method: str,
    url: str,
    *,
    requires_auth: bool = False,
    json_body: list[JsonBodyEntry] | None = None,
    extra_headers: list[HeaderInput] | None = None,
    auth_env: str | None = None,
    description: str = "",
    retry_attempts: int = 3,
    timeout_seconds: float = 20.0,
) -> HttpRequestResult:
    """Execute an outbound HTTP call with simple retry and secret resolution."""

    headers = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update({entry.name: entry.value for entry in extra_headers})

    bearer_env = None
    if requires_auth:
        bearer_env = auth_env or "API_BEARER_TOKEN"
        bearer_token = os.environ.get(bearer_env)
        if not bearer_token:
            raise ValueError(
                "Requested authenticated call but no credential found in the environment for "
                f"{bearer_env}."
            )
        headers.setdefault("Authorization", f"Bearer {bearer_token}")

    payload: dict[str, Any] | None = None
    if json_body:
        payload = {entry.key: entry.value for entry in json_body}

    attempts = 0
    last_error: Exception | None = None
    timeout = httpx.Timeout(timeout_seconds)
    response: httpx.Response | None = None

    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempts in range(1, max(retry_attempts, 1) + 1):
            try:
                response = await client.request(
                    method.upper(),
                    url,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                break
            except httpx.HTTPStatusError as exc:
                # For non-retryable HTTP errors, propagate immediately with context.
                raise RuntimeError(
                    f"HTTP request failed with status {exc.response.status_code}"
                ) from exc
            except httpx.RequestError as exc:
                last_error = exc
                if attempts == max(retry_attempts, 1):
                    raise RuntimeError("HTTP request failed after retries") from exc
                await asyncio.sleep(0.5 * attempts)
        else:
            if last_error:
                raise last_error
            raise RuntimeError("HTTP request could not be completed")

    if response is None:
        raise RuntimeError("HTTP request completed with no response object")

    body: dict[str, Any] | None
    text_preview = ""
    try:
        body = response.json()
    except ValueError:
        body = None
        text_preview = response.text[:500]

    redacted_headers = {
        key: value for key, value in response.headers.items() if key.lower() != "set-cookie"
    }

    notes = description or "Caller agent executed the HTTP request via execute_http_request."
    if bearer_env:
        notes += f" Credential sourced from {bearer_env}."

    return HttpRequestResult(
        method=method.upper(),
        url=url,
        status_code=response.status_code,
        response_headers=dict(redacted_headers),
        response_body=body,
        text_preview=text_preview,
        attempts=attempts,
        notes=notes,
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
        "When execution is required, call the publish_meta_business_post tool to "
        "submit content to the Graph API, then provide follow-up notes for the "
        "caller agent if additional HTTP work is required."
    ),
    tools=[publish_meta_business_post],
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
        "agent to execute HTTP calls using the execute_http_request tool."
    ),
    handoffs=[],
)


caller_agent = Agent(
    name="caller_agent",
    instructions=(
        "You translate campaign plans into executable HTTP requests. Verify that "
        "all sensitive credentials are sourced from environment variables (never "
        "hard-coded). Generate step-by-step execution notes, perform the HTTP call "
        "directly via the execute_http_request tool, and list any follow-up "
        "commands engineers should run with curl or Postman collections."
    ),
    tools=[execute_http_request],
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
