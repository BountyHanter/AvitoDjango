import logging
import time
from openai import OpenAI
import openai
from openai.types.beta.thread import ToolResources, Thread

client = OpenAI(api_key='sk-proj-N9hPV0Qx5fMc1RAtQuijT3BlbkFJen7kN799hqZBvul8wCjT')


# Отправляю сообщение
def submit_message(assistant_id, thread, user_message):
    # 1.1 Создаём сообщение
    message = client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    # 1.2 Создаём запуск
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    ), message


# Получаю ответ
def get_response(thread):
    # 4. Получаем список сообщений
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")


# Создаю поток и запускаю
def create_thread_and_run(user_input, id_assistant):
    # 1. Создаём тред
    thread = client.beta.threads.create()
    # 2. получаем Run
    run, message = submit_message(id_assistant, thread, user_input)
    return thread, run, message


def pretty_print(messages):
    # 5. Мягкий вывод
    logging.debug("# Messages")
    for m in messages:
        logging.debug(f"{m.role}: {m.content[0].text.value}")
        if m.role == 'assistant':
            return m.content[0].text.value


def pretty_print2(thread, message):
    messages = client.beta.threads.messages.list(
        thread_id=thread.id, order="asc", after=message.id
    )
    for m in messages:
        logging.debug(f"{m.role}: {m.content[0].text.value}")
        return m.content[0].text.value


# Waiting in a loop
def wait_on_run(run, thread):
    # 3. Ждём когда сформируется сообщение
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


def serialize_thread(thread):
    if isinstance(thread, openai.types.beta.thread.Thread):
        # Преобразуем объект Thread в словарь
        return {
            'id': thread.id,
            'created_at': thread.created_at,
            'metadata': thread.metadata,
            'object': thread.object,
            'tool_resources': {
                'code_interpreter': thread.tool_resources.code_interpreter,
                'file_search': thread.tool_resources.file_search
            }
        }
    else:
        raise TypeError("Object of type Thread is expected")


def deserialize_thread(data):
    tool_resources = ToolResources(
        code_interpreter=data['tool_resources']['code_interpreter'],
        file_search=data['tool_resources']['file_search']
    )
    return Thread(
        id=data['id'],
        created_at=data['created_at'],
        metadata=data['metadata'],
        object=data['object'],
        tool_resources=tool_resources
    )
