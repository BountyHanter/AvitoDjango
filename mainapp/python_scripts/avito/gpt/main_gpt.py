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

# Директория для хранения JSON-файлов
USER_DATA_DIR = os.path.join(settings.MEDIA_ROOT, 'user_data')


# Убедитесь, что директория существует
os.makedirs(USER_DATA_DIR, exist_ok=True)


def init_process_gpt(user_id, chat_id, message):
    assistant_key = take_assistant_key(user_id)
    if not assistant_key:
        print(f"Ошибка: assistant_key для user_id {user_id} не найден.")
        return

    access_token = load_access_token(user_id=user_id)
    print("Сообщение клиента - ", message)
    thread_file_path = os.path.join(USER_DATA_DIR, f'thread_{chat_id}.json')

    if not os.path.exists(thread_file_path):
        create_chat_in_database(chat_id=chat_id, user_id=user_id, access_token=access_token)
        thread, run, message = gpt.create_thread_and_run(user_input=message, id_assistant=assistant_key)
        save_thread_to_file(thread, thread_file_path)
        run_result = gpt.wait_on_run(run, thread)
        gpt_answer = gpt.pretty_print2(thread, message)
        send_message(user_id=user_id, message_text=gpt_answer, chat_id=chat_id, upd_status=True)
    else:
        thread = take_thread_from_file(thread_file_path)
        run, gpt_message = gpt.submit_message(assistant_key, thread, message)
        run_result = gpt.wait_on_run(run, thread)
        gpt_answer = gpt.pretty_print2(thread, gpt_message)
        send_message(user_id=user_id, message_text=gpt_answer, chat_id=chat_id, upd_status=True)


def create_chat_in_database(chat_id, user_id, access_token):
    # Получение информации о чате
    user_pic, user_name = get_chat_info(user_id=user_id, chat_id=chat_id, access_token=access_token)

    try:
        # Создаем новую запись в таблице chats
        AvitoChat.objects.create(
            chat_id=chat_id,
            user_id=user_id,
            chat_name=user_name,
            user_pic=user_pic
        )
        print(f'Чат с chat_id {chat_id} успешно создан.')
    except IntegrityError:
        print(f'Ошибка: Чат с chat_id {chat_id} уже существует.')
    except Exception as e:
        print(f'Ошибка при работе с базой данных: {e}')


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
        print(f'user_id {user_id} не найден в avito_accounts.')
        assistant_key = None
    except Exception as e:
        print(f'Ошибка при работе с базой данных: {e}')
        assistant_key = None

    return assistant_key
