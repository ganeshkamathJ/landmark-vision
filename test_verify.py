"""
Automated test: landmark search image check + non-landmark rejection.
"""
import requests, re, sys

BASE = "http://127.0.0.1:5000"
PASS = "PASS"
FAIL = "FAIL"
results = []

def check(label, cond, detail=""):
    icon = PASS if cond else FAIL
    msg = f"{icon}  {label}"
    if detail:
        msg += f"\n     {detail}"
    results.append((cond, msg))
    print(msg)

# ── 1. Text search: Ellora Caves ────────────────────────────────────────────
resp = requests.get(f"{BASE}/search", params={"q": "Ellora Caves"}, allow_redirects=True)
check("Search 'Ellora Caves' returns 200", resp.status_code == 200,
      f"status={resp.status_code} url={resp.url}")

m = re.search(r'<img[^>]+id="result-img"[^>]+src="([^"]+)"', resp.text)
if not m:
    m = re.search(r'src="([^"]+)"[^>]+id="result-img"', resp.text)
img_src = m.group(1) if m else "(not found)"
is_real_img = img_src and "placeholder" not in img_src and img_src != "(not found)"
check("Ellora Caves result has a real image (not placeholder)", is_real_img,
      f"img src = {img_src}")

# ── 2. Text search: Colosseum ───────────────────────────────────────────────
resp2 = requests.get(f"{BASE}/search", params={"q": "Colosseum"}, allow_redirects=True)
check("Search 'Colosseum' returns 200", resp2.status_code == 200)

m2 = re.search(r'<img[^>]+id="result-img"[^>]+src="([^"]+)"', resp2.text)
if not m2:
    m2 = re.search(r'src="([^"]+)"[^>]+id="result-img"', resp2.text)
img_src2 = m2.group(1) if m2 else "(not found)"
is_real_img2 = img_src2 and "placeholder" not in img_src2 and img_src2 != "(not found)"
check("Colosseum result has a real image (not placeholder)", is_real_img2,
      f"img src = {img_src2}")

# ── 3. Non-landmark: "hello" should redirect back to index with warning ─────
resp3 = requests.get(f"{BASE}/search", params={"q": "hello"}, allow_redirects=True)
went_back_to_index = ("Landmark Vision" in resp3.text and "/search" not in resp3.url)
has_warning = "does not appear to be a geographical landmark" in resp3.text
check("Non-landmark 'hello' redirects back to home", went_back_to_index,
      f"url={resp3.url}")
check("Non-landmark 'hello' shows warning flash", has_warning)

# ── 4. Non-landmark: "pizza" ─────────────────────────────────────────────────
resp4 = requests.get(f"{BASE}/search", params={"q": "pizza"}, allow_redirects=True)
went_back4 = ("Landmark Vision" in resp4.text and "/search" not in resp4.url)
check("Non-landmark 'pizza' redirects back to home", went_back4,
      f"url={resp4.url}")

# ── Summary ──────────────────────────────────────────────────────────────────
print()
passed = sum(1 for ok, _ in results if ok)
total  = len(results)
print(f"{'='*50}")
print(f"  {passed}/{total} checks passed")
print(f"{'='*50}")
sys.exit(0 if passed == total else 1)
