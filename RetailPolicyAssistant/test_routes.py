import sys
sys.path.insert(0, '/c/Users/Anagha.e/project/RetailPolicy_Intelligence_Decision_Support_System/RetailPolicyAssistant')

from app.main import app

print("=== Registered Routes ===")
for route in app.routes:
    if hasattr(route, 'path') and '/token' in route.path:
        methods = getattr(route, 'methods', set())
        print(f"Path: {route.path}, Methods: {methods}")
