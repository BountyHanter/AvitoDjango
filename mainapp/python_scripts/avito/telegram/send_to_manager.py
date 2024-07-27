import logging
from time import sleep

import requests

from mainapp.models import AvitoAccount, AvitoChat
from mainapp.python_scripts.avito.messages.get_tg_manager import get_tg_manager
from mainapp.python_scripts.avito.telegram.create_message import generate_message_text
from mainapp.python_scripts.avito.telegram.split_message import split_message


def send_telegram_message(chat_id, author_id, trigger):
    tg_manager = get_tg_manager(author_id)

    if tg_manager is None:
        logging.debug(f"No tg_manager found for author_id {author_id}")
        return

    token = '7069682876:AAFSpj-SHqEBECrzsd1916gCSwYp0gJBKrU'

    message_text = generate_message_text(chat_id, author_id, trigger)
    messages = split_message(message_text)

    for message in messages:
        # URL для отправки сообщения
        url = f"https://api.telegram.org/bot{token}/sendMessage"

        # Параметры запроса
        payload = {
            'chat_id': tg_manager,
            'text': message
        }

        # Отправка запроса
        response = requests.post(url, json=payload)

        # Проверка ответа
        if response.status_code == 200:
            logging.debug("Сообщение успешно отправлено менеджеру!")
            sleep(1)
        else:
            logging.debug(f'Ошибка при отправке сообщения: {response.status_code}, {response.text}')


def send_telegram_message_about_trigger(chat_id, user_id):
    token = '7069682876:AAFSpj-SHqEBECrzsd1916gCSwYp0gJBKrU'
    user = AvitoAccount.objects.get(user_id=user_id).name
    chat_name = AvitoChat.objects.get(chat_id=chat_id).chat_name

    # URL для отправки сообщения
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Параметры запроса
    payload = {
        'chat_id': '652982524',
        'text': f"У чата с названием{chat_name},"
                f" в авито закончились токены. Чат в аккаунте с именем {user}"
    }

    # Отправка запроса
    response = requests.post(url, json=payload)

    # Проверка ответа
    if response.status_code == 200:
        logging.debug("Сообщение успешно отправлено администратору!")
    else:
        logging.debug(f'Ошибка при отправке сообщения: {response.status_code}, {response.text}')