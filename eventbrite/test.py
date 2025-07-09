import os

import requests
from dotenv import load_dotenv

load_dotenv()

EVENTBRITE_TOKEN = os.getenv("EVENTBRITE_TOKEN")

url = "https://www.eventbriteapi.com/v3/users/me/"

headers = {"Authorization": f"Bearer {EVENTBRITE_TOKEN}"}

response = requests.get(url, headers=headers)

print("Status:", response.status_code)
try:
    print("Response:", response.json())
except Exception as e:
    print("Raw response:", response.text)
    print("Error parsing JSON:", e)
