import importlib.util
import os
import sys

print("CWD=", os.getcwd())
print("PYTHONPATH env=", os.environ.get("PYTHONPATH"))
print("sys.path[0]=", sys.path[0])
print("first 6 sys.path entries:")
for p in sys.path[:6]:
    print(" -", p)
spec = importlib.util.find_spec("shared.python.agents.template")
print("spec:", spec)
try:
    import shared

    print("shared.__path__ =", getattr(shared, "__path__", None))
except Exception as e:
    print("import shared failed:", e)
