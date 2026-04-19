import asyncio

import anthropic
from mcp import ClientSession
from mcp.types import ListToolsResult

client = anthropic.Anthropic()

SYSTEM_PROMPT = (
    "You are a financial assistant with access to live market data via MCP tools. "
    "IMPORTANT: Never state prices, earnings, ratios, filings, or any financial figures from memory. "
    "Always fetch data using the available tools before answering. "
    "If a tool returns no data or an error, say so explicitly — do not guess or fill in numbers. "
    "For general concept questions (e.g. 'what is P/E ratio?'), tools are not needed."
)


async def run_agentic_turn(
    message: str, session: ClientSession, mcp_tools: ListToolsResult
) -> tuple[str, list]:
    tools = [
        {"name": t.name, "description": t.description, "input_schema": t.inputSchema}
        for t in mcp_tools.tools
    ]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": message}],
        tools=tools,
        # auto: Claude decides; use "any" to force a tool call every time
        tool_choice={"type": "auto"},
    )

    text_parts, tool_calls = [], []
    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)
        elif block.type == "tool_use":
            tool_calls.append(block)

    if not tool_calls:
        return "".join(text_parts), []

    results = await asyncio.gather(*[
        session.call_tool(tc.name, tc.input) for tc in tool_calls
    ])

    tool_results = [
        {
            "type": "tool_result",
            "tool_use_id": tc.id,
            "content": r.content[0].text if r.content else "{}",
        }
        for tc, r in zip(tool_calls, results)
    ]

    final_response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": message},
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": tool_results},
        ],
    )

    return "".join(c.text for c in final_response.content if c.type == "text"), tool_calls
