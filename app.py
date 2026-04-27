import os
import re
import subprocess
from flask import Flask, render_template, request, Response, stream_with_context, send_from_directory
from werkzeug.utils import secure_filename

from marin import response as marin_response

app = Flask(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static/generated', exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ── Emoji → spoken word map ───────────────────────────────────────────────────
EMOJI_TO_WORD = {
    '💕': '', '💖': '', '💗': '', '💓': '', '💞': '', '💘': '',
    '❤': '', '🧡': '', '💛': '', '💚': '', '💙': '', '💜': '',
    '♡': '', '♥': '',
    '😊': '', '🥰': '', '😍': '', '😘': 'Ummaah',
    '😭': '', '😢': '', '😤': 'Huuhh', '😠': '',
    '✨': '', '🌸': '', '🌺': '', '🌹': '',
    '😂': 'haahahaa', '🤣': 'ahaahaha',
    '👉': '', '👈': '', '💪': '',
}

EMOJI_RE = re.compile(
    "[" +
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0000FE00-\U0000FE0F"
    "\U000024C2-\U0001F251"
    "♡♥❤💕💖💗💓💞💘"
    "]+",
    flags=re.UNICODE
)


def clean_for_tts(text: str) -> str:
    """Replace known emojis with spoken words, strip the rest, clean up."""
    # Replace known emojis with spoken words first
    for emoji, word in EMOJI_TO_WORD.items():
        text = text.replace(emoji, f" {word} " if word else " ")
    # Strip remaining emojis
    text = EMOJI_RE.sub(' ', text)
    # Remove *actions*
    text = re.sub(r'\*.*?\*', '', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ── TTS ───────────────────────────────────────────────────────────────────────
def speak(text, vibe="lovely"):
    clean_text = clean_for_tts(text)
    if not clean_text:
        return
    with open("input.txt", "w", encoding="utf-8") as f:
        f.write(clean_text)
    if vibe == "angry":
        voice, speed = "af_sarah:80,af_sky:20", "0.9"
    else:
        voice, speed = "af_bella", "0.90"
    subprocess.Popen(["kokoro-tts", "input.txt", "--stream", "--voice", voice, "--speed", speed])


def play_intro():
    try:
        if os.path.exists("intro.txt"):
            subprocess.Popen(["kokoro-tts", "intro.txt", "--stream", "--voice", "af_bella", "--speed", "1.02"])
        else:
            print("[Warning] intro.txt not found. Skipping intro TTS.")
    except Exception as e:
        print(f"[Error] Failed to play intro TTS: {e}")


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat')
def chat_page():
    play_intro()
    return render_template('chat.html')


@app.route('/upload', methods=['POST'])
def upload():
    """Handle image uploads from the chat UI."""
    if 'image' not in request.files:
        return 'No file', 400
    file = request.files['image']
    if file.filename == '':
        return 'No filename', 400
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return 'OK', 200


@app.route('/message', methods=['POST'])
def message():
    user_input = request.form.get('message', '').strip()

    def generate():
        full_reply = ""
        vibe = "lovely"

        for piece in marin_response(user_input):
            if piece.startswith("__VIBE__"):
                vibe = piece.replace("__VIBE__", "").strip()
                speak(full_reply, vibe)
                yield f"__VIBE__{vibe}\n"
            elif piece.startswith("__GENERATED_IMAGE__:"):
                # Pass image path to frontend
                yield piece + "\n"
            else:
                full_reply += piece
                yield piece

    return Response(stream_with_context(generate()), mimetype="text/plain")


if __name__ == '__main__':
    app.run(debug=True, port=5069)
