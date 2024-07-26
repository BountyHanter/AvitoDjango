# mainapp/views.py
import logging
import threading

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.http import require_POST

from WhatsappAvitoDjango.settings import WEBHOOK_API, DEBUG
from .models import AvitoAccount, AvitoChat, AvitoMessage, AvitoIgnoredChat
from .forms import AvitoAccountForm
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

import json

from mainapp.python_scripts.avito.authorization import save_access_token, take_access_token_from_avito as token
from .python_scripts.avito.delete_webhook import delete_webhook
from .python_scripts.avito.globals import trigger_timers
from .python_scripts.avito.messages.send_message import send_message
from .python_scripts.avito.messages.upd_chat_status import update_chat_status
from .python_scripts.avito.registr_webhook import register_webhook
from .python_scripts.avito.take_user_id import get_authorized_user_info
from .webhook_utils import parse_webhook_payload, process_webhook

logger = logging.getLogger(__name__)


@csrf_exempt
def webhook_endpoint(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            user_id, author_id, chat_id, content = parse_webhook_payload(payload)
            print(payload)
            # Немедленно возвращаем ответ
            threading.Thread(target=process_webhook, args=(user_id, author_id, chat_id, content)).start()

            print("Webhook processed successfully.")
            return JsonResponse({'status': 'Webhook received'}, status=200)
        except json.JSONDecodeError:
            print("Invalid JSON received.")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Error processing webhook: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    print("Invalid request method.")
    return JsonResponse({'error': 'Invalid request method'}, status=405)


# ------------------- html --------------------------


def user_login(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Проверка на существование пользователя и его статус
        try:
            user = User.objects.get(username=username)
            if not user.is_active:
                return render(request, 'mainapp/login.html',
                              {'error': 'Ваша учетная запись деактивирована, обратитесь к администрации.'})
        except User.DoesNotExist:
            pass

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('avito_accounts')
        else:
            print("Invalid login attempt: ", username)  # Отладочное сообщение
            return render(request, 'mainapp/login.html', {'error': 'Неправильный логин или пароль'})
    else:
        return render(request, 'mainapp/login.html')


@login_required
def avito_accounts(request):
    if request.user.is_superuser:
        accounts = AvitoAccount.objects.all()
    else:
        accounts = AvitoAccount.objects.filter(created_by=request.user)
    return render(request, 'mainapp/avito_accounts.html', {'accounts': accounts})


# --- chats ----
@login_required
def avito_chats(request):
    if request.user.is_superuser:
        accounts = AvitoAccount.objects.all()
    else:
        accounts = AvitoAccount.objects.filter(created_by=request.user)
    chats = AvitoChat.objects.all()
    return render(request, 'mainapp/avito_chats.html', {'accounts': accounts, 'chats': chats})


@login_required
def get_messages(request, chat_id):
    update_chat_status(chat_id, status=False) # Снимаем уведомление о новом сообщении
    messages = AvitoMessage.objects.filter(chat_id=chat_id).order_by('timestamp')
    return JsonResponse({'messages': list(messages.values())})


@login_required
def check_ignored_chat(request, chat_id):
    is_ignored = AvitoIgnoredChat.objects.filter(chat_id=chat_id).exists()
    return JsonResponse({'is_ignored': is_ignored})


@login_required
@csrf_exempt
@require_POST
def toggle_ignored_chat(request, chat_id):
    try:
        import json
        body = json.loads(request.body.decode('utf-8'))
        action = body.get('action')

        if action == 'start':
            AvitoIgnoredChat.objects.filter(chat_id=chat_id).delete()
        elif action == 'stop':
            AvitoIgnoredChat.objects.get_or_create(chat_id=chat_id)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@csrf_exempt
def send_message_endpoint(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('user_id')
        chat_id = data.get('chat_id')
        message_text = data.get('message_text')

        if user_id and chat_id and message_text:
            try:
                send_message(user_id=user_id, message_text=message_text, chat_id=chat_id)
                return JsonResponse({'status': 'success'}, status=200)
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# -------------


@login_required
def whatsapp_accounts(request):
    return render(request, 'mainapp/whatsapp_accounts.html')


@login_required
def whatsapp_chats(request):
    return render(request, 'mainapp/whatsapp_chats.html')


@login_required
def whatsapp_broadcasts(request):
    return render(request, 'mainapp/whatsapp_broadcasts.html')


@login_required
def whatsapp_templates(request):
    return render(request, 'mainapp/whatsapp_templates.html')


@login_required
def whatsapp_send_message(request):
    return render(request, 'mainapp/whatsapp_send_message.html')


@login_required
def whatsapp_statistics(request):
    return render(request, 'mainapp/whatsapp_statistics.html')


# -------------------------------------------------------------------------------------


@login_required
def add_account(request):
    if request.method == 'POST':
        form = AvitoAccountForm(request.POST)
        fields = {
            'name': 'Имя аккаунта',
            'client_id': 'Client_id',
            'client_secret': 'Client_secret',
            'assistant_key': 'Assistant_key',
            'triggers': 'Триггеры',
            'tg_manager': 'Телеграм менеджера',
            'wait_time': 'Время сбора сообщений',
            'check_phone': 'Триггер номера телефона'
        }

        # Логирование полученных данных
        for key, description in fields.items():
            if form.data.get(key):
                logger.debug(f'{description}: {form.data[key]}')

        if form.is_valid():
            try:
                # Получение токена
                status_code, response_content = token(client_id=form.cleaned_data['client_id'],
                                                      client_secret=form.cleaned_data['client_secret'],
                                                      save_token_in_db=False)
                if status_code != 200:
                    return JsonResponse(
                        {'success': False,
                         'error': f'Обнаружена ошибка в данных<br><br>Описание ошибки: {response_content}'})

                access_token = response_content

                # Получение user_id
                user_id = get_authorized_user_info(access_token)

                # Создание нового объекта аккаунта с добавленным user_id и created_by
                account = form.save(commit=False)
                account.user_id = user_id
                account.created_by = request.user
                account.save()

                # Проверяем, что объект успешно сохранен
                if account:
                    save_access_token(access_token, form.cleaned_data['client_id'])
                    register_webhook(str(WEBHOOK_API), access_token)
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'error': 'Ошибка сохранения данных'})
            except Exception as e:
                logger.error(f"Ошибка при добавлении аккаунта: {str(e)}")
                return JsonResponse({'success': False, 'error': str(e)})
        else:
            logger.error("Ошибки формы: %s", form.errors)
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def edit_account(request, account_id):
    account = get_object_or_404(AvitoAccount, id=account_id)
    if account.created_by != request.user and not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'У вас нет прав на редактирование этого аккаунта.'})

    if request.method == 'POST':
        form = AvitoAccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({
        'id': account.id,
        'name': account.name,
        'client_id': account.client_id,
        'client_secret': account.client_secret,
        'assistant_key': account.assistant_key,
        'triggers': account.triggers,
        'check_phone': account.check_phone,
        'tg_manager': account.tg_manager,
        'wait_time': account.wait_time,
        'time_to_shutdown': account.time_to_shutdown,
        'should_ping_manager': account.should_ping_manager,
        'time_to_trigger': account.time_to_trigger,
        'user_id': account.user_id,
    })


@login_required
def delete_account(request, account_id):
    account = get_object_or_404(AvitoAccount, id=account_id)
    if account.created_by != request.user and not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'У вас нет прав на удаление этого аккаунта.'})

    if request.method == 'DELETE':
        # Извлекаем необходимые поля
        client_id = account.client_id
        client_secret = account.client_secret
        delete_webhook(client_id, client_secret)

        account.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})
