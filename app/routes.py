"""
Flask route definitions for Landmark Vision.
"""
import os
import uuid
import logging
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, current_app,
    jsonify, send_from_directory,
)
from app import predictor as pred_module
from app.landmark_info import get_landmark

main     = Blueprint("main", __name__)
logger   = logging.getLogger(__name__)


def _allowed_file(filename: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


# ── Serve uploaded images ─────────────────────────────────────────────────────
@main.route("/uploads/<path:filename>")
def uploaded_file(filename):
    # Security: prevent path traversal
    if "/" in filename or "\\" in filename or ".." in filename:
        from flask import abort
        abort(400)
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


# ── Pages ─────────────────────────────────────────────────────────────────────
@main.route("/")
def index():
    from app.db import get_recent_history
    hf_set = bool(current_app.config.get("HUGGINGFACE_TOKEN"))
    recent_predictions = get_recent_history(limit=6)
    return render_template("index.html", hf_active=hf_set, history=recent_predictions)


@main.route("/about")
def about():
    return render_template("about.html")


# ── Build merged info dict ────────────────────────────────────────────────────
def _build_info(result: dict) -> dict:
    """
    Merge prediction result with our landmark metadata dict.
    If the landmark isn't in our local list (e.g. returned by an API),
    use the API's own description/city/country fields.
    """
    key  = result.get("class_name", "unknown")
    info = dict(get_landmark(key))          # copy so we can mutate

    # Supplement with API-provided fields if our local entry is generic
    if info["name"] == "Unknown Landmark":
        info["name"]        = result.get("display_name") or key.replace("_", " ").title()
        info["city"]        = result.get("city")        or info["city"]
        info["country"]     = result.get("country")     or info["country"]
        info["year_built"]  = result.get("year_built")  or info["year_built"]
        info["category"]    = result.get("category")    or info["category"]
        info["description"] = result.get("description") or info["description"]
        info["flag"]        = "🌍"

    # Extra fields from APIs
    info["latitude"]  = result.get("latitude") or info.get("latitude")
    info["longitude"] = result.get("longitude") or info.get("longitude")
    info["source"]    = result.get("source", "demo")

    # If BLIP gave us a caption, keep it
    if result.get("caption"):
        info["caption"] = result["caption"]

    return info


def _normalize_wikimedia_url(url: str) -> str:
    """Convert Wikimedia thumbnail URLs to original image URLs to bypass CDN size rules."""
    # Strip query params before processing to avoid corrupted URLs
    clean_url = url.split("?")[0] if "?" in url else url
    if "upload.wikimedia.org" in clean_url and "/thumb/" in clean_url:
        parts = clean_url.split("/")
        try:
            parts.remove("thumb")
            parts.pop()
            return "/".join(parts)
        except (ValueError, IndexError):
            pass
    return url


# ── Predict ───────────────────────────────────────────────────────────────────
@main.route("/predict", methods=["POST"])
def predict():
    image_url = request.form.get("image_url", "").strip()
    image_url = _normalize_wikimedia_url(image_url)
    save_path = None
    unique_name = None

    if image_url:
        try:
            import urllib.request
            import urllib.parse
            # Extract extension or default to jpg
            parsed_url = urllib.parse.urlparse(image_url)
            path = parsed_url.path
            ext = path.rsplit(".", 1)[-1].lower() if "." in path else "jpg"
            if ext not in current_app.config["ALLOWED_EXTENSIONS"]:
                ext = "jpg"
            unique_name = f"{uuid.uuid4().hex}.{ext}"
            save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)

            if image_url.startswith("file:///"):
                # Decode the URL encoded path (e.g., %20 to spaces)
                local_path = urllib.parse.unquote(image_url[8:])
                # On Windows, local_path may start with a slash (e.g., /C:/...)
                if os.name == 'nt' and (local_path.startswith('/') or local_path.startswith('\\')):
                    local_path = local_path[1:]
                local_path = os.path.normpath(local_path)
                with open(local_path, "rb") as source_file:
                    with open(save_path, "wb") as f:
                        f.write(source_file.read())
            else:
                # Request headers to look like a browser to prevent blocks
                req = urllib.request.Request(
                    image_url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                )
                with urllib.request.urlopen(req, timeout=15) as response:
                    with open(save_path, "wb") as f:
                        f.write(response.read())
        except Exception as exc:
            logger.exception("Failed to download dropped image URL: %s", exc)
            return redirect(url_for("main.index", error="Failed to retrieve the image. Please try saving it locally and uploading it."))
    else:
        if "image" not in request.files:
            return redirect(url_for("main.index", error="No file part in the request."))

        file = request.files["image"]

        if file.filename == "":
            return redirect(url_for("main.index", error="No file selected."))

        if not _allowed_file(file.filename):
            return redirect(url_for("main.index", error="Unsupported file type. Please upload PNG, JPG, JPEG, or WEBP."))

        ext         = file.filename.rsplit(".", 1)[-1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        save_path   = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
        file.save(save_path)

    try:
        result = pred_module.predict(
            image_path        = save_path,
            model_path        = current_app.config["MODEL_PATH"],
            image_size        = current_app.config["IMAGE_SIZE"],
            threshold         = current_app.config["CONFIDENCE_THRESHOLD"],
            huggingface_token = current_app.config.get("HUGGINGFACE_TOKEN", ""),
            google_api_key    = current_app.config.get("GOOGLE_VISION_API_KEY", ""),
            openai_api_key    = current_app.config.get("OPENAI_API_KEY", ""),
        )
    except Exception as exc:
        logger.exception("Prediction failed: %s", exc)
        return redirect(url_for("main.index", error="Prediction failed — please try a different image."))

    info = _build_info(result)

    # Fetch landmark reference image from Wikipedia
    landmark_ref_image = ""
    try:
        wiki = _search_wikipedia(info.get("name", ""))
        if wiki:
            landmark_ref_image = wiki.get("image_url", "")
            # Also update coordinates if not already set from prediction
            if not info.get("latitude") and wiki.get("latitude"):
                info["latitude"]  = wiki["latitude"]
                info["longitude"] = wiki["longitude"]
    except Exception as wiki_exc:
        logger.warning("Could not fetch Wikipedia reference image: %s", wiki_exc)

    # Log to history database (include the served URL so history cards show the image)
    try:
        from app.db import add_history_entry
        add_history_entry(
            info=info,
            image_filename=unique_name,
            image_url=url_for('main.uploaded_file', filename=unique_name),
            confidence=result["confidence"],
            source=result.get("source", "demo")
        )
    except Exception as db_exc:
        logger.exception("Failed to write prediction to history DB: %s", db_exc)

    return render_template(
        "result.html",
        info                = info,
        confidence          = result["confidence"],
        demo_mode           = result["demo_mode"],
        source              = result.get("source", "demo"),
        image_filename      = unique_name,
        image_url           = url_for('main.uploaded_file', filename=unique_name),
        landmark_ref_image  = landmark_ref_image,
    )


def _fetch_wiki_image_fallback(title: str) -> str:
    """Try multiple Wikipedia/Wikimedia strategies to get an image URL for a page title."""
    import urllib.request, urllib.parse, json
    ua = {"User-Agent": "Mozilla/5.0 (LandmarkVision/1.0; educational use)"}

    # Strategy 1: piprop=thumbnail with large pxwidth
    try:
        url = (
            "https://en.wikipedia.org/w/api.php?action=query&prop=pageimages"
            f"&piprop=thumbnail&pithumbsize=800&titles={urllib.parse.quote(title)}&format=json"
        )
        req = urllib.request.Request(url, headers=ua)
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read())
        pages = data.get("query", {}).get("pages", {})
        page = list(pages.values())[0]
        thumb = page.get("thumbnail", {}).get("source", "")
        if thumb:
            # Upgrade thumbnail to larger size
            thumb = thumb.replace("/80px-", "/800px-").replace("/200px-", "/800px-")
            return thumb
    except Exception:
        pass

    # Strategy 2: Wikimedia Commons via pageimages with pageid lookup
    try:
        url = (
            "https://en.wikipedia.org/w/api.php?action=query&prop=pageimages"
            f"&piprop=name&titles={urllib.parse.quote(title)}&format=json"
        )
        req = urllib.request.Request(url, headers=ua)
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read())
        pages = data.get("query", {}).get("pages", {})
        page = list(pages.values())[0]
        image_name = page.get("pageimage", "")
        if image_name:
            # Build Wikimedia Commons direct URL
            commons_url = (
                "https://en.wikipedia.org/w/api.php?action=query&prop=imageinfo"
                f"&iiprop=url&titles=File:{urllib.parse.quote(image_name)}&format=json"
            )
            req2 = urllib.request.Request(commons_url, headers=ua)
            with urllib.request.urlopen(req2, timeout=8) as r2:
                data2 = json.loads(r2.read())
            pages2 = data2.get("query", {}).get("pages", {})
            page2 = list(pages2.values())[0]
            img_url = page2.get("imageinfo", [{}])[0].get("url", "")
            if img_url:
                return img_url
    except Exception:
        pass

    return ""


def _fetch_wikimedia_commons_image(query: str) -> str:
    """Search Wikimedia Commons directly for a landmark image."""
    import urllib.request, urllib.parse, json
    ua = {"User-Agent": "Mozilla/5.0 (LandmarkVision/1.0; educational use)"}
    try:
        search_url = (
            f"https://commons.wikimedia.org/w/api.php?action=query&list=search"
            f"&srnamespace=6&srsearch={urllib.parse.quote(query)}&format=json&srlimit=5"
        )
        req = urllib.request.Request(search_url, headers=ua)
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        results = data.get("query", {}).get("search", [])
        if not results:
            return ""
        file_title = results[0]["title"]
        info_url = (
            f"https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo"
            f"&iiprop=url&titles={urllib.parse.quote(file_title)}&format=json"
        )
        req2 = urllib.request.Request(info_url, headers=ua)
        with urllib.request.urlopen(req2, timeout=10) as r2:
            idata = json.loads(r2.read())
        ipage = list(idata["query"]["pages"].values())[0]
        return ipage.get("imageinfo", [{}])[0].get("url", "")
    except Exception:
        return ""


def _search_wikipedia(query: str) -> dict | None:
    """Search Wikipedia API for a landmark summary and main image URL."""
    try:
        import urllib.request
        import urllib.parse
        import json

        # Step 1: Search Wikipedia for best page match
        search_url = (
            "https://en.wikipedia.org/w/api.php?action=query&list=search"
            f"&srsearch={urllib.parse.quote(query)}&format=json&utf8=1"
        )
        req = urllib.request.Request(
            search_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            search_data = json.loads(response.read())
        
        search_results = search_data.get("query", {}).get("search", [])
        if not search_results:
            return None
        
        # Best match page title
        title = search_results[0]["title"]

        # Step 2: Query page details (extract + original image + coordinates)
        detail_url = (
            "https://en.wikipedia.org/w/api.php?action=query&prop=extracts|pageimages|coordinates"
            f"&exintro=1&explaintext=1&piprop=original&titles={urllib.parse.quote(title)}&format=json"
        )
        req = urllib.request.Request(
            detail_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            detail_data = json.loads(response.read())
        
        pages = detail_data.get("query", {}).get("pages", {})
        if not pages:
            return None
        
        page_id = list(pages.keys())[0]
        page_info = pages[page_id]

        if "missing" in page_info:
            return None

        summary = page_info.get("extract", "")
        if len(summary) > 400:
            summary = summary[:400].rsplit(".", 1)[0] + "."

        # Primary: original full-size image
        img_url = page_info.get("original", {}).get("source", "")

        # Fallback 1: try thumbnail / Commons page image strategies
        if not img_url:
            img_url = _fetch_wiki_image_fallback(title)

        # Fallback 2: search Wikimedia Commons directly by query
        if not img_url:
            img_url = _fetch_wikimedia_commons_image(query)

        # Extract coordinates
        lat = lng = None
        coords_list = page_info.get("coordinates", [])
        if coords_list:
            lat = coords_list[0].get("lat")
            lng = coords_list[0].get("lon")
        
        return {
            "title": title,
            "summary": summary,
            "image_url": img_url,
            "latitude": lat,
            "longitude": lng
        }
    except Exception as e:
        logger.error("Wikipedia search failed: %s", e)
        return None


@main.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return redirect(url_for("main.index", error="Please enter a landmark to search."))

    # Try to match our local database for facts
    from app.landmark_info import LANDMARK_INFO, get_landmark
    matched_key = "unknown"
    query_lower = query.lower()
    for key, info in LANDMARK_INFO.items():
        if (query_lower in info["name"].lower() or 
            query_lower in info["city"].lower() or 
            query_lower in key):
            matched_key = key
            break

    local_info = dict(get_landmark(matched_key))

    wiki_result = _search_wikipedia(query)
    
    # Verify that the term is either a local landmark or has geographical coordinates on Wikipedia
    is_valid = (matched_key != "unknown") or (
        wiki_result and wiki_result.get("latitude") is not None and wiki_result.get("longitude") is not None
    )

    if not is_valid:
        error_msg = f"'{query}' does not appear to be a geographical landmark or historical site. Please try searching for a famous monument, building, or city (e.g., Taj Mahal, Colosseum)."
        return redirect(url_for("main.index", error=error_msg))

    # Build response info dict — wiki_result may be None if matched locally but has no Wikipedia page
    wiki_title   = wiki_result["title"]   if wiki_result else (local_info.get("name") or query)
    wiki_summary = wiki_result["summary"] if wiki_result else ""
    wiki_img     = wiki_result["image_url"] if wiki_result else ""
    wiki_lat     = wiki_result.get("latitude")  if wiki_result else None
    wiki_lng     = wiki_result.get("longitude") if wiki_result else None

    info = {
        "name": wiki_title,
        "city": local_info["city"] if matched_key != "unknown" else "Various / Global",
        "country": local_info["country"] if matched_key != "unknown" else "Global",
        "year_built": local_info["year_built"] if matched_key != "unknown" else "—",
        "category": local_info["category"] if matched_key != "unknown" else "Historic Site / Landmark",
        "description": wiki_summary or local_info["description"],
        "flag": local_info["flag"] if matched_key != "unknown" else "🌍",
        "source": "wikipedia_search",
        "image_url": wiki_img,
        "latitude": wiki_lat or local_info.get("latitude"),
        "longitude": wiki_lng or local_info.get("longitude")
    }

    # Log to history database
    try:
        from app.db import add_history_entry
        add_history_entry(
            info=info,
            image_filename=None,
            image_url=wiki_img,
            confidence=100.0,
            source="wikipedia_search"
        )
    except Exception as db_exc:
        logger.exception("Failed to write search to history DB: %s", db_exc)

    return render_template(
        "result.html",
        info                = info,
        confidence          = 100.0,
        demo_mode           = False,
        source              = "wikipedia_search",
        image_url           = wiki_img,
        image_filename      = None,
        landmark_ref_image  = wiki_img,
    )


# ── JSON API ──────────────────────────────────────────────────────────────────
@main.route("/api/predict", methods=["POST"])
def api_predict():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files["image"]
    if not _allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    ext         = file.filename.rsplit(".", 1)[-1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    save_path   = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
    file.save(save_path)

    try:
        result = pred_module.predict(
            image_path        = save_path,
            model_path        = current_app.config["MODEL_PATH"],
            image_size        = current_app.config["IMAGE_SIZE"],
            threshold         = current_app.config["CONFIDENCE_THRESHOLD"],
            huggingface_token = current_app.config.get("HUGGINGFACE_TOKEN", ""),
            google_api_key    = current_app.config.get("GOOGLE_VISION_API_KEY", ""),
            openai_api_key    = current_app.config.get("OPENAI_API_KEY", ""),
        )
        info = _build_info(result)
        return jsonify({**result, **info})
    except Exception as exc:
        logger.exception("API prediction failed: %s", exc)
        return jsonify({"error": str(exc)}), 500


@main.route("/history/<int:entry_id>")
def view_history(entry_id):
    from app.db import get_history_entry
    entry = get_history_entry(entry_id)
    if not entry:
        return redirect(url_for("main.index", error="History entry not found."))
    
    info = {
        "name": entry["name"],
        "city": entry["city"],
        "country": entry["country"],
        "flag": entry["flag"],
        "category": entry["category"],
        "description": entry["description"],
        "year_built": entry["year_built"],
        "latitude": entry["latitude"],
        "longitude": entry["longitude"],
        "source": entry["source"]
    }
    
    return render_template(
        "result.html",
        info           = info,
        confidence     = entry["confidence"],
        demo_mode      = (entry["source"] == "demo"),
        source         = entry["source"],
        image_filename = entry["image_filename"],
        image_url      = entry["image_url"],
        is_historical  = True
    )
