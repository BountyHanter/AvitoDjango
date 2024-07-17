import threading
import time
from collections import defaultdict
from django.utils import timezone

from mainapp.models import AvitoAccount
from mainapp.python_scripts.avito.gpt.main_gpt import init_process_gpt
from mainapp.python_scripts.avito.messages.insert_message_in_db import insert_message_in_database

message_collections = defaultdict(str)
timers = {}


def collect_messages(chat_id, user_id, author_id, content):
    global timers

    # Добавляем сообщение в коллекцию
    message_collections[chat_id] += content + "\n"

    # Если таймер для этого чата еще не существует, создаем его
    if chat_id not in timers:
        # Получаем время ожидания из базы данных
        try:
            wait_time = AvitoAccount.objects.get(user_id=user_id).wait_time
        except AvitoAccount.DoesNotExist:
            wait_time = 1  # Время ожидания по умолчанию, если не найдено в базе данных

        # Запускаем новый таймер
        timer = threading.Timer(wait_time, process_collected_messages, args=[chat_id, user_id, author_id])
        timers[chat_id] = timer
        timer.start()


def process_collected_messages(chat_id, user_id, author_id):
    global message_collections, timers

    # Получаем все собранные сообщения для данного chat_id
    content = message_collections.pop(chat_id, None)
    if content:
        # Вставляем сообщения в базу данных и запускаем обработку
        insert_message_in_database(chat_id, sender_id=author_id, content=content)
        init_process_gpt(user_id, chat_id, content)

    # Удаляем таймер после обработки
    timers.pop(chat_id, None)
