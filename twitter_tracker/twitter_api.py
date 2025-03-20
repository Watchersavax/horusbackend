import requests
from django.conf import settings

def get_twitter_data():
    token = getattr(settings, "TWITTER_BEARER_TOKEN", None)  # Get token safely

    if not token:
        print("❌ No Twitter Bearer Token Found! Check settings.py")
        return None

    headers = {"Authorization": f"Bearer {token}"}
    url = "https://api.twitter.com/2/users/by/username/horussyndicate"

    response = requests.get(url, headers=headers)

    print("🔴 Request Headers:", headers)  # Debugging output
    print("🟢 Twitter API Response:", response.json())

    return response.json()


