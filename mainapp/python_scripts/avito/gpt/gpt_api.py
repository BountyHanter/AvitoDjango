import json
import os

import time

from dotenv import load_dotenv
from openai import OpenAI
import openai
from openai.types.beta.thread import ToolResources, Thread

from mainapp.python_scripts.avito.google_api.parsing import get_product_info

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_KEY")

client = OpenAI(api_key=OPENAI_KEY)

function_registry = {
    'get_product_info':get_product_info
}

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
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
        if m.role == 'assistant':
            return m.content[0].text.value


def pretty_print2(thread, message):
    messages = client.beta.threads.messages.list(
        thread_id=thread.id, order="asc", after=message.id
    )
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
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

def response_to_gpt(run, thread, response, tool_call):
    run = client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread.id,
        run_id=run.id,
        tool_outputs=[
            {
                'tool_call_id':tool_call.id,
                'output':response,
            }
        ]
    )
    return run


def gpt_call_function(run, thread):
    tool_calls = run.required_action.submit_tool_outputs.tool_calls  # Список вызовов функций
    outputs = []

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        print(function_name, 'function name')

        # Преобразуем строку JSON в словарь
        arguments = json.loads(tool_call.function.arguments)
        print(arguments, 'arguments')

        # Выполняем функцию из function_registry
        if function_name in function_registry:
            try:
                # Передаём аргументы с использованием распаковки
                result = function_registry[function_name](**arguments)
                outputs.append({
                    'tool_call_id': tool_call.id,
                    'output': str(result),
                })
            except TypeError as e:
                print(f"Error calling function {function_name}: {e}")
                outputs.append({
                    'tool_call_id': tool_call.id,
                    'output': f"Error: {e}",
                })
        else:
            print(f"Function {function_name} not found in registry.")
            outputs.append({
                'tool_call_id': tool_call.id,
                'output': f"Error: function {function_name} is not implemented.",
            })

    # Отправляем все результаты в API
    run = response_to_gpt_multiple(run, thread, outputs)
    run = wait_on_run(run, thread)
    return run


def response_to_gpt_multiple(run, thread, outputs):
    """
    Обрабатывает сразу несколько вызовов функций.
    """
    run = client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread.id,
        run_id=run.id,
        tool_outputs=outputs  # Передаём список всех результатов
    )
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
