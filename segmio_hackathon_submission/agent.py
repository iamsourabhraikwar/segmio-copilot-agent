# Apply Python 3.14 cloudpickle monkeypatch if standard _pickle._getattribute is missing
try:
    import _pickle
    has_getattribute = hasattr(_pickle, "_getattribute")
except ImportError:
    has_getattribute = False

if not has_getattribute:
    import cloudpickle.cloudpickle
    def custom_cloudpickle_getattribute(obj, dotted_path):
        if isinstance(dotted_path, str):
            dotted_path = dotted_path.split('.')
        parent = obj
        for subpath in dotted_path:
            parent = obj
            obj = getattr(obj, subpath)
        return (obj, parent)
    cloudpickle.cloudpickle._getattribute = custom_cloudpickle_getattribute

from functools import cached_property
import cloudpickle
from google.cloud import storage
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.sessions.session import Session
from google.adk.sessions.base_session_service import GetSessionConfig
from google.adk.events.event import Event

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.genai import Client
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools import agent_tool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools import url_context


class GlobalGemini(Gemini):
  """Pins the Vertex AI client to the `global` location.

  gemini-3 series models are only served from `global`; the default ADK
  `Gemini` integration constructs a `google.genai.Client` whose location
  defaults to the AgentEngine instance's region (e.g. `us-central1`) and
  fails with model-not-found for these models. Subclassing per the override
  pattern documented on `google.adk.models.google_llm.Gemini` lets the agent
  keep running in its regional AgentEngine instance while routing the model
  request to the global endpoint.
  """

  @cached_property
  def api_client(self) -> Client:
    return Client(vertexai=True, location="global")


segmio_e_commerce_co_pilot_v1_google_search_agent = LlmAgent(
  name='Segmio_E_commerce_Co_Pilot_V1_google_search_agent',
  model=GlobalGemini(model='gemini-3.5-flash'),
  description=(
      'Agent specialized in performing Google searches.'
  ),
  sub_agents=[],
  instruction='Use the GoogleSearchTool to find information on the web.',
  tools=[
    GoogleSearchTool()
  ],
)
segmio_e_commerce_co_pilot_v1_url_context_agent = LlmAgent(
  name='Segmio_E_commerce_Co_Pilot_V1_url_context_agent',
  model=GlobalGemini(model='gemini-3.5-flash'),
  description=(
      'Agent specialized in fetching content from URLs.'
  ),
  sub_agents=[],
  instruction='Use the UrlContextTool to retrieve content from provided URLs.',
  tools=[
    url_context
  ],
)
root_agent = LlmAgent(
  name='Segmio_E_commerce_Co_Pilot_V1',
  model=GlobalGemini(model='gemini-3.5-flash'),
  description=(
      'AI Technical Director that connects to MongoDB store inventory via MCP, drafts promotional video scripts, and coordinates sequential rendering pipelines with visual continuity on Segmio.'
  ),
  sub_agents=[],
  instruction='You are the Segmio E-commerce Production Co-Pilot. Your job is to help users generate promotional videos from their MongoDB product inventory. You operate strictly in two phases:\n\nPHASE 1: DRAFT & REVIEW (Default)\n1. When the user asks for a video, use the `mongodb_mcp` tool to fetch product details (Title, Description, Image URL).\n2. Generate a compelling promotional script consisting of 3 to 5 distinct sentences (each sentence will form a scene in the video).\n3. Ensure each sentence is written to match specific duration constraints. Count the words in each sentence to choose the scene duration:\n   - Short sentences (up to 9 words) -> duration of 4 seconds\n   - Medium sentences (10 to 14 words) -> duration of 6 seconds\n   - Long sentences (15+ words) -> duration of 8 seconds\n4. Present a summary of the script, showing the duration in seconds next to each scene sentence, and end with:\n   ### 📝 Generated Script\n   [Scene 1 (4s/6s/8s): Insert Sentence 1]\n   [Scene 2 (4s/6s/8s): Insert Sentence 2]\n   ...\n   \n   ### 🖼️ Source Asset\n   Product Image URL: [Insert Mongo Image URL Here]\n   \n   ### 🎵 Voiceover Preview\n   Audio Preview URL: [Insert Voiceover Preview URL Here]\n5. Crucial: STOP here. Ask the user: "Does this look good? Say \'Approve\' to begin rendering the final video."\n\nPHASE 2: ADVANCED PIPELINE EXECUTION\nWhen the user explicitly says "Approve", "Looks good", "Go ahead", or clicks the approval button, parse the approved script and break it down into a chronological array of scenes matching the Segmio engine capabilities. For each scene:\n- Set the `duration` based on the word count (4, 6, or 8).\n- Scene 1 (The Hook):\n  - Set `reference_image_url` to the exact product image fetched from MongoDB.\n  - Set `use_last_frame_as_seed` to false (since it starts the video).\n- Scenes 2, 3, etc. (Continuity & Action):\n  - Set `use_last_frame_as_seed` to true to enforce visual continuity using the previous scene\'s last frame.\n  - Provide a highly detailed text `visual_prompt` optimized for video generation.\n  - Set `reference_image_url` to the product image if the scene focuses back on the product; otherwise, set it to null.\n\nOnce the entire sequence array is built, invoke the `trigger_segmio_pipeline` tool.',
  tools=[
    agent_tool.AgentTool(agent=segmio_e_commerce_co_pilot_v1_google_search_agent),
    agent_tool.AgentTool(agent=segmio_e_commerce_co_pilot_v1_url_context_agent),
    McpToolset(
      connection_params=StreamableHTTPConnectionParams(
        url='https://segmio.ai/api/hackathon/mcp',
      ),
    )
  ],
)

from vertexai.preview import reasoning_engines
from typing import Dict, List, Optional, Any

class MyAdkApp(reasoning_engines.AdkApp):
    def register_operations(self) -> Dict[str, List[str]]:
        return {
            "": [
                "get_session",
                "list_sessions",
                "create_session",
                "delete_session",
            ],
            "stream": [
                "stream_query",
                "streaming_agent_run_with_events",
            ],
        }

class GCSSessionService(InMemorySessionService):
    def __init__(self, bucket_name: str):
        super().__init__()
        self.bucket_name = bucket_name
        self._storage_client = None

    @property
    def storage_client(self):
        import os
        if self._storage_client is None:
            key_name = "service-account-key.json"
            if os.path.exists(key_name):
                print(f"[GCSSessionService] Loading storage credentials from local {key_name}")
                self._storage_client = storage.Client.from_service_account_json(key_name)
            else:
                # Fallback to module directory if current working directory doesn't have it
                module_dir = os.path.dirname(__file__)
                rel_path = os.path.join(module_dir, key_name)
                if os.path.exists(rel_path):
                    print(f"[GCSSessionService] Loading storage credentials from relative {rel_path}")
                    self._storage_client = storage.Client.from_service_account_json(rel_path)
                else:
                    print("[GCSSessionService] Storage key not found. Using default container credentials.")
                    self._storage_client = storage.Client()
        return self._storage_client

    def _get_gcs_path(self, app_name: str, user_id: str, session_id: str) -> str:
        return f"sessions/{app_name}/{user_id}/{session_id}.pkl"

    def _save_session_to_gcs(self, session: Session):
        try:
            path = self._get_gcs_path(session.app_name, session.user_id, session.id)
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(path)
            data = cloudpickle.dumps(session)
            blob.upload_from_string(data)
            print(f"[GCSSessionService] Saved session {session.id} to GCS bucket {self.bucket_name}")
        except Exception as e:
            print(f"[GCSSessionService] Error saving session to GCS: {e}")

    def _load_session_from_gcs(self, app_name: str, user_id: str, session_id: str) -> Optional[Session]:
        try:
            path = self._get_gcs_path(app_name, user_id, session_id)
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(path)
            if not blob.exists():
                return None
            data = blob.download_as_string()
            session = cloudpickle.loads(data)
            print(f"[GCSSessionService] Loaded session {session_id} from GCS bucket {self.bucket_name}")
            return session
        except Exception as e:
            print(f"[GCSSessionService] Error loading session from GCS: {e}")
            return None

    def _delete_session_from_gcs(self, app_name: str, user_id: str, session_id: str):
        try:
            path = self._get_gcs_path(app_name, user_id, session_id)
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(path)
            if blob.exists():
                blob.delete()
                print(f"[GCSSessionService] Deleted session {session_id} from GCS bucket {self.bucket_name}")
        except Exception as e:
            print(f"[GCSSessionService] Error deleting session from GCS: {e}")

    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Session:
        if session_id:
            existing = self._load_session_from_gcs(app_name, user_id, session_id)
            if existing:
                self.sessions.setdefault(app_name, {}).setdefault(user_id, {})[session_id] = existing
                return existing

        session = await super().create_session(
            app_name=app_name,
            user_id=user_id,
            state=state,
            session_id=session_id
        )
        self._save_session_to_gcs(session)
        return session

    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: Optional[GetSessionConfig] = None,
    ) -> Optional[Session]:
        in_memory = self.sessions.get(app_name, {}).get(user_id, {}).get(session_id)
        if not in_memory:
            loaded = self._load_session_from_gcs(app_name, user_id, session_id)
            if loaded:
                self.sessions.setdefault(app_name, {}).setdefault(user_id, {})[session_id] = loaded
                in_memory = loaded
        
        if not in_memory:
            print(f"[GCSSessionService] Session {session_id} not found in memory or GCS. Auto-creating.")
            session = await super().create_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id
            )
            self._save_session_to_gcs(session)
            return session

        return await super().get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            config=config
        )

    async def append_event(self, session: Session, event: Event) -> Event:
        app_name = session.app_name
        user_id = session.user_id
        session_id = session.id
        
        in_memory = self.sessions.get(app_name, {}).get(user_id, {}).get(session_id)
        if not in_memory:
            loaded = self._load_session_from_gcs(app_name, user_id, session_id)
            if loaded:
                self.sessions.setdefault(app_name, {}).setdefault(user_id, {})[session_id] = loaded
                session = loaded

        res_event = await super().append_event(session=session, event=event)
        
        storage_session = self.sessions.get(app_name, {}).get(user_id, {}).get(session_id)
        if storage_session:
            self._save_session_to_gcs(storage_session)
            
        return res_event

    async def delete_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
    ) -> None:
        await super().delete_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        self._delete_session_from_gcs(app_name, user_id, session_id)


def create_gcs_session_service():
    return GCSSessionService(bucket_name="segmio-v1-42520-agent-staging")
