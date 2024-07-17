# mainapp/models.py
from django.contrib.auth.models import User
from django.db import models


class AvitoAccount(models.Model):
    name = models.CharField(max_length=255, unique=True)
    client_id = models.CharField(max_length=255, unique=True)
    client_secret = models.CharField(max_length=255, unique=True)
    assistant_key = models.CharField(max_length=255)
    triggers = models.TextField(null=True, blank=True)
    check_phone = models.BooleanField(default=False)
    user_id = models.CharField(max_length=255, null=True, blank=True)
    access_token = models.CharField(max_length=255, null=True, blank=True)
    tg_manager = models.CharField(max_length=255)
    wait_time = models.IntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avito_accounts')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'avito_accounts'


class AvitoChat(models.Model):
    chat_id = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
    chat_name = models.CharField(max_length=255)
    user_pic = models.CharField(max_length=255)
    status = models.BooleanField(default=False)

    class Meta:
        db_table = 'avito_chats'


class AvitoMessage(models.Model):
    chat_id = models.CharField(max_length=255)
    sender_id = models.CharField(max_length=255)
    content = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'avito_messages'


class AvitoIgnoredChat(models.Model):
    chat_id = models.CharField(max_length=255)

    class Meta:
        db_table = 'avito_ignored_chats'
