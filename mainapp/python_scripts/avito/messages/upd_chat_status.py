from mainapp.models import AvitoChat


def update_chat_status(chat_id, status=True):
    try:
        chat = AvitoChat.objects.get(chat_id=chat_id)
        if status is True:
            chat.status = True
        else:
            chat.status = False
        chat.save()
        print(f"Статус чата с chat_id {chat_id} успешно обновлен на True")
    except AvitoChat.DoesNotExist:
        print(f"Чат с chat_id {chat_id} не найден")