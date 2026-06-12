import google.adk.sessions as sessions
import inspect

# List all submodules or classes in sessions
for name, obj in inspect.getmembers(sessions):
    if inspect.ismodule(obj):
        print(f"Submodule: {name}")
        for sub_name, sub_obj in inspect.getmembers(obj):
            if inspect.isclass(sub_obj):
                print(f"  Class: {sub_name}")
