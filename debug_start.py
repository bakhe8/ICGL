import sys
import traceback

print("🔍 Debugging Modular Server Startup...")

try:
    from api.main import app
    print("✅ Successfully imported 'app' from api.main")
except Exception:
    print("❌ Failed to import api.main:")
    traceback.print_exc()
    sys.exit(1)
