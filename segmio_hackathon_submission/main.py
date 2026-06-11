"""
Segmio E-commerce Production Co-Pilot Agent
=============================================
GCP Agent Builder deployment using Google ADK with MCP tools.
Connects to the Segmio MCP Server (Streamable HTTP) for:
  - mongodb_mcp: Fuzzy search store product inventory
  - trigger_segmio_pipeline: Trigger multi-scene AI video rendering
"""

import vertexai
from agent import root_agent, MyAdkApp, create_gcs_session_service

# ─── Configuration ───────────────────────────────────────────────────────────
PROJECT_ID = "segmio-v1-42520"
LOCATION = "us-west1"
STAGING_BUCKET = f"gs://{PROJECT_ID}-agent-staging"

# ─── Initialize Vertex AI ────────────────────────────────────────────────────
vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

# ─── Deployment via Reasoning Engine ─────────────────────────────────────────
if __name__ == "__main__":
    from vertexai.preview import reasoning_engines

    print("Deploying Segmio Co-Pilot Agent to Vertex AI...")
    print(f"   Project:  {PROJECT_ID}")
    print(f"   Location: {LOCATION}")
    print("   MCP URL:  https://segmio.ai/api/hackathon/mcp")
    print()

    app = MyAdkApp(
        agent=root_agent,
        enable_tracing=True,
        session_service_builder=create_gcs_session_service
    )

    remote_agent = reasoning_engines.ReasoningEngine.create(
        reasoning_engine=app,
        requirements=[
            "google-cloud-aiplatform[agent_engines,adk]",
            "google-adk[a2a]",
            "google-genai",
            "google-cloud-storage",
            "mcp",
            "cloudpickle==3.0",
        ],
        extra_packages=["agent.py"],
        display_name="Segmio E-commerce Co-Pilot",
        description="AI agent that searches product inventory and generates promotional videos via MCP",
    )

    print()
    print("Agent deployed successfully!")
    print(f"   Resource Name: {remote_agent.resource_name}")
    print()
    print("You can now use this agent in GCP Agent Builder.")
