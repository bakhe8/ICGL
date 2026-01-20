import os
import re
import sys
from pathlib import Path

# ICGL Self-Healing Utility
# Scans for common errors (NameError, SyntaxError) and proposes fixes.

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SERVER_FILE = PROJECT_ROOT / "api" / "server.py"

def check_server_syntax():
    print(f"🔍 Checking Syntax in {SERVER_FILE}...")
    try:
        source = SERVER_FILE.read_text(encoding="utf-8")
        compile(source, SERVER_FILE, "exec")
        print("✅ Syntax is valid.")
    except SyntaxError as e:
        print(f"❌ Syntax Error found: {e}")
        print(f"Line {e.lineno}: {e.text.strip() if e.text else ''}")
        return False
    return True

def scan_for_unscoped_vars():
    print(f"🔍 Scanning for unscoped ICGL variables in {SERVER_FILE}...")
    source = SERVER_FILE.read_text(encoding="utf-8")
    
    # Common variables that should be accessed via icgl.
    unscoped_patterns = [
        r"(?<!icgl\.)\bkb\.",
        r"(?<!icgl\.)\bregistry\.",
        r"(?<!icgl\.)\bsentinel\.",
        r"(?<!icgl\.)\bmemory\.",
        r"(?<!icgl\.)\benforcer\.",
        r"(?<!icgl\.)\bhdal\.",
        r"(?<!icgl\.)\bengineer\."
    ]
    
    found_any = False
    for pattern in unscoped_patterns:
        matches = re.finditer(pattern, source)
        for m in matches:
            line_no = source.count("\n", 0, m.start()) + 1
            print(f"⚠️ Potentially unscoped access found at line {line_no}: {m.group()}")
            found_any = True
            
    if not found_any:
        print("✅ No unscoped variables detected.")
    else:
        print("\n💡 Suggestion: Ensure these are accessed via 'icgl = get_icgl()' inside the function.")

if __name__ == "__main__":
    if not SERVER_FILE.exists():
        print(f"❌ Error: {SERVER_FILE} not found.")
        sys.exit(1)
        
    check_server_syntax()
    scan_for_unscoped_vars()
