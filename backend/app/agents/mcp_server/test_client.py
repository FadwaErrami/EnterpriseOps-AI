
import asyncio

from backend.app.agents.mcp_server.client import (
    list_mcp_tools,
    call_mcp_tool,
)


async def main():
    print("\n--- DISCOVERING MCP TOOLS ---")

    tools = await list_mcp_tools()

    for tool in tools:
        print(f"- {tool.name}: {tool.description}")

    print("\n--- CALLING MCP TOOL ---")

    result = await call_mcp_tool(
        "get_incident_details",
        {
            "incident_id": "1a9310c2-7dd2-4134-bed5-a08950371ae2"
        },
    )

    for item in result.content:
        if hasattr(item, "text"):
            print(item.text)

    if result.isError:
        raise RuntimeError("MCP tool execution failed.")


if __name__ == "__main__":
    asyncio.run(main())
