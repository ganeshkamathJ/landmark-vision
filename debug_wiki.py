import urllib.request, urllib.parse, json

# Try Wikimedia Commons REST search API
ua = {"User-Agent": "Mozilla/5.0 (LandmarkVision/1.0; educational use)"}

# Strategy: search Wikimedia Commons for the landmark name
query = "Ellora Caves"
commons_search_url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srnamespace=6&srsearch={urllib.parse.quote(query)}&format=json&srlimit=5"
req = urllib.request.Request(commons_search_url, headers=ua)
with urllib.request.urlopen(req, timeout=10) as r:
    data = json.loads(r.read())
results = data.get("query", {}).get("search", [])
print("Commons search results:")
for r in results:
    print(" -", r["title"])

if results:
    # Get URL for first image
    file_title = results[0]["title"]
    info_url = f"https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url&titles={urllib.parse.quote(file_title)}&format=json"
    req = urllib.request.Request(info_url, headers=ua)
    with urllib.request.urlopen(req, timeout=10) as r:
        idata = json.loads(r.read())
    ipage = list(idata["query"]["pages"].values())[0]
    img_url = ipage.get("imageinfo", [{}])[0].get("url", "(none)")
    print("Image URL:", img_url)
