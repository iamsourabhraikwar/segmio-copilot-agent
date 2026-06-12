# Segmio E-commerce Production Co-Pilot

## Overview
This is an AI Technical Director agent powered by Gemini and Google Cloud Agent Builder. It connects to MongoDB store inventory via MCP, drafts promotional video scripts, and coordinates sequential rendering pipelines with visual continuity on Segmio.

This project was built for the **Google Cloud Rapid Agent Hackathon - Google Cloud Partnerships**.

### Track
- MongoDB

## Features
- Fetches product details via MongoDB MCP (`mongodb_mcp`).
- Generates a compelling promotional script powered by Gemini 3.5 Flash.
- Computes scene durations based on script length.
- Triggers multi-scene AI video rendering via Segmio pipeline (`trigger_segmio_pipeline`).

## Prerequisites
- Google Cloud Account with Vertex AI enabled.
- Python 3.10+
- Google Cloud Service Account credentials (`service-account-key.json`).

## Setup & Deployment Instructions
1. Clone the repository:
   ```bash
   git clone <YOUR-REPOSITORY-URL>
   cd github_submission
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Authenticate with Google Cloud:
   Ensure you have a `service-account-key.json` file in the root directory for GCS Session Service storage. Alternatively, you can use Application Default Credentials.

4. Deploy the Agent to GCP:
   Update `PROJECT_ID`, `LOCATION`, and `STAGING_BUCKET` inside `main.py` if needed. Then run:
   ```bash
   python main.py
   ```
   This will deploy the agent to Vertex AI Reasoning Engine. Take note of the `Resource Name` printed in the console.

5. Run the Web Interface:
   After deployment, run the Streamlit web app to chat with your agent:
   ```bash
   streamlit run app.py
   ```
   In the sidebar of the web app, paste the `Resource Name` you obtained in step 4.

## Demonstration Video
[Link to your YouTube or Vimeo Video here]

## Hosted Project URL
[Link to your web, Android, or iOS app that interfaces with this agent]

## License
MIT License
