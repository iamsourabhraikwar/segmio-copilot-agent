import google.adk.sessions as sessions
import google.adk.memory as memory
import inspect

print("=== Sessions Module ===")
for name, obj in inspect.getmembers(sessions):
    if not name.startswith('_'):
        print(name)

print("\n=== Memory Module ===")
for name, obj in inspect.getmembers(memory):
    if not name.startswith('_'):
        print(name)
