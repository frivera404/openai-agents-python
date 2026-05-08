---
search:
  exclude: true
---
# ガードレール

ガードレールはエージェントと _並行して_ 実行され、ユーザー入力のチェックと検証を行います。たとえば、顧客からのリクエスト対応に非常に賢い（そのぶん遅く/高価な）モデルを使うエージェントがあるとします。悪意のあるユーザーがそのモデルに数学の宿題を手伝わせるような指示を出すのは避けたいはずです。そこで、速く/安価なモデルでガードレールを実行できます。ガードレールが悪用を検出した場合、即座にエラーを発生させ、高価なモデルの実行を止め、時間とコストを節約します。

ガードレールには 3 つの種類があります。

1. 入力ガードレールは最初のユーザー入力に対して実行されます
2. 出力ガードレールは最終的なエージェント出力に対して実行されます
3. ツールガードレールは個々の関数ツール呼び出しの前後に実行されます

## 入力ガードレール

入力ガードレールは 3 つのステップで動作します。

1. まず、ガードレールはエージェントに渡されたのと同じ入力を受け取ります。
2. 次に、ガードレール関数が実行され、[`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput] を生成し、それを [`InputGuardrailResult`][agents.guardrail.InputGuardrailResult] でラップします
3. 最後に、[`.tripwire_triggered`][agents.guardrail.GuardrailFunctionOutput.tripwire_triggered] が true かどうかを確認します。true の場合、[`InputGuardrailTripwireTriggered`][agents.exceptions.InputGuardrailTripwireTriggered] 例外が送出され、ユーザーへの適切な応答や例外処理ができます。

!!! Note

    入力ガードレールはユーザー入力に対して実行されることを意図しているため、エージェントのガードレールはそのエージェントが「最初の」エージェントである場合にのみ実行されます。なぜ `guardrails` プロパティがエージェント側にあり、`Runner.run` に渡さないのか不思議に思うかもしれません。これは、ガードレールが実際のエージェントに密接に関係する傾向があるためです。エージェントごとに異なるガードレールを実行するので、コードを同じ場所に置くことで可読性が向上します。

## 出力ガードレール

出力ガードレールは 3 つのステップで動作します。

1. まず、ガードレールはエージェントが生成した出力を受け取ります。
2. 次に、ガードレール関数が実行され、[`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput] を生成し、それを [`OutputGuardrailResult`][agents.guardrail.OutputGuardrailResult] でラップします
3. 最後に、[`.tripwire_triggered`][agents.guardrail.GuardrailFunctionOutput.tripwire_triggered] が true かどうかを確認します。true の場合、[`OutputGuardrailTripwireTriggered`][agents.exceptions.OutputGuardrailTripwireTriggered] 例外が送出され、ユーザーへの適切な応答や例外処理ができます。

!!! Note

    出力ガードレールは最終的なエージェント出力に対して実行されることを意図しているため、エージェントのガードレールはそのエージェントが「最後の」エージェントである場合にのみ実行されます。入力ガードレールと同様に、ガードレールは実際のエージェントに密接に関連することが多いため、コードを同じ場所に置くことで可読性が向上します。

## トリップワイヤー

入力または出力がガードレールに失敗した場合、ガードレールはトリップワイヤーでそれを示せます。トリップワイヤーが作動したガードレールを検出するとすぐに、{Input,Output}GuardrailTripwireTriggered 例外を送出し、エージェントの実行を停止します。

## ガードレールの実装

入力を受け取り、[`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput] を返す関数を用意する必要があります。この例では、内部でエージェントを実行してこれを行います。

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

1. このエージェントをガードレール関数内で使用します。
2. これはエージェントの入力/コンテキストを受け取り、結果を返すガードレール関数です。
3. ガードレール結果に追加情報を含めることができます。
4. これはワークフローを定義する実際のエージェントです。

出力ガードレールも同様です。

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

1. これは実際のエージェントの出力型です。
2. これはガードレールの出力型です。
3. これはエージェントの出力を受け取り、結果を返すガードレール関数です。
4. これはワークフローを定義する実際のエージェントです。

## ツールガードレール

ツールガードレールは個々の関数ツール呼び出しの前後に実行され、エージェントレベルではなくツールレベルでのきめ細かい制御を可能にします。入力・出力ガードレールとは異なり、ツールガードレールは呼び出しを続行させる、モデルへのメッセージとともにコンテンツを拒否する、または実行を停止するために例外を発生させることができます。

ツールガードレールには 2 つの種類があります。

- [`ToolInputGuardrail`][agents.tool_guardrails.ToolInputGuardrail]: ツール関数が呼び出される前に実行されます
- [`ToolOutputGuardrail`][agents.tool_guardrails.ToolOutputGuardrail]: ツール関数が出力を生成した後に実行されます

ツールガードレールは `tool_input_guardrails` および `tool_output_guardrails` フィールドを通じて [`FunctionTool`][agents.tool.FunctionTool] にアタッチされます。

### ツールガードレールの出力

ガードレール関数は [`ToolGuardrailFunctionOutput`][agents.tool_guardrails.ToolGuardrailFunctionOutput] を返す必要があります。希望する動作を表現するために、以下のファクトリーメソッドを使用します。

- `ToolGuardrailFunctionOutput.allow()`: ツール呼び出し・出力を通常通り続行させます（デフォルト）。
- `ToolGuardrailFunctionOutput.reject_content(message)`: コンテンツを拒否しつつエージェントの実行を続行し、ツール結果の代わりに `message` をモデルに送信します。
- `ToolGuardrailFunctionOutput.raise_exception()`: [`ToolInputGuardrailTripwireTriggered`][agents.exceptions.ToolInputGuardrailTripwireTriggered] または [`ToolOutputGuardrailTripwireTriggered`][agents.exceptions.ToolOutputGuardrailTripwireTriggered] 例外を発生させて実行を停止します。

### ツール入力ガードレールの実装

`@tool_input_guardrail` デコレータを使用します（または `ToolInputGuardrail` を直接構築します）。ガードレール関数は、ツールコンテキストとエージェントを含む [`ToolInputGuardrailData`][agents.tool_guardrails.ToolInputGuardrailData] オブジェクトを受け取ります。

```python
from agents import Agent, function_tool
from agents.tool_guardrails import (
    ToolInputGuardrailData,
    ToolGuardrailFunctionOutput,
    tool_input_guardrail,
)

@tool_input_guardrail
def block_sensitive_paths(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    """許可されたディレクトリ外のファイルへのアクセスを拒否します。"""
    args = data.context.tool_call_params
    path = args.get("path", "")
    if ".." in path or path.startswith("/etc"):
        return ToolGuardrailFunctionOutput.reject_content(
            message="そのパスへのアクセスは許可されていません。"
        )
    return ToolGuardrailFunctionOutput.allow()


@function_tool(tool_input_guardrails=[block_sensitive_paths])
def read_file(path: str) -> str:
    """ファイルの内容を読み取ります。"""
    with open(path) as f:
        return f.read()


agent = Agent(
    name="File Assistant",
    instructions="ユーザーがファイルを読むのを助けます。",
    tools=[read_file],
)
```

### ツール出力ガードレールの実装

`@tool_output_guardrail` デコレータを使用します（または `ToolOutputGuardrail` を直接構築します）。ガードレール関数は、ツールコンテキスト、エージェント、ツールの出力を含む [`ToolOutputGuardrailData`][agents.tool_guardrails.ToolOutputGuardrailData] オブジェクトを受け取ります。

```python
from agents import Agent, function_tool
from agents.tool_guardrails import (
    ToolOutputGuardrailData,
    ToolGuardrailFunctionOutput,
    tool_output_guardrail,
)

@tool_output_guardrail
def redact_secrets(data: ToolOutputGuardrailData) -> ToolGuardrailFunctionOutput:
    """秘密鍵のような出力をモデルに渡す前にマスクします。"""
    output = str(data.output)
    if "SECRET" in output or "password" in output.lower():
        return ToolGuardrailFunctionOutput.reject_content(
            message="ツール出力に機密情報が含まれていたため、マスクされました。"
        )
    return ToolGuardrailFunctionOutput.allow()


@function_tool(tool_output_guardrails=[redact_secrets])
def fetch_config(key: str) -> str:
    """設定値を取得します。"""
    return f"{key} の値"


agent = Agent(
    name="Config Assistant",
    instructions="ユーザーが設定値を取得するのを助けます。",
    tools=[fetch_config],
)
```