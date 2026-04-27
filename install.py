"""
install.py / setup.exe
Cross-platform installer for Marin AI.
Compiled to setup.exe on Windows via: python build_exe.py
"""
import subprocess
import sys
import os
import platform

def get_os():
    if sys.platform.startswith("win"):  return "windows"
    if "TERMUX_VERSION" in os.environ:  return "android"
    if sys.platform == "darwin":        return "mac"
    return "linux"

OS      = get_os()
BASE    = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
ENV_FILE = os.path.join(BASE, ".env")

def banner(text):
    print(f"\n{'─'*42}")
    print(f"  {text}")
    print(f"{'─'*42}")

def run(cmd, **kw):
    if isinstance(cmd, str):
        subprocess.run(cmd, shell=True, **kw)
    else:
        subprocess.run(cmd, **kw)

# ── 1. pip packages ───────────────────────────────────────────────────────────
banner("1/5 · Python packages")
packages = ["flask", "werkzeug", "requests", "ollama",
            "python-dotenv", "google-generativeai"]
run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "-q"])
run([sys.executable, "-m", "pip", "install"] + packages)

# ── 2. System tools ───────────────────────────────────────────────────────────
banner("2/5 · System tools (ffmpeg + Ollama)")
if OS == "windows":
    run(["winget", "install", "--id", "Gyan.FFmpeg",   "-e", "--silent"])
    run(["winget", "install", "--id", "Ollama.Ollama", "-e", "--silent"])
elif OS == "android":
    run(["pkg", "install", "-y", "ffmpeg", "ollama"])
elif OS == "mac":
    run(["brew", "install", "ffmpeg", "ollama"])
else:  # linux
    if os.path.exists("/usr/bin/dnf"):
        run(["sudo", "dnf", "install", "-y", "ffmpeg"])
    elif os.path.exists("/usr/bin/apt"):
        run(["sudo", "apt", "install", "-y", "ffmpeg"])
    run("curl -fsSL https://ollama.com/install.sh | sh", shell=True)

# kokoro-tts (Linux/Mac/Android only)
if OS != "windows":
    run([sys.executable, "-m", "pip", "install", "kokoro-tts"])

# ── 3. Ollama models ──────────────────────────────────────────────────────────
banner("3/5 · Pulling AI models (may take 10-30 min)")
subprocess.Popen(["ollama", "serve"],
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
import time; time.sleep(2)
run(["ollama", "pull", "llama3.2"])
run(["ollama", "pull", "moondream"])

# ── 4. Gemini API key ─────────────────────────────────────────────────────────
banner("4/5 · Gemini API Key")

existing = {}
if os.path.exists(ENV_FILE):
    with open(ENV_FILE) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                existing[k] = v

if "GEMINI_API_KEY" in existing:
    print("  ✓ Key already saved in .env — skipping.")
else:
    print("  Free key → https://aistudio.google.com/app/apikey")
    print("  (Enter to skip — local Ollama works without it)\n")
    key = input("  GEMINI_API_KEY: ").strip()

    if key:
        existing["GEMINI_API_KEY"] = key
        with open(ENV_FILE, "w") as f:
            f.write("# Marin AI — API Keys\n")
            for k, v in existing.items():
                f.write(f"{k}={v}\n")
        print("  ✓ Saved to .env")

        if OS == "windows":
            subprocess.run(["setx", "GEMINI_API_KEY", key], capture_output=True)
            print("  ✓ Added to Windows environment variables")
        else:
            rc = os.path.join(os.path.expanduser("~"), ".bashrc")
            with open(rc, "a") as f:
                f.write(f"\nexport GEMINI_API_KEY={key}\n")
            print(f"  ✓ Added export to {rc}")
    else:
        print("  Skipped.")

# ── 5. .gitignore ─────────────────────────────────────────────────────────────
banner("5/5 · Protecting .env")
gi = os.path.join(BASE, ".gitignore")
content = open(gi).read() if os.path.exists(gi) else ""
if ".env" not in content:
    with open(gi, "a") as f:
        f.write("\n# API Keys\n.env\n")
    print("  ✓ Added .env to .gitignore")
else:
    print("  ✓ Already protected.")

# ── Done ──────────────────────────────────────────────────────────────────────
print(f"\n{'━'*42}")
print("  ✓ All done!")
print("  Run:  python app.py")
print("  Open: http://localhost:5000")
print(f"{'━'*42}\n")
if OS == "windows":
    input("Press Enter to close...")
