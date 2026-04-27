import os
import json
import base64
import glob
import requests

# ── Config ─────────────────────────────────────────────────────────────────────
API_KEY      = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
VISION_MODEL = "gemini-2.5-flash"        # vision + analysis
IMAGE_MODEL  = "gemini-3.1-flash-image-preview"  # image generation

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "leo_history.json")

CHARACTER = """You are Leonardo Da Vinci — the Renaissance genius.
You see hidden geometry, divine proportion, and deeper meaning in everything.
Speak dramatically, find patterns and beauty. Be poetic but brief."""

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{VISION_MODEL}:generateContent?key={API_KEY}"
GEMINI_IMG_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{IMAGE_MODEL}:generateContent?key={API_KEY}"


def _encode_image(image_path: str) -> dict:
    """Convert image file to base64 for Gemini API."""
    ext = os.path.splitext(image_path)[1].lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".png": "image/png", ".webp": "image/webp"}
    mime = mime_map.get(ext, "image/jpeg")
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return {"inline_data": {"mime_type": mime, "data": data}}


def response(prompt: str, image_path=None):
    """
    Generator — yields text chunks.
    image_path: full path to image file to analyze (optional)
    """
    # ── Load history ──────────────────────────────────────────────────────────
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except:
            history = []

    # ── Build contents list ───────────────────────────────────────────────────
    contents = []

    # Add history
    for msg in history:
        contents.append({
            "role": msg["role"],
            "parts": [{"text": msg["content"]}]
        })

    # Build current user message
    parts = [{"text": prompt}]
    if image_path and os.path.exists(image_path):
        print(f"[Leo] Analyzing: {os.path.basename(image_path)}")
        parts.append(_encode_image(image_path))
    elif image_path:
        print(f"[Leo] Image not found at: {image_path}")

    contents.append({"role": "user", "parts": parts})

    payload = {
        "system_instruction": {"parts": [{"text": CHARACTER}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 512}
    }

    # ── Call Gemini API ───────────────────────────────────────────────────────
    reply = ""
    print("\n[Leo] Contemplating...\n")
    try:
        resp = requests.post(GEMINI_URL, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        reply = data["candidates"][0]["content"]["parts"][0]["text"]
        # Yield in chunks to keep streaming feel
        chunk_size = 20
        for i in range(0, len(reply), chunk_size):
            yield reply[i:i+chunk_size]
    except Exception as e:
        print(f"\n[Leo] Error: {e}")
        yield f"[Error: {e}]"
        return

    # ── Save history ──────────────────────────────────────────────────────────
    history.append({"role": "user",      "content": prompt})
    history.append({"role": "assistant", "content": reply})
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[-20:], f, ensure_ascii=False, indent=4)


def generate_image(prompt: str, save_path: str = None) -> str:
    """
    Generate an image from a text prompt using Gemini 2.5 Flash Image.
    Returns the path to the saved image.
    """
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]}
    }

    try:
        resp = requests.post(GEMINI_IMG_URL, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        for part in data["candidates"][0]["content"]["parts"]:
            if "inline_data" in part:
                img_data = base64.b64decode(part["inline_data"]["data"])
                if not save_path:
                    save_path = os.path.join(BASE_DIR, "generated_image.png")
                with open(save_path, "wb") as f:
                    f.write(img_data)
                print(f"[Leo] Image generated: {save_path}")
                return save_path
    except Exception as e:
        print(f"[Leo] Image generation error: {e}")
        return None


# ── Standalone test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    image_files = (glob.glob(os.path.join(BASE_DIR, "*.jpg"))  +
                   glob.glob(os.path.join(BASE_DIR, "*.jpeg")) +
                   glob.glob(os.path.join(BASE_DIR, "*.png"))  +
                   glob.glob(os.path.join(BASE_DIR, "*.webp")))

    latest_image = max(image_files, key=os.path.getctime) if image_files else None

    if not latest_image:
        print("[Leo] No image found — put a .jpg/.jpeg/.png next to image.py")
    else:
        print(f"[Leo] Found: {latest_image}")

    prompt = "This is a safe general image. Describe only what you literally see. Be brief and poetic."
    for piece in response(prompt, image_path=latest_image):
        print(piece, end="", flush=True)
    print("\n")
