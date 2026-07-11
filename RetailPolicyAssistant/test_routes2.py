import sys
sys.path.insert(0, '/c/Users/Anagha.e/project/RetailPolicy_Intelligence_Decision_Support_System/RetailPolicyAssistant')

from app.main import app

print("=== ALL Routes ===")
for route in app.routes:
    if hasattr(route, 'path'):
        methods = getattr(route, 'methods', set())
        print(f"Path: {route.path:<40} Methods: {methods}")
    else:
        print(f"Route type: {type(route)}")
