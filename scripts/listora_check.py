
import importlib.util
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
APP = BACKEND / "app"

print("\n========== LISTORA AI HEALTH CHECK ==========\n")

# 1. Python environment
print("[1] PYTHON ENVIRONMENT")
print("Python:", sys.version.split()[0])
print("Executable:", sys.executable)
print("Virtual environment:", "PASS" if sys.prefix != sys.base_prefix else "FAIL")

# 2. Dependencies
print("\n[2] DEPENDENCIES")
modules = [
    "fastapi",
    "uvicorn",
    "PIL",
    "cv2",
    "rembg",
    "numpy"
]
for module in modules:
    installed = importlib.util.find_spec(module) is not None
    print(f"{module}: {'PASS' if installed else 'FAIL'}")

# 3. Python syntax
print("\n[3] PYTHON SYNTAX")
python_files = list(APP.rglob("*.py"))
failed = []

for file in python_files:
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(file)],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        failed.append(file.relative_to(ROOT))
        
print("Files checked:", len(python_files))
print("Syntax:", "FAIL" if failed else "PASS")

for file in failed:
    print("ERROR:", file)

# 4. Backend health
print("\n[4] BACKEND API")

try:
    with urllib.request.urlopen(
        "http://127.0.0.1:8000/health", timeout=3
    ) as response:
        print("Health endpoint:", "PASS" if response.status == 200 else "FAIL")
except Exception as error:
    print("Health endpoint: NOT RUNNING")

# 5. Git status
print("\n[5] GITHUB / GIT")

def git(*args):
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True
    )

branch = git("branch", "--show-current")
status = git("status", "--short")
remote = git("remote", "get-url", "origin")

print("Branch:", branch.stdout.strip() or "UNKNOWN")
print("GitHub remote:", "PASS" if remote.returncode == 0 else "FAIL")
print("Working tree:", "CLEAN" if not status.stdout.strip() else "CHANGES PENDING")

if status.stdout.strip():
    print(status.stdout.strip())

print("\n========== CHECK COMPLETE ==========\n")
