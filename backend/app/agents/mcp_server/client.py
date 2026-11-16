
import sys

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


server_params = StdioServerParameters(
    command=sys.executable,
    args=["-m", "backend.app.agents.mcp_server.server"],
)


async def list_mcp_tools():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.list_tools()
            return result.tools


async def call_mcp_tool(tool_name: str, arguments: dict):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                tool_name,
                arguments=arguments,
            )
            return result
