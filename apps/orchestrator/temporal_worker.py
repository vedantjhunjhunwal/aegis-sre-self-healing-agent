import asyncio
from apps.config import settings


async def main():
    print(f"Temporal server configured at {settings.temporal_address}")
    print("LangGraph workflow is active in apps/orchestrator/langgraph_workflow.py")
    print("Register Temporal activities here for production hardening.")


if __name__ == "__main__":
    asyncio.run(main())
