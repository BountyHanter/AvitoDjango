# mainapp/models.py
from django.contrib.auth.models import User
from django.db import models


class AvitoAccount(models.Model):
    name = models.CharField(max_length=255, unique=True)
    client_id = models.CharField(max_length=255, unique=True)
    client_secret = models.CharField(max_length=255, unique=True)
    assistant_key = models.CharField(max_length=255)
    wait_time = models.IntegerField()
    tg_manager = models.CharField(max_length=255)
    triggers = models.TextField(null=True, blank=True)
    triggers_ai = models.TextField(null=True, blank=True)
    check_phone = models.BooleanField(default=False)
    time_to_trigger = models.IntegerField(null=True, blank=True)
    time_to_shutdown = models.IntegerField(null=True, blank=True)
    should_ping_manager_after_shutdown = models.BooleanField(default=False)
    bot_text = models.TextField(null=True, blank=True)
    bot_interval = models.IntegerField(null=True, blank=True)
    user_id = models.CharField(max_length=255, null=True, blank=True)
    access_token = models.CharField(max_length=255, null=True, blank=True)
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
    is_read = models.BooleanField(default=False)
    tokens = models.TextField(default=100000)
    can_send_reminder = models.BooleanField(default=False)

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
