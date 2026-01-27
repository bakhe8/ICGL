import subprocess
import sys

try:
    out = subprocess.check_output("netstat -ano", shell=True, text=True)
except Exception as e:
    print("ERROR", e)
    sys.exit(2)

for line in out.splitlines():
    if ":8000 " in line or ":8000\t" in line:
        parts = line.split()
        pid = parts[-1]
        print("FOUND", pid)
        try:
            subprocess.check_call(["taskkill", "/F", "/PID", pid])
            print("KILLED", pid)
            sys.exit(0)
        except Exception as e:
            print("KILL_FAILED", e)
            sys.exit(3)

print("NO_PID")
sys.exit(0)
