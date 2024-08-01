import logging
import re
import threading

from mainapp.models import AvitoAccount
from mainapp.python_scripts.avito.create_timer import add_to_ignored_chats
from mainapp.python_scripts.avito.globals import trigger_timers, shutdown_timers, user_notifications_timers


def check_trigger_user_message(user_id, chat_id, content):
    """Проверяет сообщение на триггеры и номер телефона."""
    try:
        account = AvitoAccount.objects.get(user_id=user_id)
        # Проверяем номер телефона
        if account.check_phone and check_phone_number(content):
            if account.time_to_trigger:
                if chat_id in trigger_timers and account.time_to_shutdown:
                    logging.debug(f'Отмена существующего триггерного таймера для чата {chat_id} (номер телефона)')
                    trigger_timers[chat_id].cancel()

                logging.debug(f'Создание триггерного таймера для чата {chat_id} на {account.time_to_trigger} секунд (номер телефона)')
                trigger_timer = threading.Timer(account.time_to_trigger, add_to_ignored_chats, [chat_id, user_id, True, True])
                trigger_timers[chat_id] = trigger_timer
                trigger_timer.start()
                logging.debug(f'Чат {chat_id} будет добавлен в игнорируемые через {account.time_to_trigger} секунд, так как найден номер телефона')
                shutdown_timers[chat_id].cancel()
                user_notifications_timers[chat_id].cancel()
                logging.debug(f'Отмена существующего таймера игнорирования для чата {chat_id} так как сработал триггер')
                logging.debug(f'Отмена существующего таймера напоминания для чата {chat_id} так как сработал триггер')

            else:
                add_to_ignored_chats(chat_id, user_id, True, True)
                logging.debug(f'Чат {chat_id} немедленно добавлен в игнорируемые, так как найден номер телефона и нет времени ожидания')

        # Проверяем триггеры
        elif account.triggers and check_triggers(content, account.triggers):
            if account.time_to_trigger:
                if chat_id in trigger_timers and account.time_to_shutdown:
                    logging.debug(f'Отмена существующего триггерного таймера для чата {chat_id} (триггеры)')
                    trigger_timers[chat_id].cancel()

                logging.debug(f'Создание триггерного таймера для чата {chat_id} на {account.time_to_trigger} секунд (триггеры)')
                trigger_timer = threading.Timer(account.time_to_trigger, add_to_ignored_chats, [chat_id, user_id, True, True])
                trigger_timers[chat_id] = trigger_timer
                trigger_timer.start()
                logging.debug(f'Чат {chat_id} будет добавлен в игнорируемые через {account.time_to_trigger} секунд, так как сработал триггер')
                shutdown_timers[chat_id].cancel()
                user_notifications_timers[chat_id].cancel()
                logging.debug(f'Отмена существующего таймера напоминания для чата {chat_id} так как сработал триггер')
                logging.debug(f'Отмена существующего таймера игнорирования для чата {chat_id} так как сработал триггер')
            else:
                add_to_ignored_chats(chat_id, user_id, True, True)
                shutdown_timers[chat_id].cancel()
                user_notifications_timers[chat_id].cancel()
                logging.debug(f'Отмена существующего таймера игнорирования для чата {chat_id} так как сработал триггер')
                logging.debug(f'Отмена существующего таймера напоминания для чата {chat_id} так как сработал триггер')
                logging.debug(f'Чат {chat_id} немедленно добавлен в игнорируемые, так как сработал триггер и нет времени ожидания')
    except AvitoAccount.DoesNotExist:
        logging.error(f'Account with user_id {user_id} does not exist.')


def check_trigger_gpt_message(user_id, chat_id, content):
    account = AvitoAccount.objects.get(user_id=user_id)
    if account.triggers_ai and check_triggers(content, account.triggers_ai):
        if account.time_to_trigger:
            if chat_id in trigger_timers and account.time_to_shutdown:
                logging.debug(f'Отмена существующего триггерного таймера для чата {chat_id} (триггеры ИИ)')
                trigger_timers[chat_id].cancel()

            logging.debug(f'Создание триггерного таймера для чата {chat_id} на {account.time_to_trigger} секунд (триггеры)')
            trigger_timer = threading.Timer(account.time_to_trigger, add_to_ignored_chats, [chat_id, user_id, True, True])
            trigger_timers[chat_id] = trigger_timer
            trigger_timer.start()
            logging.debug(
                f'Чат {chat_id} будет добавлен в игнорируемые через {account.time_to_trigger} секунд, так как сработал триггер')
            shutdown_timers[chat_id].cancel()
            logging.debug(f'Отмена существующего таймера игнорирования для чата {chat_id} так как сработал триггер')
        else:
            add_to_ignored_chats(chat_id, user_id, True, True)
            logging.debug(
                f'Чат {chat_id} немедленно добавлен в игнорируемые, так как сработал триггер и нет времени ожидания')


def check_triggers(content, triggers):
    """Проверяет наличие триггеров в сообщении."""
    for trigger in triggers.split('/'):
        if trigger.lower() in content.lower():
            logging.debug('Чат будет добавлен в игнорируемые, так как сработал триггер по слову')
            return True
    return False


def check_phone_number(content):
    """Проверяет наличие 9 и более цифр подряд в сообщении."""
    return bool(re.search(r'\d{9,}', content))
