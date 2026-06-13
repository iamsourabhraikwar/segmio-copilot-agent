# Segmio E-commerce Production Co-Pilot

## Overview
This is an AI Technical Director agent powered by **Gemini 3.5 Flash** and **Google Cloud Agent Builder**. It connects to MongoDB store inventory via MCP, drafts promotional video scripts, and coordinates sequential rendering pipelines with visual continuity on Segmio.

This project was built for the **Build with Gemini XPRIZE** hackathon.

## Live Demo
- **Web App:** [https://segmio.ai/agent](https://segmio.ai/agent)
- **Demo Video:** [Watch on YouTube](https://youtu.be/XUnNc34hweQ)

## Features
- Fetches product details via MongoDB MCP (`mongodb_mcp`).
- Generates a compelling promotional script powered by Gemini 3.5 Flash.
- Computes scene durations based on script word count.
- Triggers multi-scene AI video rendering via Segmio pipeline (`trigger_segmio_pipeline`).
- Visual continuity between scenes using last-frame seeding with Google Veo 3.1 Fast.
- AI image generation using Nano Banana 2 (Gemini Flash Image).
- AI voiceover generation using ElevenLabs TTS.
- Session persistence via Google Cloud Storage.

## Architecture

```
User Chat (segmio.ai/agent)
    │
    ▼
Gemini 3.5 Flash (via Vertex AI Reasoning Engine)
    │
    ├── MCP Tool: mongodb_mcp ──► MongoDB Atlas (product inventory)
    │
    └── MCP Tool: trigger_segmio_pipeline ──► Segmio Rendering Pipeline
                                                  │
                                                  ├── Nano Banana 2 (Gemini Image Gen)
                                                  ├── Google Veo 3.1 Fast (Video Gen)
                                                  ├── ElevenLabs TTS (Voiceover)
                                                  └── FFmpeg (Video Merge + Audio)
```

## Google Cloud Products Used
- **Vertex AI** — Gemini 3.5 Flash model hosting via Reasoning Engine
- **Google ADK** — Agent Development Kit for tool orchestration
- **Google Cloud Storage** — Session persistence
- **Imagen / Veo** — AI image and video generation

## Prerequisites
- Google Cloud Account with Vertex AI enabled.
- Python 3.10+
- Google Cloud Service Account credentials (`service-account-key.json`).

## Setup & Deployment Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/iamsourabhraikwar/segmio-copilot-agent.git
   cd segmio-copilot-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   Copy `.env.example` to `.env` and fill in your GCP project details. Place your `service-account-key.json` in the root directory.

4. Deploy the Agent to GCP:
   ```bash
   python main.py
   ```
   This will deploy the agent to Vertex AI Reasoning Engine. Take note of the `Resource Name` printed in the console.

5. Run the Web Interface (optional local testing):
   ```bash
   streamlit run app.py
   ```
   In the sidebar, paste the `Resource Name` you obtained in step 4.

## License
MIT License
