# ollama_client.py
import asyncio
import json
import sys
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from ollama import Client as OllamaClient

class OllamaMCPClient:
    def __init__(
        self,
        mcp_server_script: str,
        ollama_model: str = "qwen3:4b",
        ollama_url: str = "http://127.0.0.1:11434",
        max_turns: int = 5,
    ):
        self.mcp_server_script = mcp_server_script
        # FIX: Add trust_env=False to bypass system proxy settings
        self.ollama = OllamaClient(host=ollama_url, trust_env=False)
        self.model = ollama_model
        self.max_turns = max_turns

    async def run(self, user_query: str) -> str:
        transport = StdioTransport(
            command="python",
            args=[self.mcp_server_script],
        )
        async with Client(transport) as client:
            mcp_tools = await client.list_tools()
            print(f"[Client] Discovered {len(mcp_tools)} tools: {[t.name for t in mcp_tools]}")

            ollama_tools = self._convert_tools(mcp_tools)

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful GIS assistant. You have access to geospatial tools. "
                        "Use them when needed to answer the user's question. "
                        "Always provide a clear final answer after using tools."
                    ),
                },
                {"role": "user", "content": user_query},
            ]

            for turn in range(self.max_turns):
                response = self.ollama.chat(
                    model=self.model,
                    messages=messages,
                    tools=ollama_tools,
                )

                msg = response["message"]
                messages.append(msg)

                if msg.get("tool_calls"):
                    for tool_call in msg["tool_calls"]:
                        tool_name = tool_call["function"]["name"]
                        tool_args = tool_call["function"]["arguments"]
                        print(f"[Client] LLM requested tool: {tool_name}({tool_args})")

                        result = await client.call_tool(tool_name, tool_args)
                        tool_result_text = self._extract_text(result)
                        print(f"[Client] Tool result: {tool_result_text}")

                        messages.append({
                            "role": "tool",
                            "content": tool_result_text,
                            "name": tool_name,
                        })
                else:
                    final_answer = msg.get("content", "")
                    print(f"[Client] Final answer (turn {turn + 1})")
                    return final_answer

            return "Max turns reached without a final answer."

    @staticmethod
    def _convert_tools(mcp_tools):
        ollama_tools = []
        for tool in mcp_tools:
            ollama_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.input_schema,   # MCP SDK v2 spelling
                },
            })
        return ollama_tools

    @staticmethod
    def _extract_text(call_tool_result):
        """Extract plain text from a FastMCP CallToolResult (MCP SDK v2)."""
        content = getattr(call_tool_result, "content", None)
        if content is None:
            content = call_tool_result

        texts = []
        for block in content:
            if hasattr(block, "text"):
                texts.append(block.text)
            elif isinstance(block, dict) and "text" in block:
                texts.append(block["text"])

        return "\n".join(texts) if texts else str(call_tool_result)


async def main():
    if len(sys.argv) < 2:
        print("Usage: python ollama_client.py <path_to_geo_server.py>")
        sys.exit(1)

    server_script = sys.argv[1]
    client = OllamaMCPClient(
        mcp_server_script=server_script,
        ollama_model="qwen3:4b",
    )

    queries = [
        "Create a 5 km buffer around latitude 47.65, longitude -117.60. What is its approximate area?",
        "What is the distance between Seattle (47.6062, -122.3321) and Portland (45.5152, -122.6784)?",
    ]

    for q in queries:
        print("\n" + "=" * 60)
        print(f"User: {q}")
        answer = await client.run(q)
        print(f"Assistant: {answer}")


if __name__ == "__main__":
    asyncio.run(main())