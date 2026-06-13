import os
import streamlit as st
import vertexai
from vertexai.preview import reasoning_engines

st.set_page_config(page_title="Segmio Co-Pilot", page_icon="🤖")

st.title("Segmio E-commerce Production Co-Pilot")
st.markdown("This agent connects to MongoDB via MCP, drafts video scripts, and coordinates the Segmio video rendering pipeline.")

# Default settings
DEFAULT_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "segmio-v1-42520")
DEFAULT_LOCATION = os.environ.get("GCP_LOCATION", "us-west1")

st.sidebar.header("Configuration")
project_id = st.sidebar.text_input("GCP Project ID", value=DEFAULT_PROJECT_ID)
location = st.sidebar.text_input("GCP Location", value=DEFAULT_LOCATION)
agent_resource = st.sidebar.text_input("Agent Resource Name", placeholder="projects/.../locations/.../reasoningEngines/...", help="Find this in Vertex AI Reasoning Engine after deploying via main.py")

st.sidebar.markdown("---")
st.sidebar.markdown("**Note:** You must deploy the agent using `python main.py` first, then copy the Resource Name here to test.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask Segmio to create a promotional video..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not agent_resource:
            st.error("Please enter the Agent Resource Name in the sidebar.")
            st.stop()
            
        with st.spinner("Agent is thinking..."):
            try:
                vertexai.init(project=project_id, location=location)
                remote_agent = reasoning_engines.ReasoningEngine(agent_resource)
                
                # ADK LlmAgent expects 'input' or 'message' string, but ReasoningEngine wrapper usually maps kwargs directly.
                response = remote_agent.query(input=prompt)
                
                # Format output depending on ADK return structure
                if isinstance(response, dict) and "output" in response:
                    reply = response["output"]
                elif isinstance(response, dict) and "response" in response:
                    reply = response["response"]
                else:
                    reply = str(response)

                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error communicating with agent: {e}")
