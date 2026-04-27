@echo off
setlocal EnableDelayedExpansion
title Marin AI — Setup
color 0D

echo.
echo  =======================================
echo    Marin AI ^— Automatic Setup
echo    Windows Installer
echo  =======================================
echo.

:: ── Step 1: Check Python ──────────────────────────────────────────────────────
echo [1/6] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Python not found. Installing via winget...
    winget install --id Python.Python.3.11 -e --silent
    :: Refresh PATH
    call refreshenv >nul 2>&1
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo  ERROR: Python install failed.
        echo  Please install manually: https://python.org/downloads
        pause & exit /b 1
    )
)
for /f "tokens=*" %%i in ('python --version') do echo  Found: %%i

:: ── Step 2: pip packages ──────────────────────────────────────────────────────
echo.
echo [2/6] Installing Python packages...
python -m pip install --upgrade pip --quiet
python -m pip install flask werkzeug requests ollama python-dotenv google-generativeai
if %errorlevel% neq 0 (
    echo  ERROR: pip install failed. Check your internet connection.
    pause & exit /b 1
)
echo  Done.

:: ── Step 3: ffmpeg ────────────────────────────────────────────────────────────
echo.
echo [3/6] Installing ffmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% equ 0 (
    echo  ffmpeg already installed — skipping.
) else (
    winget install --id Gyan.FFmpeg -e --silent
    if %errorlevel% neq 0 (
        echo  WARNING: ffmpeg winget install failed.
        echo  Download manually: https://ffmpeg.org/download.html
        echo  Extract and add bin\ folder to PATH.
    ) else (
        echo  Done.
    )
)

:: ── Step 4: Ollama ────────────────────────────────────────────────────────────
echo.
echo [4/6] Installing Ollama...
ollama --version >nul 2>&1
if %errorlevel% equ 0 (
    echo  Ollama already installed — skipping.
) else (
    winget install --id Ollama.Ollama -e --silent
    if %errorlevel% neq 0 (
        echo  WARNING: Ollama winget failed.
        echo  Download manually: https://ollama.com/download
    ) else (
        echo  Done.
    )
)

:: Start ollama service then pull models
echo  Pulling AI models (this takes a while — grab a coffee)...
start /b ollama serve >nul 2>&1
timeout /t 2 /nobreak >nul
ollama pull llama3.2
ollama pull moondream

:: ── Step 5: Gemini API Key ────────────────────────────────────────────────────
echo.
echo [5/6] Setting up Gemini API Key...
echo.

:: Check if .env already has the key
if exist .env (
    findstr /i "GEMINI_API_KEY" .env >nul 2>&1
    if %errorlevel% equ 0 (
        echo  Gemini API key already set in .env — skipping.
        goto :skip_key
    )
)

echo  Get your free key at: https://aistudio.google.com/app/apikey
echo  (Press Enter to skip — app works with local Ollama only)
echo.
set /p GEMINI_KEY="  Enter GEMINI_API_KEY: "

if not "!GEMINI_KEY!"=="" (
    :: Save to .env file
    echo # Marin AI - API Keys >> .env
    echo GEMINI_API_KEY=!GEMINI_KEY! >> .env
    echo  Saved to .env

    :: Also set as Windows user environment variable (survives reboot)
    setx GEMINI_API_KEY "!GEMINI_KEY!" >nul
    echo  Added to Windows environment variables
) else (
    echo  Skipped.
)

:skip_key

:: ── Step 6: Protect .env from git ────────────────────────────────────────────
echo.
echo [6/6] Protecting .env from git...
if exist .gitignore (
    findstr /i ".env" .gitignore >nul 2>&1
    if %errorlevel% neq 0 (
        echo. >> .gitignore
        echo # API Keys >> .gitignore
        echo .env >> .gitignore
        echo  Added .env to .gitignore
    ) else (
        echo  .env already in .gitignore — skipping.
    )
) else (
    echo # API Keys > .gitignore
    echo .env >> .gitignore
    echo  Created .gitignore
)

:: ── Done ──────────────────────────────────────────────────────────────────────
echo.
echo  =======================================
echo    Setup Complete!
echo    Run: python app.py
echo    Then open: http://localhost:5000
echo  =======================================
echo.
pause
