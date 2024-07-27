import logging
import os
import json

from django.conf import settings
from django.db import IntegrityError

from mainapp.models import AvitoAccount, AvitoChat

from . import gpt_api as gpt
from mainapp.python_scripts.avito.check_client_info import get_chat_info
from mainapp.python_scripts.avito.load_access_token import load_access_token
from mainapp.python_scripts.avito.messages.send_message import send_message
from .gpt_api import serialize_thread
from ..create_timer import add_to_ignored_chats
from ..telegram.send_to_manager import send_telegram_message_about_trigger

# Директория для хранения JSON-файлов
USER_DATA_DIR = os.path.join(settings.MEDIA_ROOT, 'user_data')


# Убедитесь, что директория существует
os.makedirs(USER_DATA_DIR, exist_ok=True)


def init_process_gpt(user_id, chat_id, message):
    try:
        chat = AvitoChat.objects.get(chat_id=chat_id)  # Попытка получить объект AvitoChat
        if int(chat.tokens) == 0:  # Если у чата закончились токены
            logging.debug(f"Чат {chat_id} израсходовал токены")
            add_to_ignored_chats(chat_id, user_id, False, False)
            send_telegram_message_about_trigger(chat_id, user_id)
            return
    except AvitoChat.DoesNotExist:
        # Если объект не существует, создаем его с начальным количеством токенов
        pass
    assistant_key = take_assistant_key(user_id)
    if not assistant_key:
        logging.debug(f"Ошибка: assistant_key для user_id {user_id} не найден.")
        return

    access_token = load_access_token(user_id=user_id)
    logging.debug(f"Сообщение клиента - {message}")
    thread_file_path = os.path.join(USER_DATA_DIR, f'thread_{chat_id}.json')

    if not os.path.exists(thread_file_path):
        title = create_chat_in_database(chat_id=chat_id, user_id=user_id, access_token=access_token)
        thread, run, message = gpt.create_thread_and_run(user_input=f'Сообщение в объявлении {title}, {message}', id_assistant=assistant_key)
        save_thread_to_file(thread, thread_file_path)
        run_result = gpt.wait_on_run(run, thread)
        gpt_answer = gpt.pretty_print2(thread, message)
        send_message(user_id=user_id, message_text=gpt_answer, chat_id=chat_id, upd_status=True)
    else:
        thread = take_thread_from_file(thread_file_path)
        run, gpt_message = gpt.submit_message(assistant_key, thread, message)
        run_result = gpt.wait_on_run(run, thread)
        try:
            spent_tokens = int(run_result.usage.total_tokens)

            current_tokens = int(chat.tokens)  # Текущие токены
            new_current_tokens = current_tokens - spent_tokens  # Вычисляем новое значение токенов

            if new_current_tokens <= 0:
                new_current_tokens = 0

            chat.tokens = new_current_tokens  # Обновляем значение токенов
            chat.save()  # Сохраняем изменения
        except AttributeError as e:
            logging.debug(f"init_process_gpt Ошибка атрибута: {e}")
        except TypeError as e:
            logging.debug(f"init_process_gpt Ошибка типа: {e}")
        except AvitoChat.DoesNotExist as e:
            logging.debug(f"init_process_gpt Ошибка: объект AvitoChat не найден: {e}")
        except Exception as e:
            logging.debug(f"init_process_gpt Неизвестная ошибка: {e}")

        gpt_answer = gpt.pretty_print2(thread, gpt_message)
        send_message(user_id=user_id, message_text=gpt_answer, chat_id=chat_id, upd_status=True)


def create_chat_in_database(chat_id, user_id, access_token):
    # Получение информации о чате
    user_pic, user_name, title = get_chat_info(user_id=user_id, chat_id=chat_id, access_token=access_token)

    try:
        # Создаем новую запись в таблице chats
        AvitoChat.objects.create(
            chat_id=chat_id,
            user_id=user_id,
            chat_name=user_name,
            user_pic=user_pic
        )
        logging.debug(f'Чат с chat_id {chat_id} успешно создан.')
        return title
    except IntegrityError:
        logging.debug(f'Ошибка: Чат с chat_id {chat_id} уже существует.')
    except Exception as e:
        logging.debug(f'Ошибка при работе с базой данных: {e}')

    return 'Без названия'


def save_thread_to_file(thread, filename):
    thread_data = serialize_thread(thread)
    with open(filename, 'w') as f:
        f.write(json.dumps(thread_data, indent=4))


def take_thread_from_file(filename):
    with open(filename, 'r') as f:
        content = f.read()
        thread_data = json.loads(content)
    thread = gpt.deserialize_thread(thread_data)
    return thread


def take_assistant_key(user_id):
    try:
        # Извлекаем assistant_key по user_id
        account = AvitoAccount.objects.get(user_id=user_id)
        assistant_key = account.assistant_key
    except AvitoAccount.DoesNotExist:
        logging.debug(f'user_id {user_id} не найден в avito_accounts.')
        assistant_key = None
    except Exception as e:
        logging.debug(f'Ошибка при работе с базой данных: {e}')
        assistant_key = None

    return assistant_key
