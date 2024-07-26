# mainapp/forms.py
from django import forms
from .models import AvitoAccount, AvitoChat, AvitoMessage


class AvitoAccountForm(forms.ModelForm):
    class Meta:
        model = AvitoAccount
        fields = ['name', 'client_id', 'client_secret', 'assistant_key',
                  'triggers', 'check_phone', 'tg_manager', 'wait_time', 'user_id',
                  'time_to_shutdown', 'should_ping_manager', 'time_to_trigger']


class AvitoChatForm(forms.ModelForm):
    class Meta:
        model = AvitoChat
        fields = ['chat_id', 'user_id', 'chat_name', 'user_pic']


class AvitoMessageForm(forms.ModelForm):
    class Meta:
        model = AvitoMessage
        fields = ['chat_id', 'sender_id', 'content']
