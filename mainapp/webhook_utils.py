# mainapp/webhook_utils.py

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
        print("Webhook ignored due to user_id and author_id match or author_id in range 0-10.")
        return True
    return False


def check_phone_number(content):
    """Проверяет наличие 9 и более цифр подряд в сообщении."""
    return bool(re.search(r'\d{9,}', content))


def check_triggers(content, triggers):
    """Проверяет наличие триггеров в сообщении."""
    print('Триггеры и контент')
    print(triggers, content)
    for trigger in triggers.split('/'):
        if trigger.lower() in content.lower():
            print('Чат будет добавлен в игнорируемые, так как сработал триггер по слову')
            return True
    return False


def should_ignore_chat(user_id, chat_id, content):
    """Проверяет, сообщение на триггеры и номер телефона."""
    try:
        account = AvitoAccount.objects.get(user_id=user_id)
        if account.check_phone and check_phone_number(content):
            AvitoIgnoredChat.objects.get_or_create(chat_id=chat_id)
            print(f'Чат {chat_id} добавлен в игнорируемые, так как найден номер телефона')
            send_telegram_message(chat_id=chat_id, author_id=user_id)
        if account.triggers and check_triggers(content, account.triggers):
            AvitoIgnoredChat.objects.get_or_create(chat_id=chat_id)
            print(f'Чат {chat_id} добавлен в игнорируемые, так как сработал триггер')
            send_telegram_message(chat_id=chat_id, author_id=user_id)
    except AvitoAccount.DoesNotExist:
        print(f'Account with user_id {user_id} does not exist.')
    return False



def process_webhook(user_id, author_id, chat_id, content):
    """Обрабатывает вебхук: проверка на игнорирование и сбор сообщений."""
    if should_ignore_webhook(user_id, author_id):
        return
    if AvitoIgnoredChat.objects.filter(chat_id=chat_id).exists():
        print(f'Чат {chat_id} игнорируется.')
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
            print(user_id)
            wait_time = AvitoAccount.objects.get(user_id=user_id).wait_time
        except AvitoAccount.DoesNotExist:
            print('Время в базе данных не найдено, по умолчанию 60 секунд')
            wait_time = 60  # Время ожидания по умолчанию, если не найдено в базе данных

        # Запускаем новый таймер
        timer = threading.Timer(wait_time, process_collected_messages, args=[chat_id, user_id, author_id])
        timers[chat_id] = timer
        timer.start()


def process_collected_messages(chat_id, user_id, author_id):

    # Получаем все собранные сообщения для данного chat_id
    content = message_collections.pop(chat_id, None)
    if content:
        # Вставляем сообщения в базу данных и запускаем обработку
        insert_message_in_database(chat_id, sender_id=author_id, content=content)
        should_ignore_chat(user_id, chat_id, content)
        init_process_gpt(user_id, chat_id, content)

        # Установим или обновим таймер для данного chat_id
        update_or_create_timer(chat_id, user_id)

    # Удаляем таймер после обработки
    timers.pop(chat_id, None)


def timeout(dd):
    print('Таймер вышел')