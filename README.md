<div align="center">

# 🌸 Marin Chatbot

**A romantic AI girlfriend chatbot powered by Gemini 2.5 Flash**
*Featuring Marin Kitagawa from My Dress-Up Darling*

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web_App-black?style=flat-square&logo=flask)
![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-AI-orange?style=flat-square&logo=google)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

</div>

---

## ✨ Features

- 💬 **Romantic AI chat** — Marin responds with warmth, teasing, and affection as your virtual girlfriend
- 🔊 **Text-to-Speech** — Powered by Kokoro TTS with two voice modes: *lovely* and *angry*
- 😘 **Expressive sounds** — Marin says "Ummaah~!", "Mwaaah!", "Kyaaa~!" naturally in conversation
- 🖼️ **Image upload & analysis** — Send photos and Marin reacts to them (via Leo / Gemini Vision)
- 🎨 **AI image generation** — Ask Marin to "draw" something and she generates it with Gemini
- 💢 **Vibe detection** — Emotional state detection switches TTS voice between sweet and stormy
- 🧠 **Persistent memory** — Remembers the last 15 exchanges across sessions

---

## 🗂️ Project Structure

```
himels_GF/
├── app.py              # Flask server, TTS, routing
├── marin.py            # Marin's personality, Gemini chat, vibe detection
├── image.py            # Leo (Da Vinci) — image analysis + generation via Gemini
├── static/
│   ├── uploads/        # Temporary image uploads from user
│   └── generated/      # AI-generated images from Marin
├── templates/
│   ├── index.html      # Landing page
│   └── chat.html       # Main chat UI
├── intro.txt           # Intro TTS script (spoken on chat load)
├── input.txt           # TTS input buffer (auto-written)
├── history.json        # Marin's conversation memory
├── leo_history.json    # Leo's image analysis memory
├── vibe_state.json     # Persisted emotional state
├── kokoro-v1.0.onnx    # Kokoro TTS model
└── voices-v1.0.bin     # Kokoro TTS voices
```

---

## ⚙️ Installation

### 1. Clone & install dependencies

```bash
git clone <your-repo-url>
cd himels_GF
pip install flask requests werkzeug
```

### 2. Install Kokoro TTS

```bash
pip install kokoro-tts
# Download required model files
wget https://github.com/nazdridoy/kokoro-tts/releases/download/v1.0.0/kokoro-v1.0.onnx
wget https://github.com/nazdridoy/kokoro-tts/releases/download/v1.0.0/voices-v1.0.bin
```

### 3. Set your Gemini API key

```bash
export GEMINI_API_KEY="your_api_key_here"
```

> Get a free key at [aistudio.google.com](https://aistudio.google.com)

---

## 🚀 Usage

```bash
python app.py
```

Then open your browser to **http://localhost:5069**

---

## 🤖 AI Models Used

| Purpose | Model |
|---|---|
| Marin's chat personality | `gemini-2.5-flash` |
| Image analysis (Leo) | `gemini-2.5-flash` |
| Image generation | `gemini-3.1-flash-image-preview` |

---

## 💬 How It Works

```
You type a message
        ↓
app.py → marin.py (Gemini 2.5 Flash)
        ↓
  (if image uploaded) → image.py → Leo describes it → Marin reacts
  (if "draw me X")   → image.py → generate_image() → shown in chat
        ↓
Marin's reply streams back
        ↓
Vibe detected (lovely / angry) → Kokoro TTS speaks with matching voice
```

---

## 🎭 Marin's Personality

- Calls you **Himel** and is deeply in love with you
- Uses spoken affection sounds: *Ummaah~!*, *Mwaaah!*, *Kyaaa~!*, *Hehehe~*, *Hmph!*
- **Loves:** teasing, romantic moments, cute things
- **Hates:** dogs, horses, and inappropriate topics
- Gets **stormy angry** when truly upset — voice switches to a sharper tone

---

## 📝 License

MIT — do whatever you want with it 💕