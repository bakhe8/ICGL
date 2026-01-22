import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from backend.governance.icgl import ICGL


def test_reg():
    try:
        icgl = ICGL()
        agents = icgl.registry.list_agents()
        print(
            f"Registered Roles: {[a if isinstance(a, str) else a.value for a in agents]}"
        )

        # Check for our new roles
        roles = [a if isinstance(a, str) else a.value for a in agents]
        if "testing" in roles and "verification" in roles:
            print("SUCCESS: Testing and Verification agents are registered.")
        else:
            print(f"FAILURE: Missing agents. Found: {roles}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_reg()
