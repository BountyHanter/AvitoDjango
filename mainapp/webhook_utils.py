# mainapp/webhook_utils.py
import logging
import threading
import re
from .models import AvitoAccount, AvitoIgnoredChat
from .python_scripts.avito.create_timer import update_or_create_timer, add_to_ignored_chats
from .python_scripts.avito.gpt.main_gpt import init_process_gpt
from .python_scripts.avito.messages.insert_message_in_db import insert_message_in_database
from .python_scripts.avito.globals import timers, trigger_timers, message_collections
from .python_scripts.avito.telegram.send_to_manager import send_telegram_message


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


def check_phone_number(content):
    """Проверяет наличие 9 и более цифр подряд в сообщении."""
    return bool(re.search(r'\d{9,}', content))


def check_triggers(content, triggers):
    """Проверяет наличие триггеров в сообщении."""
    for trigger in triggers.split('/'):
        if trigger.lower() in content.lower():
            logging.debug('Чат будет добавлен в игнорируемые, так как сработал триггер по слову')
            return True
    return False


def should_ignore_chat(user_id, chat_id, content):
    """Проверяет, сообщение на триггеры и номер телефона."""
    try:
        account = AvitoAccount.objects.get(user_id=user_id)
        if account.check_phone and check_phone_number(content):
            if chat_id in trigger_timers:
                logging.debug(f'Отмена существующего триггерного таймера для чата {chat_id} (номер телефона)')
                trigger_timers[chat_id].cancel()

            logging.debug(f'Создание триггерного таймера для чата {chat_id} на {account.time_to_trigger} секунд (номер телефона)')
            trigger_timer = threading.Timer(account.time_to_trigger, add_to_ignored_chats, [chat_id, user_id, True, True])
            trigger_timers[chat_id] = trigger_timer
            trigger_timer.start()
            logging.debug(f'Чат {chat_id} будет добавлен в игнорируемые через {account.time_to_trigger} секунд, так как найден номер телефона')
            timers[chat_id].cancel()
            logging.debug(f'Отмена существующего таймера игнорирования для чата {chat_id} так как сработал триггер')
        elif account.triggers and check_triggers(content, account.triggers):
            if chat_id in trigger_timers:
                logging.debug(f'Отмена существующего триггерного таймера для чата {chat_id} (триггеры)')
                trigger_timers[chat_id].cancel()

            logging.debug(f'Создание триггерного таймера для чата {chat_id} на {account.time_to_trigger} секунд (триггеры)')
            trigger_timer = threading.Timer(account.time_to_trigger, add_to_ignored_chats, [chat_id, user_id, True, True])
            trigger_timers[chat_id] = trigger_timer
            trigger_timer.start()
            logging.debug(f'Чат {chat_id} будет добавлен в игнорируемые через {account.time_to_trigger} секунд, так как сработал триггер')
            timers[chat_id].cancel()
            logging.debug(f'Отмена существующего таймера игнорирования для чата {chat_id} так как сработал триггер')
    except AvitoAccount.DoesNotExist:
        logging.error(f'Account with user_id {user_id} does not exist.')




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
            logging.debug('Время в базе данных не найдено, по умолчанию 60 секунд')
            wait_time = 60  # Время ожидания по умолчанию, если не найдено в базе данных

        # Запускаем новый таймер
        timer = threading.Timer(wait_time, process_collected_messages, args=[chat_id, user_id, author_id])
        timers[chat_id] = timer
        timer.start()


def process_collected_messages(chat_id, user_id, author_id):

    # Получаем все собранные сообщения для данного chat_id
    content = message_collections.pop(chat_id, None)
    if content:
        logging.debug(f'Начало обработки сообщений для чата {chat_id}')
        update_or_create_timer(chat_id, user_id)
        insert_message_in_database(chat_id, sender_id=author_id, content=content)
        should_ignore_chat(user_id, chat_id, content)
        init_process_gpt(user_id, chat_id, content)

    # Удаляем таймер после обработки
    if chat_id in timers:
        logging.debug(f'Удаление таймера для чата {chat_id} после обработки')
        timers.pop(chat_id, None)
