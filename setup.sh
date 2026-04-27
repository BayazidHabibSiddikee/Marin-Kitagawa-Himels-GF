#!/bin/bash
# ── Marin AI — Linux/Android Setup ────────────────────────────────────────────
set -e   # stop on first real error

# Colors
RED='\033[0;31m' GREEN='\033[0;32m' PINK='\033[1;35m'
CYAN='\033[0;36m' RESET='\033[0m' BOLD='\033[1m'

echo -e "${PINK}"
echo " ======================================="
echo "   Marin AI — Automatic Setup"
echo "   Linux / Android Installer"
echo " ======================================="
echo -e "${RESET}"

# ── Detect OS ─────────────────────────────────────────────────────────────────
if [ -n "$TERMUX_VERSION" ]; then
    DISTRO="termux"
elif command -v dnf &>/dev/null; then
    DISTRO="fedora"
elif command -v apt &>/dev/null; then
    DISTRO="debian"
elif command -v pacman &>/dev/null; then
    DISTRO="arch"
else
    DISTRO="unknown"
fi
echo -e " Detected: ${CYAN}$DISTRO${RESET}"

# ── Step 1: System packages ───────────────────────────────────────────────────
echo -e "\n${BOLD}[1/6] Installing system packages...${RESET}"
case $DISTRO in
    fedora)
        sudo dnf install -y python3 python3-pip ffmpeg curl
        ;;
    debian)
        sudo apt update -y
        sudo apt install -y python3 python3-pip ffmpeg curl
        ;;
    arch)
        sudo pacman -Sy --noconfirm python python-pip ffmpeg curl
        ;;
    termux)
        pkg install -y python ffmpeg curl
        ;;
    *)
        echo -e " ${RED}Unknown distro — skipping system packages.${RESET}"
        echo " Install manually: python3 pip ffmpeg curl"
        ;;
esac
echo -e " ${GREEN}Done.${RESET}"

# ── Step 2: pip packages ──────────────────────────────────────────────────────
echo -e "\n${BOLD}[2/6] Installing Python packages...${RESET}"

# Use --break-system-packages if needed (newer Debian/Fedora/Ubuntu)
PIP_FLAGS=""
python3 -m pip install pip --quiet 2>/dev/null || PIP_FLAGS="--break-system-packages"

python3 -m pip install $PIP_FLAGS \
    flask werkzeug requests ollama \
    python-dotenv google-generativeai
echo -e " ${GREEN}Done.${RESET}"

# ── Step 3: kokoro-tts ────────────────────────────────────────────────────────
echo -e "\n${BOLD}[3/6] Installing kokoro-tts...${RESET}"
if command -v kokoro-tts &>/dev/null; then
    echo " Already installed — skipping."
else
    python3 -m pip install $PIP_FLAGS kokoro-tts 2>/dev/null || \
        echo -e " ${RED}kokoro-tts install failed — TTS won't work but chat will.${RESET}"
fi

# ── Step 4: Ollama ────────────────────────────────────────────────────────────
echo -e "\n${BOLD}[4/6] Installing Ollama + pulling models...${RESET}"
if command -v ollama &>/dev/null; then
    echo " Ollama already installed — skipping install."
else
    if [ "$DISTRO" = "termux" ]; then
        pkg install -y ollama
    else
        curl -fsSL https://ollama.com/install.sh | sh
    fi
fi

# Start ollama in background and pull models
ollama serve &>/dev/null &
sleep 2
echo " Pulling llama3.2..."
ollama pull llama3.2
echo " Pulling moondream..."
ollama pull moondream
echo -e " ${GREEN}Done.${RESET}"

# ── Step 5: Gemini API Key ────────────────────────────────────────────────────
echo -e "\n${BOLD}[5/6] Setting up Gemini API Key...${RESET}"

ENV_FILE="$(dirname "$(realpath "$0")")/.env"

# Check if already set
if [ -f "$ENV_FILE" ] && grep -q "GEMINI_API_KEY" "$ENV_FILE"; then
    echo " Gemini key already in .env — skipping."
else
    echo ""
    echo -e " Get your free key at: ${CYAN}https://aistudio.google.com/app/apikey${RESET}"
    echo " (Press Enter to skip — app works with local Ollama only)"
    echo ""
    read -rp "  Enter GEMINI_API_KEY: " GEMINI_KEY

    if [ -n "$GEMINI_KEY" ]; then
        # Save to .env
        echo "# Marin AI - API Keys"   >> "$ENV_FILE"
        echo "GEMINI_API_KEY=$GEMINI_KEY" >> "$ENV_FILE"
        echo -e " ${GREEN}Saved to .env${RESET}"

        # Also add to shell profile so it persists in terminal
        SHELL_RC="$HOME/.bashrc"
        [ -n "$ZSH_VERSION" ] && SHELL_RC="$HOME/.zshrc"
        [ "$DISTRO" = "termux" ] && SHELL_RC="$HOME/.bashrc"

        if ! grep -q "GEMINI_API_KEY" "$SHELL_RC" 2>/dev/null; then
            echo "" >> "$SHELL_RC"
            echo "# Marin AI" >> "$SHELL_RC"
            echo "export GEMINI_API_KEY=$GEMINI_KEY" >> "$SHELL_RC"
            echo -e " ${GREEN}Added export to $SHELL_RC${RESET}"
            echo " Run: source $SHELL_RC  (or restart terminal)"
        fi
    else
        echo " Skipped."
    fi
fi

# ── Step 6: Protect .env ──────────────────────────────────────────────────────
echo -e "\n${BOLD}[6/6] Protecting .env from git...${RESET}"
GITIGNORE="$(dirname "$(realpath "$0")")/.gitignore"

if [ -f "$GITIGNORE" ]; then
    if ! grep -q "\.env" "$GITIGNORE"; then
        echo -e "\n# API Keys\n.env" >> "$GITIGNORE"
        echo " Added .env to .gitignore"
    else
        echo " Already in .gitignore — skipping."
    fi
else
    printf "# API Keys\n.env\n" > "$GITIGNORE"
    echo " Created .gitignore"
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo -e "${PINK}"
echo " ======================================="
echo "   Setup Complete!"
echo "   Run:  python3 app.py"
echo "   Open: http://localhost:5000"
echo " ======================================="
echo -e "${RESET}"
