import logging

from mainapp.models import AvitoChat


def update_chat_status(chat_id, status=True):
    try:
        chat = AvitoChat.objects.get(chat_id=chat_id)
        if status is True:
            chat.is_read = True
        else:
            chat.is_read = False
        chat.save()
    except AvitoChat.DoesNotExist:
        logging.debug(f"Чат с chat_id {chat_id} не найден")