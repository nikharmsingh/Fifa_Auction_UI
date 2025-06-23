import csv
import requests
import time
import json

def get_futbin_id(player_name):
    # FUTBIN search endpoint (returns JSON)
    url = f"https://www.futbin.com/search?year=24&term={player_name.replace(' ', '%20')}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data and isinstance(data, list):
                # Return the first result's ID
                return data[0]['id']
    except Exception as e:
        print(f"Error fetching FUTBIN ID for {player_name}: {e}")
    return None

def main():
    player_set = set()
    with open("player_data.csv", newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            player_set.add(row['Player Name'])

    futbin_ids = {}
    for idx, player in enumerate(sorted(player_set)):
        futbin_id = get_futbin_id(player)
        if futbin_id:
            futbin_ids[player] = futbin_id
            print(f"[{idx+1}/{len(player_set)}] {player}: {futbin_id}")
        else:
            print(f"[{idx+1}/{len(player_set)}] {player}: NOT FOUND")
        time.sleep(1.5)  # Be polite to FUTBIN, avoid getting blocked

    with open("futbin_ids.json", "w", encoding="utf-8") as f:
        json.dump(futbin_ids, f, indent=2, ensure_ascii=False)

    print("Done! Mapping saved to futbin_ids.json.")

if __name__ == "__main__":
    main()