from __future__ import annotations

import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from agents.agent import Agent
    from openai_assistant_agent import OpenAIAssistantAgent
except Exception:
    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.append(str(PROJECT_ROOT))
    from agents.agent import Agent
    from openai_assistant_agent import OpenAIAssistantAgent


@dataclass(frozen=True)
class SubAgentSpec:
    """Lightweight description of a sub-agent managed by the supervisor.

    This is deliberately metadata-only. The underlying implementation is the
    shared OpenAIAssistantAgent, which already knows about tools and MCP.
    """

    id: str
    name: str
    role: str
    description: str


DEFAULT_SUB_AGENTS: Mapping[str, SubAgentSpec] = {
    "supervisor": SubAgentSpec(
        id="supervisor",
        name="Prime Goal Supervisor",
        role="Supervisor",
        description=(
            "Maintains global goals and decides which specialist sub-agent "
            "should handle a given request. Summarizes outcomes back to the user."
        ),
    ),
    "research": SubAgentSpec(
        id="research",
        name="Research Agent",
        role="Researcher",
        description=(
            "Uses web search and documentation tools to gather and summarize "
            "information from external sources."
        ),
    ),
    "automation": SubAgentSpec(
        id="automation",
        name="Automation Agent",
        role="Executor",
        description=(
            "Runs commands, code, and structured workflows using local shell, "
            "code interpreter, and related tools."
        ),
    ),
    "memory": SubAgentSpec(
        id="memory",
        name="Memory Agent",
        role="Knowledge Manager",
        description=(
            "Organizes and retrieves long-term project knowledge, notes, and "
            "vector-store based memories."
        ),
    ),
    "ui": SubAgentSpec(
        id="ui",
        name="Conversation Agent",
        role="User Interface",
        description=(
            "Primary conversational interface that explains plans and results "
            "clearly to the user. Typically delegates complex work to other "
            "sub-agents via the supervisor."
        ),
    ),
    "shopkeeper": SubAgentSpec(
        id="shopkeeper",
        name="ShopKeeper",
        role="Commerce Specialist",
        description=(
            "Retrieves product and offer information from ctdatenight.com and "
            "summarizes offers for conversion; bound to ctdatenight.com only."
        ),
    ),
    "retention": SubAgentSpec(
        id="retention",
        name="Retention",
        role="Retention Specialist",
        description=(
            "Creates targeted retention messaging and CTA flows using only data "
            "from ctdatenight.com."
        ),
    ),
    "info": SubAgentSpec(
        id="info",
        name="Info",
        role="Information",
        description=(
            "Answers factual queries about CTDateNight resources using only "
            "ctdatenight.com content."
        ),
    ),
}


class SupervisorOrchestrator:
    """Simple supervisor that chooses a sub-agent and wraps query results.

    Today this is intentionally lightweight: it does not construct separate
    underlying Agent instances per sub-agent. Instead, it uses the shared
    ``OpenAIAssistantAgent`` and attaches routing metadata (which sub-agent was
    chosen and why). This keeps it easy to integrate with the existing
    Prime Goal API while giving you a clear place to grow more complex
    orchestration later.
    """

    def __init__(
        self,
        agent: OpenAIAssistantAgent,
        sub_agents: Mapping[str, SubAgentSpec] | None = None,
        sub_agent_instances: Mapping[str, Agent] | None = None,
    ) -> None:
        self._agent = agent
        self._sub_agents: Mapping[str, SubAgentSpec] = sub_agents or DEFAULT_SUB_AGENTS
        # Optional concrete Agent instances for specific sub-agents. If present,
        # these will be used to run queries for the selected sub-agent instead
        # of the shared OpenAIAssistantAgent.
        self._sub_agent_instances: Mapping[str, Agent] = sub_agent_instances or {}

    def select_sub_agent(self, query: str) -> SubAgentSpec:
        """Pick a sub-agent based on simple keyword heuristics.

        This is deliberately very simple and transparent. You can extend it
        later (e.g. by calling an LLM to plan, or by adding scoring logic).
        """

        text = query.lower()
        # Hard routing for commerce / offers / signup related queries
        if any(
            tok in text
            for tok in (
                "offer",
                "offers",
                "shop",
                "shopkeeper",
                "product",
                "price",
                "signup",
                "sign up",
                "checkout",
            )
        ):
            return self._sub_agents.get("shopkeeper", self._sub_agents["ui"])

        # Retention-related queries
        if any(
            tok in text
            for tok in ("retain", "retention", "discount", "coupon", "promo", "promotions")
        ):
            return self._sub_agents.get("retention", self._sub_agents["ui"])

        # Info-specific queries
        if any(
            tok in text for tok in ("info", "information", "faq", "help", "how do i", "where can i")
        ):
            return self._sub_agents.get("info", self._sub_agents["ui"])

        if any(word in text for word in ("search", "look up", "look-up", "research", "google")):
            return self._sub_agents["research"]

        if any(word in text for word in ("run", "execute", "command", "script", "shell", "deploy")):
            return self._sub_agents["automation"]

        if any(word in text for word in ("remember", "note", "knowledge", "docs", "document")):
            return self._sub_agents["memory"]

        # Default: treat this as a normal conversational request.
        return self._sub_agents["ui"]

    async def plan(self, query: str) -> dict[str, Any]:
        """Return a small, machine-readable plan for the request.

        Structure is intentionally shallow so it is easy to surface over HTTP
        or in the UI.
        """

        sub_agent = self.select_sub_agent(query)
        return {
            "selected_sub_agent_id": sub_agent.id,
            "selected_sub_agent_name": sub_agent.name,
            "selected_sub_agent_role": sub_agent.role,
            "selected_sub_agent_description": sub_agent.description,
        }

    async def run_supervised(self, query: str, thread_id: str | None = None) -> dict[str, Any]:
        """Run a query through the shared agent with supervisor metadata.

        The result shape is a dict so it is easy to expose as JSON:

        - ``plan``: output of :meth:`plan`.
        - ``result``: whatever the underlying ``OpenAIAssistantAgent.run_query``
          returns (query, response, thread_id, timestamp, etc.).
        """

        plan = await self.plan(query)

        sub_id = plan.get("selected_sub_agent_id")

        # If we have a concrete agent instance registered for this sub-agent,
        # delegate the query to it. Fall back to the shared agent otherwise.
        agent_to_call: Any
        if sub_id and sub_id in self._sub_agent_instances:
            agent_to_call = self._sub_agent_instances[sub_id]
        else:
            agent_to_call = self._agent

        result = await agent_to_call.run_query(query, thread_id=thread_id)
        return {"plan": plan, "result": result}
