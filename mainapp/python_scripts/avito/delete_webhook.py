import sys
import requests
from .authorization import take_access_token_from_avito


def delete_webhook(client_id, client_secret):
    response, access_token = take_access_token_from_avito(client_id=client_id, client_secret=client_secret, save_token_in_db=False)
    if response != 200:
        print('delete_webhook неудачно')
        print(access_token)
        return
    address = 'http://94.241.173.208:5001/webhook'
    url = "https://api.avito.ru/messenger/v1/webhook/unsubscribe"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "url": address
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print('delete_webhook.py')
        print("Successfully unsubscribed from webhook.")
        print("Response:", response.json())
    else:
        print('delete_webhook.py')
        print(f"Failed to unsubscribe from webhook. Status code: {response.status_code}")
        print("Response:", response.text)