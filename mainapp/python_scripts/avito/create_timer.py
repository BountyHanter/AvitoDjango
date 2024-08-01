import threading

from mainapp.models import AvitoAccount, AvitoIgnoredChat
from mainapp.python_scripts.avito.telegram.send_to_manager import send_telegram_message
from mainapp.python_scripts.avito.globals import trigger_timers, shutdown_timers

import logging


def update_or_create_timer(chat_id, user_id):

    # Получаем время ожидания из модели AvitoAccount
    try:
        if chat_id in trigger_timers:
            logging.debug(f'Отмена существующего триггерного таймера для чата {chat_id}')
            trigger_timers[chat_id].cancel()
            trigger_timers.pop(chat_id, None)

        avito_account = AvitoAccount.objects.get(user_id=user_id)
        wait_time = avito_account.time_to_shutdown
        should_ping_manager = avito_account.should_ping_manager

    except AvitoAccount.DoesNotExist:
        logging.error(f'Аккаунт с user_id {user_id} не найден, установка времени ожидания по умолчанию.')
        wait_time = 5  # 5 минут
        should_ping_manager = False

    # Если таймер уже существует, отмените его
    if chat_id in shutdown_timers:
        logging.debug(f'Отмена существующего таймера для чата {chat_id}')
        shutdown_timers[chat_id].cancel()
        shutdown_timers.pop(chat_id, None)

    # Создаем новый таймер
    logging.debug(f'Создание нового таймера для чата {chat_id} на {wait_time} минут')
    timer = threading.Timer(wait_time * 60, add_to_ignored_chats, [chat_id, user_id, should_ping_manager, False])
    shutdown_timers[chat_id] = timer
    timer.start()


def add_to_ignored_chats(chat_id, user_id, should_ping_manager, trigger):
    logging.debug("Добавляем в игнорируемые")
    # Добавляем чат в игнор-лист
    AvitoIgnoredChat.objects.get_or_create(chat_id=chat_id)
    logging.debug(f"Чат {chat_id} добавлен в игнорируемые так как клиент не ответил/израсходованы токены/сработал триггер")

    if should_ping_manager:
        send_telegram_message(chat_id, user_id, trigger=trigger)

    # Удаляем таймер после выполнения задачи
    shutdown_timers[chat_id].cancel()
    shutdown_timers.pop(chat_id, None)
