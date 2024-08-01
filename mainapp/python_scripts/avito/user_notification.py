import asyncio
import threading

from mainapp.models import AvitoAccount, AvitoChat
from mainapp.python_scripts.avito.create_timer import update_or_create_timer
from mainapp.python_scripts.avito.globals import user_notifications_timers
from mainapp.python_scripts.avito.messages.send_message import send_message


def user_notification(user_id, chat_id):
    try:
        if chat_id in user_notifications_timers:
            user_notifications_timers[chat_id].cancel()
            user_notifications_timers.pop(chat_id, None)
        account = AvitoAccount.objects.get(user_id=user_id)
        chat = AvitoChat.objects.get(chat_id=chat_id)

        if account.bot_interval and account.bot_text and chat.can_send_reminder is True:
            def send_reminder():
                send_message(user_id=user_id, message_text=account.bot_text, chat_id=chat_id, upd_status=True)
                chat.can_send_reminder = False
                if account.time_to_shutdown:
                    update_or_create_timer(chat_id, user_id)

            timer = threading.Timer(account.bot_interval, send_reminder)
            user_notifications_timers[chat_id] = timer
            timer.start()
        elif account.time_to_shutdown:
            update_or_create_timer(chat_id, user_id)
    except AvitoAccount.DoesNotExist:
        print(f"AvitoAccount с user_id {user_id} не существует.")
    except AvitoChat.DoesNotExist:
        print(f"AvitoChat с id {chat_id} не существует.")
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
