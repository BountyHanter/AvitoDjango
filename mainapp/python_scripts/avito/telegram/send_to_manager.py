from time import sleep

import requests

from mainapp.python_scripts.avito.messages.get_tg_manager import get_tg_manager
from mainapp.python_scripts.avito.telegram.create_message import generate_message_text
from mainapp.python_scripts.avito.telegram.split_message import split_message


def send_telegram_message(chat_id, author_id):
    tg_manager = get_tg_manager(author_id)

    if tg_manager is None:
        print(f"No tg_manager found for author_id {author_id}")
        return

    token = '7069682876:AAFSpj-SHqEBECrzsd1916gCSwYp0gJBKrU'

    message_text = generate_message_text(chat_id, author_id)
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
            print("Сообщение успешно отправлено менеджеру!")
            sleep(1)
        else:
            print('Ошибка при отправке сообщения:', response.status_code, response.text)
