import threading

from mainapp.models import AvitoAccount, AvitoIgnoredChat
from mainapp.python_scripts.avito.telegram.send_to_manager import send_telegram_message
from mainapp.python_scripts.avito.globals import trigger_timers, timers


def update_or_create_timer(chat_id, user_id):

    # Получаем время ожидания из модели AvitoAccount
    try:
        if chat_id in trigger_timers:
            trigger_timers[chat_id].cancel()
        avito_account = AvitoAccount.objects.get(user_id=user_id)
        wait_time = avito_account.time_to_shutdown
        should_ping_manager = avito_account.should_ping_manager

    except AvitoAccount.DoesNotExist:
        # Установим значение по умолчанию, если учетная запись не найдена
        wait_time = 5  # 5 минут

    # Если таймер уже существует, отмените его
    if chat_id in timers:
        timers[chat_id].cancel()

    # Создаем новый таймер
    timer = threading.Timer(wait_time * 60, add_to_ignored_chats, [chat_id, user_id, should_ping_manager])
    timers[chat_id] = timer
    timer.start()


def add_to_ignored_chats(chat_id, user_id, should_ping_manager):
    print("Добавляем в игнорируемые")
    # Добавляем чат в игнор-лист
    AvitoIgnoredChat.objects.get_or_create(chat_id=chat_id)
    print(f"Чат {chat_id} добавлен в игнорируемые так как клиент не ответил/израсходованы токены/сработал триггер")

    if should_ping_manager:
        send_telegram_message(chat_id, user_id, trigger=False)

    # Удаляем таймер после выполнения задачи
    timers.pop(chat_id, None)
