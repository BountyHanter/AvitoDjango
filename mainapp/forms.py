# mainapp/forms.py
from django import forms
from .models import AvitoAccount, AvitoChat, AvitoMessage


class AvitoAccountForm(forms.ModelForm):
    class Meta:
        model = AvitoAccount
        fields = [
            'name', 'client_id', 'client_secret', 'assistant_key', 'wait_time', 'tg_manager',
            'triggers', 'triggers_ai', 'check_phone', 'time_to_trigger', 'time_to_shutdown',
            'should_ping_manager_after_shutdown', 'bot_text', 'bot_interval', 'user_id',
        ]


class AvitoChatForm(forms.ModelForm):
    class Meta:
        model = AvitoChat
        fields = ['chat_id', 'user_id', 'chat_name', 'user_pic']


class AvitoMessageForm(forms.ModelForm):
    class Meta:
        model = AvitoMessage
        fields = ['chat_id', 'sender_id', 'content']
