from __future__ import annotations

import json

from collections.abc import AsyncIterator

import pytest

from agents.agent_output import AgentOutputSchema
from agents.handoffs import Handoff
from agents.items import (
    HandoffOutputItem,
    ModelResponse,
    ToolCallOutputItem,
    TResponseInputItem,
    TResponseOutputItem,
    TResponseStreamEvent,
)
from agents.model_settings import ModelSettings
from agents.models.interface import Model, ModelTracing
from agents.run import Runner
from agents.tool import Tool
from agents.tracing import SpanError, generation_span
from agents.usage import Usage
from openai.types.responses import Response, ResponseCompletedEvent

from tests.test_responses import (
    get_function_tool_call,
    get_handoff_tool_call,
    get_text_message,
)

from examples.r_unlimited import workflow


def _response_from_output(
    output: list[TResponseOutputItem], response_id: str | None = None
) -> Response:
    return Response(
        id=response_id or "gpt4-test-response",
        created_at=0,
        model="gpt-4",
        object="response",
        output=output,
        tool_choice="none",
        tools=[],
        top_p=None,
        parallel_tool_calls=False,
    )


class StubGpt4Model(Model):
    """A lightweight GPT-4 stand-in used for deterministic test responses."""

    def __init__(
        self,
        *,
        tracing_enabled: bool = False,
        initial_output: list[TResponseOutputItem] | Exception | None = None,
    ) -> None:
        self.model = "gpt-4"
        self._queue: list[list[TResponseOutputItem] | Exception] = []
        if initial_output is not None:
            self._queue.append(initial_output)
        self.tracing_enabled = tracing_enabled
        self.last_turn_args: dict[str, object] = {}

    def add_multiple_turn_outputs(
        self, outputs: list[list[TResponseOutputItem] | Exception]
    ) -> None:
        self._queue.extend(outputs)

    def _next_output(self) -> list[TResponseOutputItem] | Exception:
        if not self._queue:
            return []
        return self._queue.pop(0)

    async def get_response(
        self,
        system_instructions: str | None,
        input: str | list[TResponseInputItem],
        model_settings: ModelSettings,
        tools: list[Tool],
        output_schema: AgentOutputSchema | None,
        handoffs: list[Handoff],
        tracing: ModelTracing,
    ) -> ModelResponse:
        self.last_turn_args = {
            "system_instructions": system_instructions,
            "input": input,
            "model_settings": model_settings,
            "tools": tools,
            "output_schema": output_schema,
        }

        with generation_span(model="gpt-4", disabled=not self.tracing_enabled) as span:
            output = self._next_output()
            if isinstance(output, Exception):
                span.set_error(
                    SpanError(
                        message="Error",
                        data={
                            "name": output.__class__.__name__,
                            "message": str(output),
                        },
                    )
                )
                raise output

        return ModelResponse(output=output, usage=Usage(), referenceable_id=None)

    async def stream_response(
        self,
        system_instructions: str | None,
        input: str | list[TResponseInputItem],
        model_settings: ModelSettings,
        tools: list[Tool],
        output_schema: AgentOutputSchema | None,
        handoffs: list[Handoff],
        tracing: ModelTracing,
    ) -> AsyncIterator[TResponseStreamEvent]:
        output = self._next_output()
        if isinstance(output, Exception):
            raise output

        yield ResponseCompletedEvent(
            type="response.completed",
            response=_response_from_output(output),
        )


@pytest.mark.asyncio
async def test_social_campaign_agent_builds_meta_plan(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(workflow.META_BUSINESS_ACCOUNT_ENV, "1234567890")

    model = StubGpt4Model()
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
    model = StubGpt4Model()
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
    social_model = StubGpt4Model(initial_output=[get_text_message("Social updates prepared.")])
    email_model = StubGpt4Model(initial_output=[get_text_message("Newsletter outline ready.")])
    affiliate_model = StubGpt4Model(initial_output=[get_text_message("Affiliate copy drafted.")])
    analytics_model = StubGpt4Model(initial_output=[get_text_message("Analytics recap complete.")])
    caller_model = StubGpt4Model(initial_output=[get_text_message("Caller standing by.")])

    social_agent = workflow.social_campaign_agent.clone(model=social_model)
    email_agent = workflow.email_outreach_agent.clone(model=email_model)
    affiliate_agent = workflow.affiliate_relations_agent.clone(model=affiliate_model)
    analytics_agent = workflow.analytics_insights_agent.clone(model=analytics_model)
    caller_agent = workflow.caller_agent.clone(model=caller_model)

    orchestrator_model = StubGpt4Model()
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
    model = StubGpt4Model(initial_output=[get_text_message("Email copy drafted.")])
    agent = workflow.email_outreach_agent.clone(model=model)

    result = await Runner.run(agent, "Draft an update for subscribers.")

    assert "Email copy" in result.final_output
