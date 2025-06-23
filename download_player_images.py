import os
import csv
import json
import requests
import urllib.parse

DEFAULT_IMG = "https://ui-avatars.com/api/?name={name}&background=232a34&color=3a86ff&size=64"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def safe_filename(name):
    return "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name).replace(' ', '_')

def get_wikipedia_image(player_name):
    title = player_name.replace(' ', '_')
    url = (
        "https://en.wikipedia.org/w/api.php"
        "?action=query"
        "&prop=pageimages"
        "&format=json"
        "&pithumbsize=500"
        f"&titles={urllib.parse.quote(title)}"
    )
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            if "thumbnail" in page and "source" in page["thumbnail"]:
                return page["thumbnail"]["source"]
    except Exception as e:
        print(f"Failed to fetch Wikipedia image for {player_name}: {e}")
    return None

def download_image(url, path):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                f.write(r.content)
            return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
    return False

def main():
    images_dir = "images"
    os.makedirs(images_dir, exist_ok=True)

    player_set = set()
    with open("player_data.csv", newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            player_set.add(row['Player Name'])

    mapping = {}
    total = len(player_set)
    missing = []

    for idx, player in enumerate(sorted(player_set)):
        filename = safe_filename(player) + ".jpg"
        local_path = os.path.join(images_dir, filename)

        # Use local image if it exists and is non-empty
        if os.path.exists(local_path) and os.path.getsize(local_path) > 1024:
            print(f"[{idx+1}/{total}] {player}: ✅ already exists, skipping")
            mapping[player] = f"images/{filename}"
            continue

        img_url = get_wikipedia_image(player)
        source = "Wikipedia"
        if img_url:
            success = download_image(img_url, local_path)
            if success:
                print(f"[{idx+1}/{total}] {player}: ✅ from {source}")
                mapping[player] = f"images/{filename}"
                continue

        # If Wikipedia failed, use avatar URL directly in mapping (do not download)
        avatar_url = DEFAULT_IMG.format(name=urllib.parse.quote(player))
        print(f"[{idx+1}/{total}] {player}: Using avatar URL")
        mapping[player] = avatar_url

    with open("player_images.json", "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Done! {total} player images processed.")
    print("Saved to 'images/' and mapping saved to 'player_images.json'.")
    if missing:
        print(f"\n⚠️ The following players have missing images: {', '.join(missing)}")

if __name__ == "__main__":
    main()
