---
search:
  exclude: true
---
# 가드레일

가드레일은 에이전트와 _병렬로_ 실행되며, 사용자 입력에 대한 점검과 검증을 수행할 수 있게 합니다. 예를 들어, 고객 요청을 돕기 위해 매우 똑똑한(따라서 느리고 비싼) 모델을 사용하는 에이전트를 상상해 보세요. 악의적인 사용자가 수학 숙제를 도와달라고 모델에 요청하는 것은 원치 않을 것입니다. 이때 빠르고 저렴한 모델로 가드레일을 실행할 수 있습니다. 가드레일이 악의적 사용을 감지하면 즉시 오류를 발생시켜, 비용이 많이 드는 모델 실행을 중단하고 시간과 비용을 절약할 수 있습니다.

가드레일에는 세 가지 종류가 있습니다:

1. 입력 가드레일은 초기 사용자 입력에서 실행됨
2. 출력 가드레일은 최종 에이전트 출력에서 실행됨
3. 툴 가드레일은 개별 함수 툴 호출 전후에 실행됨

## 입력 가드레일

입력 가드레일은 다음 3단계로 실행됩니다:

1. 먼저, 가드레일은 에이전트에 전달된 것과 동일한 입력을 받습니다
2. 다음으로, 가드레일 함수가 실행되어 [`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput]을 생성하고, 이는 [`InputGuardrailResult`][agents.guardrail.InputGuardrailResult]로 래핑됩니다
3. 마지막으로 [`.tripwire_triggered`][agents.guardrail.GuardrailFunctionOutput.tripwire_triggered]가 true인지 확인합니다. true이면 [`InputGuardrailTripwireTriggered`][agents.exceptions.InputGuardrailTripwireTriggered] 예외가 발생하며, 이에 적절히 사용자에게 응답하거나 예외를 처리할 수 있습니다

!!! Note

    입력 가드레일은 사용자 입력에서 실행되도록 설계되었으므로, 에이전트의 가드레일은 해당 에이전트가 *첫 번째* 에이전트일 때만 실행됩니다. 왜 `guardrails` 속성이 에이전트에 있고 `Runner.run`에 전달되지 않는지 궁금할 수 있습니다. 이는 가드레일이 실제 에이전트와 밀접하게 연관되는 경향이 있기 때문입니다. 에이전트마다 서로 다른 가드레일을 실행하므로, 코드를 함께 배치하는 것이 가독성에 유리합니다.

## 출력 가드레일

출력 가드레일은 다음 3단계로 실행됩니다:

1. 먼저, 가드레일은 에이전트가 생성한 출력을 받습니다
2. 다음으로, 가드레일 함수가 실행되어 [`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput]을 생성하고, 이는 [`OutputGuardrailResult`][agents.guardrail.OutputGuardrailResult]로 래핑됩니다
3. 마지막으로 [`.tripwire_triggered`][agents.guardrail.GuardrailFunctionOutput.tripwire_triggered]가 true인지 확인합니다. true이면 [`OutputGuardrailTripwireTriggered`][agents.exceptions.OutputGuardrailTripwireTriggered] 예외가 발생하며, 이에 적절히 사용자에게 응답하거나 예외를 처리할 수 있습니다

!!! Note

    출력 가드레일은 최종 에이전트 출력에서 실행되도록 설계되었으므로, 에이전트의 가드레일은 해당 에이전트가 *마지막* 에이전트일 때만 실행됩니다. 입력 가드레일과 마찬가지로, 가드레일은 실제 에이전트와 밀접하게 연관되므로 코드를 함께 배치하는 것이 가독성에 유리합니다.

## 트립와이어

입력 또는 출력이 가드레일을 통과하지 못하면, 가드레일은 트립와이어로 이를 신호할 수 있습니다. 트립와이어가 트리거된 가드레일을 발견하는 즉시 `{Input,Output}GuardrailTripwireTriggered` 예외를 발생시키고 에이전트 실행을 중단합니다.

## 가드레일 구현

입력을 받아 [`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput]을 반환하는 함수를 제공해야 합니다. 이 예제에서는 내부적으로 에이전트를 실행하여 이를 수행합니다.

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

1. 이 에이전트를 가드레일 함수에서 사용합니다
2. 이는 에이전트의 입력/컨텍스트를 받아 결과를 반환하는 가드레일 함수입니다
3. 가드레일 결과에 추가 정보를 포함할 수 있습니다
4. 워크플로를 정의하는 실제 에이전트입니다

출력 가드레일도 유사합니다.

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

1. 실제 에이전트의 출력 타입입니다
2. 가드레일의 출력 타입입니다
3. 에이전트의 출력을 받아 결과를 반환하는 가드레일 함수입니다
4. 워크플로를 정의하는 실제 에이전트입니다

## 툴 가드레일

툴 가드레일은 개별 함수 툴 호출 전후에 실행되어, 에이전트 수준이 아닌 툴 수준에서 세밀한 제어를 가능하게 합니다. 입력/출력 가드레일과 달리, 툴 가드레일은 호출을 계속 진행시키거나, 모델에 메시지를 전달하며 콘텐츠를 거부하거나, 실행을 완전히 중단하기 위해 예외를 발생시킬 수 있습니다.

툴 가드레일에는 두 가지 종류가 있습니다:

- [`ToolInputGuardrail`][agents.tool_guardrails.ToolInputGuardrail]: 툴 함수가 호출되기 전에 실행됨
- [`ToolOutputGuardrail`][agents.tool_guardrails.ToolOutputGuardrail]: 툴 함수가 출력을 생성한 후에 실행됨

툴 가드레일은 `tool_input_guardrails` 및 `tool_output_guardrails` 필드를 통해 [`FunctionTool`][agents.tool.FunctionTool]에 연결됩니다.

### 툴 가드레일 출력

가드레일 함수는 [`ToolGuardrailFunctionOutput`][agents.tool_guardrails.ToolGuardrailFunctionOutput]을 반환해야 합니다. 원하는 동작을 표현하기 위해 팩토리 메서드를 사용하세요:

- `ToolGuardrailFunctionOutput.allow()`: 툴 호출/출력을 정상적으로 계속 진행시킵니다 (기본값).
- `ToolGuardrailFunctionOutput.reject_content(message)`: 콘텐츠를 거부하되 에이전트 실행은 계속하며, 툴 결과 대신 `message`를 모델에 전달합니다.
- `ToolGuardrailFunctionOutput.raise_exception()`: [`ToolInputGuardrailTripwireTriggered`][agents.exceptions.ToolInputGuardrailTripwireTriggered] 또는 [`ToolOutputGuardrailTripwireTriggered`][agents.exceptions.ToolOutputGuardrailTripwireTriggered] 예외를 발생시켜 실행을 중단합니다.

### 툴 입력 가드레일 구현

`@tool_input_guardrail` 데코레이터를 사용합니다 (또는 `ToolInputGuardrail`을 직접 구성). 가드레일 함수는 툴 컨텍스트와 에이전트를 포함하는 [`ToolInputGuardrailData`][agents.tool_guardrails.ToolInputGuardrailData] 객체를 받습니다.

```python
from agents import Agent, function_tool
from agents.tool_guardrails import (
    ToolInputGuardrailData,
    ToolGuardrailFunctionOutput,
    tool_input_guardrail,
)

@tool_input_guardrail
def block_sensitive_paths(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    """허용된 디렉토리 외부의 파일 접근을 차단합니다."""
    args = data.context.tool_call_params
    path = args.get("path", "")
    if ".." in path or path.startswith("/etc"):
        return ToolGuardrailFunctionOutput.reject_content(
            message="해당 경로에 대한 접근은 허용되지 않습니다."
        )
    return ToolGuardrailFunctionOutput.allow()


@function_tool(tool_input_guardrails=[block_sensitive_paths])
def read_file(path: str) -> str:
    """파일의 내용을 읽습니다."""
    with open(path) as f:
        return f.read()


agent = Agent(
    name="File Assistant",
    instructions="사용자가 파일을 읽도록 도와줍니다.",
    tools=[read_file],
)
```

### 툴 출력 가드레일 구현

`@tool_output_guardrail` 데코레이터를 사용합니다 (또는 `ToolOutputGuardrail`을 직접 구성). 가드레일 함수는 툴 컨텍스트, 에이전트, 툴의 출력을 포함하는 [`ToolOutputGuardrailData`][agents.tool_guardrails.ToolOutputGuardrailData] 객체를 받습니다.

```python
from agents import Agent, function_tool
from agents.tool_guardrails import (
    ToolOutputGuardrailData,
    ToolGuardrailFunctionOutput,
    tool_output_guardrail,
)

@tool_output_guardrail
def redact_secrets(data: ToolOutputGuardrailData) -> ToolGuardrailFunctionOutput:
    """모델에 전달되기 전에 비밀 키처럼 보이는 출력을 마스킹합니다."""
    output = str(data.output)
    if "SECRET" in output or "password" in output.lower():
        return ToolGuardrailFunctionOutput.reject_content(
            message="툴 출력에 민감한 정보가 포함되어 마스킹되었습니다."
        )
    return ToolGuardrailFunctionOutput.allow()


@function_tool(tool_output_guardrails=[redact_secrets])
def fetch_config(key: str) -> str:
    """설정 값을 가져옵니다."""
    return f"{key}의 값"


agent = Agent(
    name="Config Assistant",
    instructions="사용자가 설정 값을 가져오도록 도와줍니다.",
    tools=[fetch_config],
)
```