from pydantic import BaseModel
from typing import List
import os
import json
from openai import OpenAI

# Try to import from either the installed 'openai.agents' package or
# the local 'agents' package. This fallback ensures the agent can run
# in environments where the package name differs or installation is missing.
try:
    from openai.agents import Agent, AgentInputItem, Runner, withTrace, ModelSettings
except Exception:
    # Official 'openai-agents' installs a top-level `agents` package.
    # Import relevant symbols from `agents` and provide aliasing for
    # types that may have different names across versions (e.g., TResponseInputItem).
    try:
        from agents import Agent, Runner, ModelSettings
        # `withTrace` may not be available in all `agents` versions; try importing it.
        try:
            from agents import withTrace
        except Exception:
            withTrace = None
        from agents.items import TResponseInputItem as AgentInputItem
    except Exception:
        # Minimal fallback if `agents` package has a different API.
        from agents import Agent, Runner
        withTrace = None
        AgentInputItem = None

class Company(BaseModel):
    company_name: str
    industry: str
    headquarters_location: str
    company_size: str
    website: str
    description: str
    founded_year: int

class WebResearchAgentOutput(BaseModel):
    companies: List[Company]

class SummarizeAndDisplayOutput(BaseModel):
    company_name: str
    industry: str
    headquarters_location: str
    company_size: str
    website: str
    description: str
    founded_year: int

web_research_agent = Agent(
    name="Web research agent",
    instructions="You are a helpful assistant. Use web search to find information about the following company I can use in marketing asset based on the underlying topic.",
    model="gpt-4.1",
    output_type=WebResearchAgentOutput,
    model_settings=ModelSettings(
        temperature=1,
        top_p=1,
        max_tokens=2048,
        store=True,
    )
)

summarize_and_display = Agent(
    name="Summarize and display",
    instructions="Put the research together in a nice display using the output format described.",
    model="gpt-4.1",
    output_type=SummarizeAndDisplayOutput,
    model_settings=ModelSettings(
        reasoning={"effort": "minimal", "summary": "auto"},
        store=True,
    )
)

async def run_web_research_workflow(input_text: str):
    # Use `withTrace` if available; otherwise use a no-op async context manager.
    if withTrace is None:
        from contextlib import asynccontextmanager

        @asynccontextmanager
        async def _noop_trace(*args, **kwargs):
            yield

        _trace_ctx = _noop_trace()
    else:
        _trace_ctx = withTrace("web research agent")

    async with _trace_ctx:
        state = {}
        conversation_history: List[AgentInputItem] = [
            {"role": "user", "content": [{"type": "input_text", "text": input_text}]}
        ]
        # Instantiate Runner in a backwards-compatible way: some versions accept
        # `trace_metadata` in the constructor, others require no-arg construction
        # and accept trace metadata on `run()` or via an attribute. Try the
        # constructor first and fall back to a no-arg Runner if needed.
        trace_metadata = {
            "__trace_source__": "agent-builder",
            "workflow_id": "wf_6902eca050788190a1ddf8a59364d5de0e4a2bb1fc56131c"
        }

        try:
            runner = Runner(trace_metadata=trace_metadata)
        except Exception:
            # Some Runner implementations don't accept constructor args
            # or may raise other errors; fall back to no-arg construction.
            try:
                runner = Runner()
            except Exception:
                # If Runner can't be constructed, re-raise with context.
                raise

        # If the runner instance supports setting trace metadata as an
        # attribute, set it so older/newer APIs can read it from the
        # instance rather than constructor args.
        try:
            setattr(runner, 'trace_metadata', trace_metadata)
        except Exception:
            # Ignore if attribute assignment isn't supported.
            pass

        # Helper to call runner.run with trace metadata if supported.
        async def _run_with_trace(runner_obj, agent_obj, history):
            import inspect

            run_kwargs = {}
            try:
                sig = inspect.signature(runner_obj.run)
                if 'trace_metadata' in sig.parameters:
                    run_kwargs['trace_metadata'] = trace_metadata
                elif 'trace' in sig.parameters:
                    run_kwargs['trace'] = trace_metadata
            except Exception:
                # If introspection fails, fall back to passing nothing.
                pass

            # Try a few invocation patterns to support multiple library
            # versions: (agent, history, **kwargs), (history, **kwargs),
            # and (agent, history) without kwargs.
            try:
                return await runner_obj.run(agent_obj, history, **run_kwargs)
            except TypeError:
                try:
                    return await runner_obj.run(history, **run_kwargs)
                except TypeError:
                    try:
                        return await runner_obj.run(agent_obj, history)
                    except TypeError:
                        # As a last resort, try calling run with just history
                        return await runner_obj.run(history)

        try:
            # (debug prints removed)

            web_research_result = await _run_with_trace(runner, web_research_agent, conversation_history)

            # Support different shapes for new_items across library versions.
            for item in getattr(web_research_result, 'new_items', []) or []:
                if hasattr(item, 'raw_item'):
                    conversation_history.append(item.raw_item)
                else:
                    conversation_history.append(item)

            if not web_research_result.final_output:
                raise ValueError("Agent result is undefined")

            summarize_result = await _run_with_trace(runner, summarize_and_display, conversation_history)

            if not summarize_result.final_output:
                raise ValueError("Agent result is undefined")

            summarize_output = {
                "output_text": summarize_result.final_output.model_dump_json(),
                "output_parsed": summarize_result.final_output
            }
            return summarize_output
        except Exception as exc:
            # If the agents Runner raises a BadRequest due to input shape
            # mismatches with the installed OpenAI client, fall back to a
            # direct Responses API call with a normalized single-string input.
            err_str = str(exc)
            if "Invalid type for 'input[1]'" in err_str or 'invalid_type' in err_str.lower():
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    raise

                client = OpenAI(api_key=api_key)
                system_text = web_research_agent.instructions or ''
                prompt_text = f"{system_text}\n\nUser: {input_text}"

                fallback_payload = {
                    "model": web_research_agent.model or "gpt-4.1",
                    "input": prompt_text,
                    "temperature": web_research_agent.model_settings.temperature if getattr(web_research_agent, 'model_settings', None) else 1,
                    "store": True,
                }
                # (debug prints removed)

                try:
                    response = client.responses.create(
                        model=fallback_payload["model"],
                        input=fallback_payload["input"],
                        temperature=fallback_payload["temperature"],
                        store=fallback_payload["store"],
                    )
                except Exception:
                    # Re-raise original exception if fallback fails.
                    raise

                # Extract text from response similar to other runner code
                assistant_response = ''
                output = getattr(response, 'output', None)
                if output:
                    for item in output:
                        if getattr(item, 'type', None) == 'message':
                            content = getattr(item, 'content', None)
                            if isinstance(content, list):
                                for c in content:
                                    c_type = getattr(c, 'type', None)
                                    if c_type in ("output_text", "text"):
                                        text_obj = getattr(c, 'text', None)
                                        if isinstance(text_obj, str):
                                            assistant_response += text_obj
                                        elif isinstance(text_obj, dict):
                                            text_value = text_obj.get('value') or text_obj.get('text')
                                            if text_value:
                                                assistant_response += str(text_value)
                            elif isinstance(content, str):
                                assistant_response += content

                if not assistant_response.strip():
                    raise

                # Return a lightweight compatible output dict
                return {
                    "output_text": assistant_response,
                    "output_parsed": assistant_response,
                }
            else:
                # Not an input-shape error we handle here; re-raise
                raise
        # Support different shapes for new_items across library versions.
        for item in getattr(web_research_result, 'new_items', []) or []:
            if hasattr(item, 'raw_item'):
                conversation_history.append(item.raw_item)
            else:
                # If item is already a raw dict-like item or AgentInputItem.
                conversation_history.append(item)

        if not web_research_result.final_output:
            raise ValueError("Agent result is undefined")

        web_research_output = {
            "output_text": web_research_result.final_output.model_dump_json(),
            "output_parsed": web_research_result.final_output
        }
        summarize_result = await _run_with_trace(runner, summarize_and_display, conversation_history)

        if not summarize_result.final_output:
            raise ValueError("Agent result is undefined")

        summarize_output = {
            "output_text": summarize_result.final_output.model_dump_json(),
            "output_parsed": summarize_result.final_output
        }
        return summarize_output