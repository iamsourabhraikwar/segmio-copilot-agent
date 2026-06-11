# Segmio E-commerce Co-Pilot 🚀
### GCP Agent Builder & MongoDB Atlas MCP Integration

This repository contains the public "connective tissue" of the **Segmio E-commerce Co-Pilot** submission for the **MongoDB Track** of the **Google Cloud Rapid Agent Hackathon**. 

It isolates the agent configurations, model parameters, and MCP connection code from the core proprietary Segmio platform video rendering engine, keeping business logic secure while allowing judges to verify our implementation.

---

## 📂 Repository Contents

```
├── LICENSE                # MIT Open Source License (visible in repo About section)
├── README.md              # Technical documentation and deployment guides
├── ABOUT.md               # Complete copy-pasteable text for the Devpost submission
├── .gitignore             # Standard git ignore patterns for Node/Python/Secrets
├── agent.py               # Google ADK agent setup, LlmAgent, tools & GCS memory
├── main.py                # Python deployment script for Vertex AI Reasoning Engines
├── requirements.txt       # Python dependency requirements
├── prompt.txt             # Clean copy of System Prompt instructions for Gemini
├── openapi.json           # OpenAPI schema representing the MCP tool definitions
└── mcp/
    └── route.ts           # Next.js API route that operates as the Streamable HTTP MCP server
```

---

## ⚙️ How It Works

```
                     ┌──────────────────────────────┐
                     │     Google Cloud Agent       │
                     │  (Gemini 3.5 Flash Brain)    │
                     └──────────────┬───────────────┘
                                    │
            ┌───────────────────────┴───────────────────────┐
            ▼ (MCP reads product data)                      ▼ (MCP triggers render)
┌───────────────────────┐                       ┌───────────────────────┐
│     mongodb_mcp       │                       │trigger_segmio_pipeline│
└───────────┬───────────┘                       └───────────┬───────────┘
            │                                               │
            ▼                                               ▼ (HTTP POST loopback)
┌───────────────────────┐                       ┌───────────────────────┐
│  MongoDB Atlas DB     │                       │ Segmio Rendering API  │
│(Fuzzy Inventory regex)│                       │ (Veo 3.1 & continuity)│
└───────────────────────┘                       └───────────────────────┘
```

1. **Stateful Connection**: The frontend establishes an SSE stream with the deployed Vertex AI Reasoning Engine using the Google Cloud SDK and standard service account keys.
2. **MongoDB Inventory Search**: When the user requests a product video, Gemini triggers the `mongodb_mcp` tool. The MCP server performs a fuzzy regex database search on a live MongoDB Atlas cluster, returning titles, categories, pricing, descriptions, and base product images.
3. **Double-Phase Orchestration**:
   * **Phase 1 (Draft)**: Gemini crafts a 3 to 5 scene script sequence with matching duration bounds based on word counts. It stops for human-in-the-loop review.
   * **Phase 2 (Pipeline Handoff)**: Once the user approves, Gemini builds a chronological scene sequence manifest containing detailed visual prompts, reference images, and a visual continuity flag (`use_last_frame_as_seed`) for stitching frames coherently, then invokes `trigger_segmio_pipeline`.
4. **Local Loopback Routing**: To bypass public Cloudflare WAF blockages in staging, the MCP server invokes rendering internally via a loopback connection (`127.0.0.1:PORT`) using an AbortController for a 30-second timeout safety net.

---

## 🚀 Deployment (Vertex AI Reasoning Engines)

To register and deploy this agent to Google Cloud Platform:

### 1. Requirements
Ensure you have the Google Cloud CLI initialized and credentials configured:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment variables
Save your service account credential key file as `service-account-key.json` in the root folder, and set the environment parameters:
```env
GOOGLE_APPLICATION_CREDENTIALS="service-account-key.json"
```

### 3. Deplaying to GCP
Run the deployment script:
```bash
python main.py
```
This script packages `agent.py`, pushes it to your GCP staging bucket, and creates a Reasoning Engine resource running on **Gemini 3.5 Flash**.

---

## 🔌 Model Context Protocol (MCP) Setup

The MCP server is built as a Next.js API route in `mcp/route.ts` and handles Streamable HTTP requests (JSON-RPC 2.0).

### MCP Endpoints
* **POST `/api/hackathon/mcp`**: Handles standard MCP protocol methods (`initialize`, `tools/list`, `tools/call` for `mongodb_mcp` and `trigger_segmio_pipeline`).
* **DELETE `/api/hackathon/mcp`**: Destroys active HTTP sessions.

---

## 📜 License
This project is licensed under the [MIT License](LICENSE).
