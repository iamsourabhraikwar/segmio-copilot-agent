import google.adk as adk
import inspect

print("ADK Version:", adk.__version__ if hasattr(adk, '__version__') else "unknown")

# List all modules in adk
for name, obj in inspect.getmembers(adk):
    if not name.startswith('_'):
        print(name)
