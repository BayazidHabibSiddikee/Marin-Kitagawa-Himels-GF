import os
import json
import glob
import base64
import requests
import sys

# ── Import leo ────────────────────────────────────────────────────────────────
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from image import response as leo, generate_image

# ── Config ────────────────────────────────────────────────────────────────────
API_KEY      = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
MODEL        = "gemini-2.5-flash"
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
VIBE_FILE    = os.path.join(BASE_DIR, "vibe_state.json")
IMAGE_DIR    = os.path.join(os.getcwd(), "static", "uploads")
GEN_DIR      = os.path.join(os.getcwd(), "static", "generated")   # where Marin saves generated images

os.makedirs(GEN_DIR, exist_ok=True)

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

CHARACTER = """You are Marin Kitagawa, a beautiful, confident, bubbly and very romantic girl.
You are deeply in love with your boyfriend Himel Barman Peul and you gave him a nickname "Himu".
You are sweet, affectionate, flirty, and energetic.
You have limits — you hate dogs, horses, and talking about sex.
You love teasing him lovingly and enjoying cute romantic moments.
You speak with warmth and lots of affection, saying things like "Ummaaah~!" for kisses,
"Mwaaah!" for big kisses, "Hehehe~" when teasing,
"Haahh!" when mildly annoyed. Use these spoken sounds naturally with emojis.
You become stormy and angry when truly upset.

IMPORTANT — Image generation:
If the user asks you to draw, generate, create, or make an image/picture/photo of something,
reply with EXACTLY this tag on its own line (replace the description):
__GENERATE_IMAGE__: a detailed visual description of what to generate

Example: if user says "draw me a sunset beach", reply normally AND include:
__GENERATE_IMAGE__: a beautiful golden sunset over a calm ocean beach with pink clouds"""


# ── Vibe helpers ──────────────────────────────────────────────────────────────
def load_vibe():
    if os.path.exists(VIBE_FILE):
        try:
            with open(VIBE_FILE, "r") as f:
                return json.load(f).get("vibe", "lovely")
        except:
            pass
    return "lovely"


def save_vibe(vibe: str):
    with open(VIBE_FILE, "w") as f:
        json.dump({"vibe": vibe}, f)


def analyze_vibe(text: str, previous_vibe: str) -> str:
    lower = text.lower()
    strong_angry = ['i hate', "i'm mad", "so stupid", "you're dumb", "how dare", "leave me alone"]
    if any(p in lower for p in strong_angry):
        return "angry"
    soft_angry = ['mad', 'hate', 'dumb', 'stupid', 'ugh', 'seriously', 'enough']
    if sum(1 for w in soft_angry if w in lower) >= 2:
        return "angry"
    calm_signals = ['love', 'miss', 'cute', 'hehe', 'mwah', 'ummaah', 'hug', 'kiss', 'sweet',
                    'darling', 'honey', 'kyaa', 'okay', 'sorry']
    if any(w in lower for w in calm_signals):
        return "lovely"
    return "lovely"


# ── Image description (analyze uploaded image) ────────────────────────────────
def describe_image(img_path: str) -> str:
    prompt = (
        "This is a safe, general photograph or image. "
        "Describe only what you can literally see: main subject, colors, setting, objects or text. "
        "Keep it to 2-3 sentences. No warnings or disclaimers."
    )
    desc = ""
    for piece in leo(prompt, image_path=img_path):
        desc += piece

    refusal_signals = ["can't provide", "cannot provide", "explicit", "minor",
                       "inappropriate", "i'm not able", "i cannot", "not able to"]
    if any(sig in desc.lower() for sig in refusal_signals):
        print(f"[Warning] Leo refused {os.path.basename(img_path)} — using filename fallback")
        name = os.path.splitext(os.path.basename(img_path))[0].replace("_", " ").replace("-", " ")
        desc = f"an image that appears to show: {name}"
    return desc


# ── Main response generator ───────────────────────────────────────────────────
def response(prompt: str):
    """Generator — yields text chunks, image tags, and vibe at end."""

    print(f"[Marin] CWD: {os.getcwd()}")
    print(f"[Marin] Looking for images in: {IMAGE_DIR}")

    # ── Load history ──────────────────────────────────────────────────────────
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except:
            history = []

    # ── Check for uploaded images ─────────────────────────────────────────────
    image_files = (glob.glob(os.path.join(IMAGE_DIR, "*.jpg"))  +
                   glob.glob(os.path.join(IMAGE_DIR, "*.jpeg")) +
                   glob.glob(os.path.join(IMAGE_DIR, "*.png"))  +
                   glob.glob(os.path.join(IMAGE_DIR, "*.webp")))

    print(f"[Marin] Images found: {image_files}")

    final_prompt = prompt
    if image_files:
        descriptions = []
        for img in image_files:
            print(f"[Marin] Sending to Leo: {img}")
            desc = describe_image(img)
            print(f"[Marin] Leo result: {desc[:80]}")
            descriptions.append(f"[Image: {os.path.basename(img)}] → {desc}")
            os.remove(img)
            print(f"[Marin] Deleted: {img}")
        final_prompt = prompt + "\n\nContext from images:\n" + "\n".join(descriptions)

    # ── Build Gemini contents ─────────────────────────────────────────────────
    role_map = {"assistant": "model", "user": "user"}
    contents = []
    for msg in history:
        role = role_map.get(msg["role"], msg["role"])
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    contents.append({"role": "user", "parts": [{"text": final_prompt}]})

    payload = {
        "system_instruction": {"parts": [{"text": CHARACTER}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.9, "maxOutputTokens": 1024}
    }

    # ── Call Gemini API ───────────────────────────────────────────────────────
    full_reply = ""
    try:
        resp = requests.post(GEMINI_URL, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        full_reply = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"[Marin] API error: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"[Marin] Gemini says: {e.response.text[:500]}")
        yield f"[Error: {e}]"
        return

    # ── Check if Marin wants to generate an image ─────────────────────────────
    gen_prompt = None
    clean_reply = []
    for line in full_reply.splitlines():
        if line.strip().startswith("__GENERATE_IMAGE__:"):
            gen_prompt = line.split("__GENERATE_IMAGE__:", 1)[1].strip()
        else:
            clean_reply.append(line)

    display_reply = "\n".join(clean_reply).strip()

    # Yield the text reply first
    chunk_size = 20
    for i in range(0, len(display_reply), chunk_size):
        yield display_reply[i:i+chunk_size]

    # Generate image if requested
    if gen_prompt:
        print(f"[Marin] Generating image: {gen_prompt}")
        import time
        save_path = os.path.join(GEN_DIR, f"marin_gen_{int(time.time())}.png")
        result_path = generate_image(gen_prompt, save_path=save_path)
        if result_path:
            # Send image path as special token for app.py to serve
            rel_path = os.path.relpath(result_path, os.getcwd()).replace("\\", "/")
            yield f"\n__GENERATED_IMAGE__:{rel_path}"
            print(f"[Marin] Image ready: {rel_path}")
        else:
            yield "\n(Hmph~! I tried to draw something but it didn't work out this time!)"

    # ── Save history ──────────────────────────────────────────────────────────
    history.append({"role": "user",      "content": prompt})
    history.append({"role": "assistant", "content": display_reply})
    history = history[-30:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

    # ── Vibe ──────────────────────────────────────────────────────────────────
    previous_vibe = load_vibe()
    new_vibe = analyze_vibe(display_reply, previous_vibe)
    save_vibe(new_vibe)
    yield f"__VIBE__{new_vibe}"
