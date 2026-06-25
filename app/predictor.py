"""
Landmark Vision — Prediction Engine
====================================
Priority order (first available wins):
  1. Trained Keras model     — model/landmark_model.h5 + TensorFlow
  2. HuggingFace BLIP+CLIP   — FREE: just a free HF account token
  3. Google Cloud Vision API — FREE 1,000/month (needs Cloud account)
  4. OpenAI GPT-4o Vision    — ~$0.01/image
  5. Demo mode               — always works, Pillow+numpy only

.env / environment variables:
    HUGGINGFACE_TOKEN=hf_...          ← get free at huggingface.co/settings/tokens
    GOOGLE_VISION_API_KEY=AIza...     ← Google Cloud Console (1000 free/month)
    OPENAI_API_KEY=sk-...             ← OpenAI platform
"""

import os
import re
import json
import base64
import hashlib
import logging
import time
import urllib.request
import urllib.error
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# ── Cached Keras state ────────────────────────────────────────────────────────
_keras_model  = None
_class_names  = None
_tf_available = None

# ── Demo landmark pool ────────────────────────────────────────────────────────
_DEMO_POOL = [
    "eiffel_tower", "colosseum", "statue_of_liberty", "big_ben",
    "taj_mahal", "great_wall_of_china", "machu_picchu",
    "sydney_opera_house", "sagrada_familia", "acropolis",
    "christ_the_redeemer", "petra", "chichen_itza", "stonehenge",
    "burj_khalifa", "empire_state_building", "pyramids_of_giza",
    "notre_dame", "mount_fuji", "angkor_wat", "golden_gate_bridge",
    "parthenon", "leaning_tower_of_pisa", "niagara_falls",
    "tower_of_london", "buckingham_palace", "louvre", "alhambra",
    "westminster_abbey", "st_peters_basilica", "versailles",
]

# ── Landmark keyword map for BLIP caption matching ────────────────────────────
# Maps keyword fragments → class_name keys in landmark_info.py
_KEYWORD_MAP = {
    "eiffel":          "eiffel_tower",
    "colosseum":       "colosseum",
    "statue of liberty": "statue_of_liberty",
    "liberty":         "statue_of_liberty",
    "big ben":         "big_ben",
    "westminster":     "westminster_abbey",
    "buckingham":      "buckingham_palace",
    "taj mahal":       "taj_mahal",
    "great wall":      "great_wall_of_china",
    "machu picchu":    "machu_picchu",
    "sydney opera":    "sydney_opera_house",
    "opera house":     "sydney_opera_house",
    "sagrada":         "sagrada_familia",
    "acropolis":       "acropolis",
    "parthenon":       "parthenon",
    "christ redeemer": "christ_the_redeemer",
    "corcovado":       "christ_the_redeemer",
    "petra":           "petra",
    "chichen itza":    "chichen_itza",
    "stonehenge":      "stonehenge",
    "burj khalifa":    "burj_khalifa",
    "empire state":    "empire_state_building",
    "pyramid":         "pyramids_of_giza",
    "giza":            "pyramids_of_giza",
    "notre dame":      "notre_dame",
    "notre-dame":      "notre_dame",
    "mount fuji":      "mount_fuji",
    "fuji":            "mount_fuji",
    "angkor":          "angkor_wat",
    "golden gate":     "golden_gate_bridge",
    "leaning tower":   "leaning_tower_of_pisa",
    "pisa":            "leaning_tower_of_pisa",
    "niagara":         "niagara_falls",
    "tower of london": "tower_of_london",
    "louvre":          "louvre",
    "alhambra":        "alhambra",
    "st peter":        "st_peters_basilica",
    "saint peter":     "st_peters_basilica",
    "versailles":      "versailles",
    "colosseo":        "colosseum",
}

# ── CLIP candidate labels (for zero-shot classification) ─────────────────────
_CLIP_LABELS = [
    "the Eiffel Tower in Paris",
    "the Colosseum in Rome",
    "the Statue of Liberty in New York",
    "Big Ben in London",
    "the Taj Mahal in India",
    "the Great Wall of China",
    "Machu Picchu in Peru",
    "the Sydney Opera House",
    "the Sagrada Familia in Barcelona",
    "the Acropolis of Athens",
    "Christ the Redeemer in Brazil",
    "Petra in Jordan",
    "Chichen Itza in Mexico",
    "Stonehenge in England",
    "the Burj Khalifa in Dubai",
    "the Empire State Building in New York",
    "the Pyramids of Giza in Egypt",
    "Notre-Dame Cathedral in Paris",
    "Mount Fuji in Japan",
    "Angkor Wat in Cambodia",
    "the Golden Gate Bridge in San Francisco",
    "the Leaning Tower of Pisa",
    "Niagara Falls",
    "the Tower of London",
    "the Louvre Museum in Paris",
    "the Alhambra Palace in Spain",
    "the Palace of Versailles",
    "Buckingham Palace in London",
    "Westminster Abbey in London",
    "St Peter's Basilica in Vatican",
    "the Parthenon in Athens",
]

# Map CLIP label index → class_name
_CLIP_IDX_TO_KEY = [
    "eiffel_tower", "colosseum", "statue_of_liberty", "big_ben",
    "taj_mahal", "great_wall_of_china", "machu_picchu",
    "sydney_opera_house", "sagrada_familia", "acropolis",
    "christ_the_redeemer", "petra", "chichen_itza", "stonehenge",
    "burj_khalifa", "empire_state_building", "pyramids_of_giza",
    "notre_dame", "mount_fuji", "angkor_wat", "golden_gate_bridge",
    "leaning_tower_of_pisa", "niagara_falls", "tower_of_london",
    "louvre", "alhambra", "versailles", "buckingham_palace",
    "westminster_abbey", "st_peters_basilica", "parthenon",
]


# ═══════════════════════════════════════════════════════════════════════════════
# TIER 1 — Keras / TensorFlow model
# ═══════════════════════════════════════════════════════════════════════════════

def _tf_ok() -> bool:
    global _tf_available
    if _tf_available is None:
        try:
            import tensorflow  # noqa
            _tf_available = True
        except ImportError:
            _tf_available = False
    return _tf_available


def _load_keras_model(model_path: str) -> bool:
    global _keras_model, _class_names
    if _keras_model is not None:
        return True
    if not _tf_ok() or not os.path.exists(model_path):
        return False
    import tensorflow as tf
    logger.info("Loading Keras model …")
    _keras_model = tf.keras.models.load_model(model_path)
    lp = os.path.join(os.path.dirname(model_path), "landmark_labels.txt")
    if os.path.exists(lp):
        with open(lp) as f:
            _class_names = [ln.strip() for ln in f if ln.strip()]
    else:
        _class_names = [f"landmark_{i}" for i in range(_keras_model.output_shape[-1])]
    return True


def _predict_keras(image_path, image_size, threshold):
    import tensorflow as tf
    img  = Image.open(image_path).convert("RGB").resize(image_size, Image.LANCZOS)
    arr  = tf.keras.applications.mobilenet_v2.preprocess_input(
               np.expand_dims(np.array(img, dtype=np.float32), 0))
    p    = _keras_model.predict(arr, verbose=0)
    idx  = int(np.argmax(p[0]))
    conf = float(p[0][idx])
    key  = (_class_names[idx] if _class_names else f"landmark_{idx}") \
               .lower().replace(" ", "_").replace("-", "_")
    if conf < threshold:
        key = "unknown"
    return {"class_name": key, "confidence": round(conf * 100, 1),
            "source": "keras_model", "demo_mode": False}


# ═══════════════════════════════════════════════════════════════════════════════
# TIER 2 — HuggingFace (FREE — sign up at huggingface.co)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Strategy:
#   Use Qwen3-VL-8B-Instruct via the unified Inference Providers router
#   to identify the landmark and output standard JSON metadata.
#
# Get your FREE token: https://huggingface.co/settings/tokens
# Set env var:  HUGGINGFACE_TOKEN=hf_...

def _predict_huggingface(image_path: str, token: str) -> dict | None:
    """
    Query Qwen3-VL-8B-Instruct vision-language model on router.huggingface.co
    to perform precise landmark identification for free.
    """
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        ext  = image_path.rsplit(".", 1)[-1].lower()
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
                "webp": "image/webp", "gif": "image/gif"}.get(ext, "image/jpeg")
        prompt = (
            'Identify the landmark in this image. Reply ONLY with JSON:\n'
            '{"name":"...","city":"...","country":"...","year_built":"...",'
            '"category":"...","description":"2-3 sentences.","latitude":48.8584,"longitude":2.2945,"confidence":0.95}\n'
            'If not a landmark, set name to "Unknown Landmark" and confidence to 0.1, and set coordinates to null.'
        )
        payload = json.dumps({
            "model": "Qwen/Qwen3-VL-8B-Instruct",
            "max_tokens": 400,
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}"}},
            ]}],
        }).encode()

        req = urllib.request.Request(
            "https://router.huggingface.co/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        
        raw = data["choices"][0]["message"]["content"].strip()
        if raw.startswith("```"):
            raw = re.sub(r"```(?:json)?", "", raw).strip(" `\n")
        info = json.loads(raw)
        name = info.get("name", "Unknown Landmark")
        conf = float(info.get("confidence", 0.8))
        key  = name.lower().replace(" ", "_").replace("-", "_").replace("'", "")
        
        # Match against our 31 local classes to get detailed flag, city, country if possible
        from app.landmark_info import LANDMARK_INFO
        matched_key = key
        for lkey in LANDMARK_INFO.keys():
            if lkey in key or key in lkey:
                matched_key = lkey
                break

        return {
            "class_name": matched_key,
            "display_name": name,
            "city": info.get("city", ""),
            "country": info.get("country", ""),
            "year_built": info.get("year_built", "—"),
            "category": info.get("category", "Landmark"),
            "description": info.get("description", ""),
            "latitude": info.get("latitude"),
            "longitude": info.get("longitude"),
            "confidence": round(conf * 100, 1) if conf <= 1 else conf,
            "source": "huggingface_vlm",
            "demo_mode": False
        }
    except Exception as e:
        logger.error("HuggingFace VLM prediction error: %s", e)
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# TIER 3 — Google Cloud Vision API (free 1,000 /month)
# ═══════════════════════════════════════════════════════════════════════════════

def _predict_google_vision(image_path: str, api_key: str) -> dict | None:
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        payload = json.dumps({
            "requests": [{"image": {"content": img_b64},
                          "features": [{"type": "LANDMARK_DETECTION",
                                        "maxResults": 1}]}]
        }).encode()
        req = urllib.request.Request(
            f"https://vision.googleapis.com/v1/images:annotate?key={api_key}",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        anns = data["responses"][0].get("landmarkAnnotations", [])
        if not anns:
            return None
        ann  = anns[0]
        name = ann.get("description", "Unknown Landmark")
        conf = ann.get("score", 0.0)
        locs = ann.get("locations", [])
        lat = lng = None
        if locs:
            ll = locs[0].get("latLng", {})
            lat, lng = ll.get("latitude"), ll.get("longitude")
        key = name.lower().replace(" ", "_").replace("-", "_").replace("'", "")
        logger.info("Google Vision: '%s' (%.1f%%)", name, conf * 100)
        return {"class_name": key, "display_name": name,
                "confidence": round(conf * 100, 1),
                "latitude": lat, "longitude": lng,
                "source": "google_vision", "demo_mode": False}
    except Exception as e:
        logger.error("Google Vision error: %s", e)
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# TIER 4 — OpenAI GPT-4o Vision
# ═══════════════════════════════════════════════════════════════════════════════

def _predict_openai(image_path: str, api_key: str) -> dict | None:
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        ext  = image_path.rsplit(".", 1)[-1].lower()
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
                "webp": "image/webp", "gif": "image/gif"}.get(ext, "image/jpeg")
        prompt = (
            'Identify the landmark. Reply ONLY with JSON: '
            '{"name":"...","city":"...","country":"...","year_built":"...",'
            '"category":"...","description":"2-3 sentences.","latitude":48.8584,"longitude":2.2945,"confidence":0.95}'
            ' If not a landmark set name to "Unknown Landmark" and confidence to 0.1, and set coordinates to null.'
        )
        payload = json.dumps({
            "model": "gpt-4o", "max_tokens": 400,
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url",
                 "image_url": {"url": f"data:{mime};base64,{img_b64}"}},
            ]}],
        }).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {api_key}"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        raw = data["choices"][0]["message"]["content"].strip()
        if raw.startswith("```"):
            raw = re.sub(r"```(?:json)?", "", raw).strip(" `\n")
        info = json.loads(raw)
        name = info.get("name", "Unknown Landmark")
        conf = float(info.get("confidence", 0.8))
        key  = name.lower().replace(" ", "_").replace("-", "_").replace("'", "")
        return {"class_name": key, "display_name": name,
                "city": info.get("city", ""), "country": info.get("country", ""),
                "year_built": info.get("year_built", "—"),
                "category": info.get("category", "Landmark"),
                "description": info.get("description", ""),
                "latitude": info.get("latitude"),
                "longitude": info.get("longitude"),
                "confidence": round(conf * 100, 1),
                "source": "openai_vision", "demo_mode": False}
    except Exception as e:
        logger.error("OpenAI Vision error: %s", e)
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# TIER 5 — Demo mode (no APIs, no TF, always works)
# ═══════════════════════════════════════════════════════════════════════════════

def _predict_demo(image_path: str) -> dict:
    img    = Image.open(image_path).convert("RGB").resize((64, 64))
    means  = np.array(img, dtype=np.float32).mean(axis=(0, 1))
    digest = hashlib.md5(means.tobytes()).hexdigest()
    idx    = int(digest[:4], 16) % len(_DEMO_POOL)
    conf   = 72.0 + (int(digest[4:6], 16) % 23)
    return {"class_name": _DEMO_POOL[idx], "confidence": conf,
            "source": "demo", "demo_mode": True}


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

def predict(
    image_path: str,
    model_path: str,
    image_size: tuple,
    threshold: float,
    huggingface_token: str = "",
    google_api_key:    str = "",
    openai_api_key:    str = "",
) -> dict:
    """
    Classify a landmark image using the best available engine.
    Falls through the tier chain automatically.
    """

    # ── Tier 1: Keras model ──────────────────────────────────────────────────
    if _load_keras_model(model_path):
        try:
            return _predict_keras(image_path, image_size, threshold)
        except Exception as e:
            logger.error("Keras failed: %s", e)

    # ── Tier 2: HuggingFace (FREE) ───────────────────────────────────────────
    if huggingface_token:
        result = _predict_huggingface(image_path, huggingface_token)
        if result:
            return result
        logger.warning("HuggingFace returned no result, trying next tier.")
    else:
        logger.info("No HUGGINGFACE_TOKEN set. "
                    "Get a FREE token at: https://huggingface.co/settings/tokens")

    # ── Tier 3: Google Vision ────────────────────────────────────────────────
    if google_api_key:
        result = _predict_google_vision(image_path, google_api_key)
        if result:
            return result

    # ── Tier 4: OpenAI ───────────────────────────────────────────────────────
    if openai_api_key:
        result = _predict_openai(image_path, openai_api_key)
        if result:
            return result

    # ── Tier 5: Demo ─────────────────────────────────────────────────────────
    return _predict_demo(image_path)
