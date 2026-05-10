import json
import os
from collections import defaultdict

import requests

# Steam application ID is 753
# The 6 at the end is a game-specific context ID for trading cards in the Steam application
INVENTORY_URL = "https://steamcommunity.com/inventory/{}/753/6"
MANUAL_FILEPATH = "steam.json"


def pull_inventory_json():
    steam_id = input("Enter your Steam ID from your profile URL: ").strip()
    url = INVENTORY_URL.format(steam_id)

    # TODO: this probably doesn't work without the user's cookie, etc. unless everything is public
    response = requests.get(url)
    json_data = response.json()

    if 'rgInventory' not in json_data:
        raise ValueError(f"Steam request failed. Try logging into Steam in your browser, "
                         f"saving {url} as '{MANUAL_FILEPATH}', and rerunning.")

    return json_data


def find_duplicates(data):
    # rgInventory now contains amoutns for items, but descriptions are in rgDescriptions
    counts_by_class_instance = defaultdict(int)
    for item in data['rgInventory'].values():
        key = f"{item['classid']}_{item['instanceid']}"
        counts_by_class_instance[key] += int(item.get('amount', 1))

    # returning (count, type, market_name) for the duplicates
    return [(amount, data['rgDescriptions'][k]['type'], data['rgDescriptions'][k]['market_name'])
            for k, amount in counts_by_class_instance.items() if amount > 1 and k in data['rgDescriptions']]


if __name__ == "__main__":
    if os.path.exists(MANUAL_FILEPATH):
        print(f"Using file '{MANUAL_FILEPATH}' instead of pulling from Steam.")
        with open(MANUAL_FILEPATH, "r") as file:
            data = json.loads(file.read())
    else:
        data = pull_inventory_json()

    print("Duplicate items:")
    for count, item_type, market_name in find_duplicates(data):
        print(f"  {count} copies of '{item_type}': '{market_name}'")
