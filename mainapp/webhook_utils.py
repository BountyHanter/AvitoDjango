# mainapp/webhook_utils.py
import logging
import threading
import re
from .models import AvitoAccount, AvitoIgnoredChat
from .python_scripts.avito.check_triggers import check_trigger_user_message
from .python_scripts.avito.create_timer import update_or_create_timer, add_to_ignored_chats
from .python_scripts.avito.gpt.main_gpt import init_process_gpt
from .python_scripts.avito.messages.insert_message_in_db import insert_message_in_database
from .python_scripts.avito.globals import timers, trigger_timers, message_collections, shutdown_timers
from .python_scripts.avito.user_notification import user_notification


def parse_webhook_payload(payload):
    """Парсит полезную нагрузку вебхука и извлекает нужные данные."""
    value = payload.get('payload', {}).get('value', {})
    user_id = value.get('user_id')
    author_id = value.get('author_id')
    chat_id = value.get('chat_id')
    content = value.get('content', {}).get('text', '')  # Извлечение текста сообщения
    return user_id, author_id, chat_id, content


def should_ignore_webhook(user_id, author_id):
    """Проверяет, нужно ли игнорировать вебхук на основе user_id и author_id."""
    if user_id == author_id or (author_id is not None and 0 <= author_id <= 10):
        logging.debug("Webhook игнорируется так как он от аккаунта/системы")
        return True
    return False

def process_webhook(user_id, author_id, chat_id, content):
    """Обрабатывает вебхук: проверка на игнорирование и сбор сообщений."""
    if should_ignore_webhook(user_id, author_id):
        return
    if AvitoIgnoredChat.objects.filter(chat_id=chat_id).exists():
        logging.debug(f'Чат {chat_id} игнорируется.')
        return
    collect_messages(chat_id, user_id, author_id, content)


def collect_messages(chat_id, user_id, author_id, content):

    # Инициализируем коллекцию сообщений, если она не существует
    if chat_id not in message_collections:
        message_collections[chat_id] = ""

    # Добавляем сообщение в коллекцию
    message_collections[chat_id] += content + "\n"

    # Если таймер для этого чата еще не существует, создаем его
    if chat_id not in timers:
        try:
            logging.debug(user_id)
            wait_time = AvitoAccount.objects.get(user_id=user_id).wait_time
        except AvitoAccount.DoesNotExist:
            logging.debug('Время в базе данных не найдено, отменяем')
            return
        # Запускаем новый таймер
        timer = threading.Timer(wait_time, process_collected_messages, args=[chat_id, user_id, author_id])
        timers[chat_id] = timer
        timer.start()


def process_collected_messages(chat_id, user_id, author_id):
    # Получаем все собранные сообщения для данного chat_id
    content = message_collections.pop(chat_id, None)
    if content:
        logging.debug(f'Начало обработки сообщений для чата {chat_id}')
        # if AvitoAccount.objects.get(user_id=user_id).time_to_shutdown:
        #     update_or_create_timer(chat_id, user_id)
        insert_message_in_database(chat_id, sender_id=author_id, content=content)
        init_process_gpt(user_id, chat_id, content)
        user_notification(user_id, chat_id)
        check_trigger_user_message(user_id, chat_id, content)

    # Удаляем таймер после обработки
    timers.pop(chat_id, None)


