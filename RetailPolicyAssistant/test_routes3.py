import sys
sys.path.insert(0, '/c/Users/Anagha.e/project/RetailPolicy_Intelligence_Decision_Support_System/RetailPolicyAssistant')

from app.main import app

print("=== Inspecting Routers ===")
for route in app.routes:
    if hasattr(route, 'router'):
        print(f"\n=== Router Routes ===")
        for r in route.router.routes:
            if hasattr(r, 'path'):
                methods = getattr(r, 'methods', set())
                print(f"  Path: {r.path:<40} Methods: {methods}")
