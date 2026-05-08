# Guardrails

Guardrails run _in parallel_ to your agents, enabling you to do checks and validations of user input. For example, imagine you have an agent that uses a very smart (and hence slow/expensive) model to help with customer requests. You wouldn't want malicious users to ask the model to help them with their math homework. So, you can run a guardrail with a fast/cheap model. If the guardrail detects malicious usage, it can immediately raise an error, which stops the expensive model from running and saves you time/money.

There are three kinds of guardrails:

1. Input guardrails run on the initial user input
2. Output guardrails run on the final agent output
3. Tool guardrails run before or after individual function tool invocations

## Input guardrails

Input guardrails run in 3 steps:

1. First, the guardrail receives the same input passed to the agent.
2. Next, the guardrail function runs to produce a [`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput], which is then wrapped in an [`InputGuardrailResult`][agents.guardrail.InputGuardrailResult]
3. Finally, we check if [`.tripwire_triggered`][agents.guardrail.GuardrailFunctionOutput.tripwire_triggered] is true. If true, an [`InputGuardrailTripwireTriggered`][agents.exceptions.InputGuardrailTripwireTriggered] exception is raised, so you can appropriately respond to the user or handle the exception.

!!! Note

    Input guardrails are intended to run on user input, so an agent's guardrails only run if the agent is the *first* agent. You might wonder, why is the `guardrails` property on the agent instead of passed to `Runner.run`? It's because guardrails tend to be related to the actual Agent - you'd run different guardrails for different agents, so colocating the code is useful for readability.

## Output guardrails

Output guardrails run in 3 steps:

1. First, the guardrail receives the output produced by the agent.
2. Next, the guardrail function runs to produce a [`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput], which is then wrapped in an [`OutputGuardrailResult`][agents.guardrail.OutputGuardrailResult]
3. Finally, we check if [`.tripwire_triggered`][agents.guardrail.GuardrailFunctionOutput.tripwire_triggered] is true. If true, an [`OutputGuardrailTripwireTriggered`][agents.exceptions.OutputGuardrailTripwireTriggered] exception is raised, so you can appropriately respond to the user or handle the exception.

!!! Note

    Output guardrails are intended to run on the final agent output, so an agent's guardrails only run if the agent is the *last* agent. Similar to the input guardrails, we do this because guardrails tend to be related to the actual Agent - you'd run different guardrails for different agents, so colocating the code is useful for readability.

## Tripwires

If the input or output fails the guardrail, the Guardrail can signal this with a tripwire. As soon as we see a guardrail that has triggered the tripwires, we immediately raise a `{Input,Output}GuardrailTripwireTriggered` exception and halt the Agent execution.

## Implementing a guardrail

You need to provide a function that receives input, and returns a [`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput]. In this example, we'll do this by running an Agent under the hood.

```python
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)

class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str

guardrail_agent = Agent( # (1)!
    name="Guardrail check",
    instructions="Check if the user is asking you to do their math homework.",
    output_type=MathHomeworkOutput,
)


@input_guardrail
async def math_guardrail( # (2)!
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output, # (3)!
        tripwire_triggered=result.final_output.is_math_homework,
    )


agent = Agent(  # (4)!
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    input_guardrails=[math_guardrail],
)

async def main():
    # This should trip the guardrail
    try:
        await Runner.run(agent, "Hello, can you help me solve for x: 2x + 3 = 11?")
        print("Guardrail didn't trip - this is unexpected")

    except InputGuardrailTripwireTriggered:
        print("Math homework guardrail tripped")
```

1. We'll use this agent in our guardrail function.
2. This is the guardrail function that receives the agent's input/context, and returns the result.
3. We can include extra information in the guardrail result.
4. This is the actual agent that defines the workflow.

Output guardrails are similar.

```python
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    output_guardrail,
)
class MessageOutput(BaseModel): # (1)!
    response: str

class MathOutput(BaseModel): # (2)!
    reasoning: str
    is_math: bool

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the output includes any math.",
    output_type=MathOutput,
)

@output_guardrail
async def math_guardrail(  # (3)!
    ctx: RunContextWrapper, agent: Agent, output: MessageOutput
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, output.response, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math,
    )

agent = Agent( # (4)!
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    output_guardrails=[math_guardrail],
    output_type=MessageOutput,
)

async def main():
    # This should trip the guardrail
    try:
        await Runner.run(agent, "Hello, can you help me solve for x: 2x + 3 = 11?")
        print("Guardrail didn't trip - this is unexpected")

    except OutputGuardrailTripwireTriggered:
        print("Math output guardrail tripped")
```

1. This is the actual agent's output type.
2. This is the guardrail's output type.
3. This is the guardrail function that receives the agent's output, and returns the result.
4. This is the actual agent that defines the workflow.

## Tool guardrails

Tool guardrails run before or after individual function tool invocations, allowing fine-grained control at the tool level rather than at the agent level. Unlike input/output guardrails, tool guardrails can either allow the call to proceed, reject the content with a message to the model, or raise an exception to halt execution entirely.

There are two kinds of tool guardrails:

- [`ToolInputGuardrail`][agents.tool_guardrails.ToolInputGuardrail]: runs before the tool function is invoked
- [`ToolOutputGuardrail`][agents.tool_guardrails.ToolOutputGuardrail]: runs after the tool function has produced its output

Tool guardrails are attached to a [`FunctionTool`][agents.tool.FunctionTool] via the `tool_input_guardrails` and `tool_output_guardrails` fields.

### Tool guardrail output

Your guardrail function must return a [`ToolGuardrailFunctionOutput`][agents.tool_guardrails.ToolGuardrailFunctionOutput]. Use the factory methods to express the desired behavior:

- `ToolGuardrailFunctionOutput.allow()`: Allow the tool call/output to proceed normally (default).
- `ToolGuardrailFunctionOutput.reject_content(message)`: Reject the content but continue agent execution, sending `message` to the model instead of the tool result.
- `ToolGuardrailFunctionOutput.raise_exception()`: Halt execution by raising a [`ToolInputGuardrailTripwireTriggered`][agents.exceptions.ToolInputGuardrailTripwireTriggered] or [`ToolOutputGuardrailTripwireTriggered`][agents.exceptions.ToolOutputGuardrailTripwireTriggered] exception.

### Implementing tool input guardrails

Use the `@tool_input_guardrail` decorator (or construct a `ToolInputGuardrail` directly). The guardrail function receives a [`ToolInputGuardrailData`][agents.tool_guardrails.ToolInputGuardrailData] object containing the tool context and the agent.

```python
from agents import Agent, function_tool
from agents.tool_guardrails import (
    ToolInputGuardrailData,
    ToolGuardrailFunctionOutput,
    tool_input_guardrail,
)

@tool_input_guardrail
def block_sensitive_paths(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    """Reject any attempt to read files outside the allowed directory."""
    args = data.context.tool_call_params  # raw JSON-decoded arguments dict
    path = args.get("path", "")
    if ".." in path or path.startswith("/etc"):
        return ToolGuardrailFunctionOutput.reject_content(
            message="Access to that path is not allowed."
        )
    return ToolGuardrailFunctionOutput.allow()


@function_tool(tool_input_guardrails=[block_sensitive_paths])
def read_file(path: str) -> str:
    """Read the contents of a file."""
    with open(path) as f:
        return f.read()


agent = Agent(
    name="File Assistant",
    instructions="Help the user read files.",
    tools=[read_file],
)
```

### Implementing tool output guardrails

Use the `@tool_output_guardrail` decorator (or construct a `ToolOutputGuardrail` directly). The guardrail function receives a [`ToolOutputGuardrailData`][agents.tool_guardrails.ToolOutputGuardrailData] object containing the tool context, the agent, and the tool's output.

```python
from agents import Agent, function_tool
from agents.tool_guardrails import (
    ToolOutputGuardrailData,
    ToolGuardrailFunctionOutput,
    tool_output_guardrail,
)

@tool_output_guardrail
def redact_secrets(data: ToolOutputGuardrailData) -> ToolGuardrailFunctionOutput:
    """Redact any output that looks like a secret key before it reaches the model."""
    output = str(data.output)
    if "SECRET" in output or "password" in output.lower():
        return ToolGuardrailFunctionOutput.reject_content(
            message="The tool output contained sensitive information and was redacted."
        )
    return ToolGuardrailFunctionOutput.allow()


@function_tool(tool_output_guardrails=[redact_secrets])
def fetch_config(key: str) -> str:
    """Fetch a configuration value."""
    return f"Value for {key}"


agent = Agent(
    name="Config Assistant",
    instructions="Help the user fetch configuration values.",
    tools=[fetch_config],
)
```

### Raising exceptions from tool guardrails

When you want to completely stop execution rather than just rejecting the content, return `ToolGuardrailFunctionOutput.raise_exception()`. The runner will raise a `ToolInputGuardrailTripwireTriggered` or `ToolOutputGuardrailTripwireTriggered` exception that you can catch in your application code.

```python
from agents import Agent, Runner, function_tool
from agents.exceptions import ToolInputGuardrailTripwireTriggered
from agents.tool_guardrails import (
    ToolInputGuardrailData,
    ToolGuardrailFunctionOutput,
    tool_input_guardrail,
)

@tool_input_guardrail
def require_approval(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    """Halt execution if the action has not been approved."""
    approved = data.context.tool_call_params.get("approved", False)
    if not approved:
        return ToolGuardrailFunctionOutput.raise_exception()
    return ToolGuardrailFunctionOutput.allow()


@function_tool(tool_input_guardrails=[require_approval])
def perform_action(action: str, approved: bool = False) -> str:
    """Perform a privileged action."""
    return f"Action '{action}' completed."


async def main():
    agent = Agent(
        name="Action Agent",
        instructions="Perform actions when asked.",
        tools=[perform_action],
    )
    try:
        result = await Runner.run(agent, "Perform the action 'deploy'.")
        print(result.final_output)
    except ToolInputGuardrailTripwireTriggered:
        print("Action was blocked: approval required.")
```