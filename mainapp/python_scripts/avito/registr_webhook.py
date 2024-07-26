import logging

import requests


def register_webhook(server_ip, access_token):
    # URL для регистрации webhook
    api_url = 'https://api.avito.ru/messenger/v3/webhook'
    # Ваш URL для получения уведомлений
    webhook_url = f'http://{server_ip}/webhook'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    data = {
        'url': webhook_url,
    }

    response = requests.post(api_url, headers=headers, json=data)

    if response.status_code in (200, 201):
        logging.debug('registr_webhook.py')
        logging.debug(f'Webhook успешно зарегистрирован: {response.json()}')
    else:
        logging.debug('registr_webhook.py')
        logging.debug(f'Ошибка при регистрации webhook: {response.status_code}, {response.text}')
