import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_APP_ID = os.getenv("API_APP_ID")
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")
ACCOUNT_ID = os.getenv("ACCOUNT_ID")
CLIENT_FOLDER_ID = os.getenv("CLIENT_FOLDER_ID")

url = f"https://app.icontact.com/icp/a/{ACCOUNT_ID}/c/{CLIENT_FOLDER_ID}"

# Required headers
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Api-Version": "2.2",
    "Api-AppId": API_APP_ID,
    "Api-Username": API_USERNAME,
    "Api-Password": API_PASSWORD,
}

response = requests.get(url, headers=headers)
print("Status:", response.status_code)
print("Response:", response.json())
