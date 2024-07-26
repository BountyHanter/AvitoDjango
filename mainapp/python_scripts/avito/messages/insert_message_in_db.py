# views.py
import logging
import sys

from mainapp.models import AvitoMessage


def insert_message_in_database(chat_id, sender_id, content):
    try:
        # Вставка сообщения в таблицу messages
        AvitoMessage.objects.create(
            chat_id=chat_id,
            sender_id=sender_id,
            content=content
        )
        #logging.debug(f'Сообщение для чата {chat_id} успешно добавлено.')
        sys.stdout.flush()
    except Exception as e:
        logging.debug(f'Ошибка при работе с базой данных: {e}')
        sys.stdout.flush()
