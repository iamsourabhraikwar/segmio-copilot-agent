import os
from google.cloud import aiplatform_v1beta1 as aiplatform
from google.protobuf import struct_pb2

# Set credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\HP\Desktop\Web App\Web App Zip File\8.7\my_agent_project\service-account-key.json"

PROJECT_ID = "segmio-v1-42520"
LOCATION = "us-west1"
ENGINE_ID = "2198539470435778560"
RESOURCE_NAME = f"projects/742928471594/locations/us-west1/reasoningEngines/{ENGINE_ID}"

client = aiplatform.ReasoningEngineExecutionServiceClient(
    client_options={"api_endpoint": "us-west1-aiplatform.googleapis.com"}
)

print(f"Calling stream_query_reasoning_engine for resource: {RESOURCE_NAME}...")

try:
    # Build struct input with session_id
    input_dict = {
        "message": "Hello! What products are available in the MongoDB database?",
        "user_id": "test-user-123",
        "session_id": "test-session-999"
    }
    
    # We must convert input_dict to a Protocol Buffers Struct
    from google.protobuf.struct_pb2 import Struct
    input_struct = Struct()
    input_struct.update(input_dict)
    
    request = {
        "name": RESOURCE_NAME,
        "input": input_struct,
        "class_method": "stream_query"
    }
    
    # stream_query_reasoning_engine returns a generator
    response_stream = client.stream_query_reasoning_engine(request=request)
    
    print("\n--- Stream Response ---")
    for response in response_stream:
        print(response)
    print("----------------------\n")
    print("SUCCESS: Deployed reasoning engine works perfectly!")
except Exception as e:
    print("\n--- Error ---")
    print(e)
    import traceback
    traceback.print_exc()
    print("-------------\n")
