from __future__ import annotations

import json

import pytest

from agents.items import HandoffOutputItem, ToolCallOutputItem
from agents.run import Runner

from tests.fake_model import FakeModel
from tests.test_responses import (
    get_function_tool_call,
    get_handoff_tool_call,
    get_text_message,
)

from examples.r_unlimited import workflow


@pytest.mark.asyncio
async def test_social_campaign_agent_builds_meta_plan(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(workflow.META_BUSINESS_ACCOUNT_ENV, "1234567890")

    model = FakeModel()
    model.add_multiple_turn_outputs(
        [
            [
                get_function_tool_call(
                    workflow.build_meta_business_post_plan.name,
                    json.dumps(
                        {
                            "objective": "traffic",
                            "message": "Join our wellness webinar!",
                            "cta": "SIGN_UP",
                            "link": "https://bristoltalks.com/webinar",
                        }
                    ),
                )
            ],
            [get_text_message("Campaign plan prepared.")],
        ]
    )

    agent = workflow.social_campaign_agent.clone(model=model)
    result = await Runner.run(agent, "Promote the webinar on Meta.")

    tool_outputs = [item for item in result.new_items if isinstance(item, ToolCallOutputItem)]
    assert tool_outputs, "expected the agent to call the Meta planning tool"
    meta_plan = tool_outputs[0].output

    assert isinstance(meta_plan, workflow.MetaBusinessPostPlan)
    assert meta_plan.page_id == "1234567890"
    assert meta_plan.payload["objective"] == "traffic"
    assert "Campaign plan" in result.final_output


@pytest.mark.asyncio
async def test_caller_agent_drafts_http_request() -> None:
    model = FakeModel()
    model.add_multiple_turn_outputs(
        [
            [
                get_function_tool_call(
                    workflow.draft_http_request.name,
                    json.dumps(
                        {
                            "method": "post",
                            "url": "https://api.example.com/v1/sync",
                            "requires_auth": True,
                            "auth_env": "POSTMAN_API_KEY",
                            "json_body": [
                                {"key": "campaign_id", "value": "meta-123"},
                            ],
                            "extra_headers": [
                                {"name": "X-Trace-Id", "value": "abc123"},
                            ],
                            "description": "Send the payload via the caller agent.",
                        }
                    ),
                )
            ],
            [get_text_message("HTTP request ready for execution.")],
        ]
    )

    agent = workflow.caller_agent.clone(model=model)
    result = await Runner.run(agent, "Prepare the sync call.")

    tool_outputs = [item for item in result.new_items if isinstance(item, ToolCallOutputItem)]
    assert tool_outputs, "expected the caller agent to draft an HTTP plan"
    request_plan = tool_outputs[0].output

    assert isinstance(request_plan, workflow.HttpRequestPlan)
    assert request_plan.method == "POST"
    assert request_plan.headers["X-Trace-Id"] == "abc123"
    assert "HTTP request" in result.final_output


@pytest.mark.asyncio
async def test_orchestrator_handoff_to_social_agent() -> None:
    social_model = FakeModel(initial_output=[get_text_message("Social updates prepared.")])
    email_model = FakeModel(initial_output=[get_text_message("Newsletter outline ready.")])
    affiliate_model = FakeModel(initial_output=[get_text_message("Affiliate copy drafted.")])
    analytics_model = FakeModel(initial_output=[get_text_message("Analytics recap complete.")])
    caller_model = FakeModel(initial_output=[get_text_message("Caller standing by.")])

    social_agent = workflow.social_campaign_agent.clone(model=social_model)
    email_agent = workflow.email_outreach_agent.clone(model=email_model)
    affiliate_agent = workflow.affiliate_relations_agent.clone(model=affiliate_model)
    analytics_agent = workflow.analytics_insights_agent.clone(model=analytics_model)
    caller_agent = workflow.caller_agent.clone(model=caller_model)

    orchestrator_model = FakeModel()
    orchestrator_model.add_multiple_turn_outputs(
        [
            [
                get_text_message("Delegating to social agent."),
                get_handoff_tool_call(social_agent),
            ],
            [get_text_message("Workflow coordination complete.")],
        ]
    )

    orchestrator = workflow.r_unlimited_orchestrator.clone(
        model=orchestrator_model,
        handoffs=[
            social_agent,
            email_agent,
            affiliate_agent,
            analytics_agent,
            caller_agent,
        ],
    )

    result = await Runner.run(orchestrator, "Plan the wellness weekend promotions.")

    assert result.last_agent.name == social_agent.name
    assert "Social updates" in result.final_output

    handoff_outputs = [item for item in result.new_items if isinstance(item, HandoffOutputItem)]
    assert handoff_outputs, "expected the orchestrator to record the handoff output"


@pytest.mark.asyncio
async def test_email_outreach_agent_generates_copy() -> None:
    model = FakeModel(initial_output=[get_text_message("Email copy drafted.")])
    agent = workflow.email_outreach_agent.clone(model=model)

    result = await Runner.run(agent, "Draft an update for subscribers.")

    assert "Email copy" in result.final_output
