import requests
import json

location_items = requests.get(f"http://timeline-backend/timeline/entries.json/?schema=activity.location&limit=100&ordering=-date_on_timeline").json()['results']

with open('/var/www/map/locations.json', 'w') as output_json_file:
    json.dump(location_items, output_json_file)