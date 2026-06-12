import os
import vertexai
import cloudpickle

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\HP\Desktop\Web App\Web App Zip File\8.7\my_agent_project\service-account-key.json"
vertexai.init(project="segmio-v1-42520", location="us-west1", staging_bucket="gs://segmio-v1-42520-agent-staging")

from agent import root_agent, MyAdkApp, create_gcs_session_service

app = MyAdkApp(
    agent=root_agent,
    enable_tracing=True,
    session_service_builder=create_gcs_session_service
)

try:
    print("Attempting to pickle app...")
    pickled = cloudpickle.dumps(app)
    print("SUCCESS: Pickling succeeded! Size:", len(pickled), "bytes")
except Exception as e:
    print("Error during pickling:")
    print(e)
    import traceback
    traceback.print_exc()
