from app.main import app

for route in app.routes:
    methods = ",".join(route.methods) if hasattr(route, "methods") else "NONE"
    print(f"{route.path:<60} {methods:>20} {route.name}")
