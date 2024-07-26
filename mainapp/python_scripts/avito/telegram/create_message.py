from mainapp.models import AvitoMessage


def generate_message_text(chat_id, author_id, trigger):
    # Получаем все сообщения для данного chat_id, отсортированные по timestamp
    messages = AvitoMessage.objects.filter(chat_id=chat_id).order_by('timestamp')

    # Формируем текст сообщения
    message_lines = []
    for message in messages:
        sender = 'аккаунт' if str(message.sender_id) == str(author_id) else 'клиент'
        message_lines.append(f"{sender} - {message.content}")

    # Объединяем все строки в одно сообщение
    chat_messages = "\n\n".join(message_lines)
    if trigger:
        message_text = (f"Требуется менеджер - https://www.avito.ru/profile/messenger/channel/{chat_id}\n\n"
                        f"Сообщения:\n{chat_messages}")
    else:
        message_text = (f"Клиент не ответил - https://www.avito.ru/profile/messenger/channel/{chat_id}\n\n"
                        f"Сообщения:\n{chat_messages}")
    return message_text
