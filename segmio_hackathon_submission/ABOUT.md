# Devpost Submission Text: About the Project

This file contains the complete copy-pasteable text for your Devpost project submission. You can use these sections to fill out the Devpost submission form.

---

## 1. Elevator Pitch (One-sentence summary)
An intelligent, stateful AI agent powered by Google Cloud Reasoning Engines and Gemini 3.5 Flash that queries live MongoDB product inventory via MCP, generates high-impact promotional scripts, and triggers multi-scene marketing video compiles with visual continuity.

---

## 2. The Story: About the Project

### 💡 Inspiration (Why we built it)
In e-commerce, promotional video ads drive conversion, but generating custom videos for thousands of catalog items is a slow, manual bottleneck. We wanted to build an agent that bridges the gap between database inventory and automated video generation. By using Gemini's advanced reasoning to query live products, draft structured scripts, and automatically trigger rendering pipelines, we turn manual marketing operations into a one-click automated flow.

### 🎯 Alignment with Hackathon Vision
We designed Segmio E-commerce Co-Pilot to address the hackathon's core challenge: creating **AI that doesn't just provide answers—it helps you take action**. Instead of simply chatting with the user about database records, this agent functions as an automated marketing coordinator. By moving beyond a simple chatbot, it operates a dual-phase workspace where it autonomously queries databases via MCP, drafts structured timelines, and triggers real-world video generation pipelines under human oversight.

### ⚙️ What it does
**Segmio E-commerce Co-Pilot** is a production co-pilot that:
1. **Discovers and Queries Inventory**: Connects to your live MongoDB Atlas product inventory using the Model Context Protocol (MCP) to fuzzy-search names, category metadata, prices, and images.
2. **Generates Multi-Scene Script Drafts**: Analyzes retrieved inventory items to draft a 3-to-5 scene sequence, automatically setting scene durations based on word-count constraints (4s, 6s, or 8s).
3. **Orchestrates Visual Continuity**: Designs visual generation prompts for each scene, marking subsequent scenes as **Continuity Frames** (informing the render engine to use the last frame of the previous scene as a seed) to prevent visual drift.
4. **Triggers Video Compilation**: Once reviewed and approved (via the "Approve" button or by typing "looks good" in chat), it triggers our video rendering engine and displays real-time execution logs in our Agent Thought Drawer.

### 🛠️ How we built it
* **Vertex AI Reasoning Engines / Agent Builder**: Deployed a stateful Python agent using the Google ADK, powered by **Gemini 3.5 Flash** to manage multi-turn sessions.
* **Streamable HTTP MCP Server**: Built a Next.js API route that handles JSON-RPC 2.0 tool calls, connecting the agent to MongoDB and our rendering pipeline.
* **MongoDB Atlas Database**: Programmed regex-based fuzzy product filters to lookup titles, categories, and image assets.
* **Robust Local Routing**: Implemented dynamic local loopbacks to route rendering requests directly to the standalone server, bypassing public Cloudflare WAF blockages in staging.
* **Dynamic SSE Stream Parser**: Engineered a custom frontend parser that extracts structured script tables and preview assets from the streaming SSE response in real-time.

### 🛑 Challenges we ran into
* **Reverse Proxy WAF Blockages**: When the MCP server tried to contact the rendering pipeline via its public domain, security layers blocked the connection. We resolved this by routing requests locally through `127.0.0.1:PORT` with an abort timeout safety net.
* **Stateless Conversational Loops**: Ensuring the agent remembers previous script drafts across approval queries. We implemented custom GCS pickle storage to persist the reasoning engine state.
* **Multi-Format Extraction**: The agent sometimes generated script tables or list bullets differently. We built a robust markdown regex parser that extracts scenes accurately from any output structure.

### 🏆 Accomplishments that we're proud of
* Establishing a seamless human-in-the-loop approval workflow where the user can preview synthesized voiceover audio, product base assets, and scene prompt settings before committing credits.
* Designing a clean local loopback architecture that enables inter-process tool execution reliably.
* Generating beautiful, stitched videos with true visual continuity.

### 📖 What we learned
* Harnessing stateful Google Cloud ADK session managers using cloudpickle and GCP Storage buckets.
* Formatting tools and schemas for JSON-RPC MCP server discovery.
* Writing visual prompt structures that direct AI video compilation models efficiently.

### 🔮 What's next for Segmio E-commerce Co-Pilot
* Expanding the MongoDB MCP schemas to handle product specifications and inventory availability.
* Integrating custom brand voice synthesis directly within the prompt creation phase.
* Implementing automated publishing endpoints to upload compiled videos straight to TikTok and Instagram.
