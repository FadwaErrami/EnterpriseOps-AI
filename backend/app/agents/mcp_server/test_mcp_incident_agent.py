
import asyncio
from pprint import pprint

from backend.app.agents.mcp_server.mcp_incident_agent import analyze_with_mcp

async def main():
    incident_id = "1a9310c2-7dd2-4134-bed5-a08950371ae2"

    print("\n--- LANGGRAPH + MCP WORKFLOW ---")

    result = await analyze_with_mcp(incident_id)

    print("\n--- INCIDENT ---")
    pprint(result["incident"])

    print("\n--- RECENT LOGS ---")
    pprint(result["logs"])

    print("\n--- RUNBOOKS ---")
    pprint(result["runbooks"])

    print("\n--- AI DIAGNOSIS (GROQ) ---")
    pprint(result["diagnosis"])

    print("\n--- HUMAN APPROVAL ---")
    pprint(result["approval"])

    print("\n--- HUMAN APPROVAL GATE ---")
    print("Remediation allowed:", result["remediation_allowed"])
    print("Workflow status:", result["workflow_status"])

    print("\n--- REMEDIATION RESULT ---")
    pprint(result["remediation_result"])
    
    if result.get("error"):
        print("\nERROR:", result["error"])
    else:
        print("\nMCP + LANGGRAPH WORKFLOW SUCCESSFUL")


if __name__ == "__main__":
    asyncio.run(main())
