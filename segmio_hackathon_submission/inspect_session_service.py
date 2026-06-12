from google.adk.sessions.base_session_service import BaseSessionService
import inspect

print("BaseSessionService Methods:")
for name, member in inspect.getmembers(BaseSessionService):
    if inspect.isfunction(member) or inspect.ismethod(member):
        sig = inspect.signature(member)
        print(f"  {name}{sig}")
