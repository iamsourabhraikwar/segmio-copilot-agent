# Segmio E-commerce Production Co-Pilot 🚀

## Overview
This is an AI Technical Director agent powered by Gemini and Google Cloud Agent Builder. It connects to MongoDB store inventory via MCP, drafts promotional video scripts, and coordinates sequential rendering pipelines with visual continuity on Segmio.

This project was built for the **Google Cloud Rapid Agent Hackathon - Google Cloud Partnerships**.

### Track
- MongoDB

## Demonstration Video
[Watch the Segmio Co-Pilot Demo on YouTube](https://youtu.be/XUnNc34hweQ)

## Features
- Fetches product details via MongoDB MCP (`mongodb_mcp`).
- Generates a compelling promotional script powered by Gemini 3.5 Flash.
- Computes scene durations based on script length.
- Triggers multi-scene AI video rendering via Segmio pipeline (`trigger_segmio_pipeline`).

## Setup & Deployment Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/iamsourabhraikwar/segmio-copilot-agent.git
   cd segmio-copilot-agent/segmio_hackathon_submission
