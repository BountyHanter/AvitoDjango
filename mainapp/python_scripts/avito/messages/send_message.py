import requests

from asgiref.sync import sync_to_async


from mainapp.python_scripts.avito.authorization import take_access_token_from_avito
from mainapp.python_scripts.avito.load_access_token import load_access_token
from mainapp.python_scripts.avito.messages.insert_message_in_db import insert_message_in_database
from mainapp.python_scripts.avito.messages.upd_chat_status import update_chat_status


def send_message(*, user_id, message_text, chat_id, upd_status=False):
    access_token = load_access_token(user_id=user_id)
    api_url = f'https://api.avito.ru/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    data = {
        'message': {'text': message_text},
        'type': 'text'
    }
    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()  # Будет вызывать исключение для не 2xx ответов
        insert_message_in_database(chat_id, user_id, message_text)
        if upd_status is True:
            update_chat_status(chat_id)
        print('send_message.py')
        print('Сообщение успешно отправлено:', response.json())
    except requests.exceptions.HTTPError as e:
        if response.status_code == 403:
            print('send_message.py')
            print('Ошибка аутентификации. Попытка получить новый токен...')
            take_access_token_from_avito(user_id=user_id)
            send_message(user_id=user_id, message_text=message_text, chat_id=chat_id)  # Повторная отправка сообщения с новым токеном
        else:
            print('send_message.py')
            print('Ошибка при отправке сообщения:', response.status_code, response.text)

