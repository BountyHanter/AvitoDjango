import logging

import requests

from mainapp.models import AvitoAccount


def take_access_token_from_avito(*, user_id=None, client_id=None, client_secret=None, save_token_in_db=True):
    """
    Получает токен доступа.

    Функция требует, чтобы был передан либо `user_id`, либо одновременно `client_id` и `client_secret`.
    Сделал keyword-only аргументы чтобы не засунуть случайно в `user_id` - `client_id`.

    :param user_id: Отправляется в случае когда токен запрашивает функция отправки сообщения.
    :param client_id: Ключ из Авито.
    :param client_secret: Ключ из Авито.
    :param save_token_in_db: False. Используется пока что только для того чтобы не сохранять токен при добавлении нового аккаунта.
    :return: Кортеж из двух элементов: (status_code, access_token или error_message).
    :raises ValueError: Если не переданы требуемые параметры.
    """
    if user_id is None and (client_id is None or client_secret is None):
        raise ValueError("Необходимо передать либо 'user_id', либо 'client_id' и 'client_secret'.")

    if client_id is None:
        try:
            account = AvitoAccount.objects.get(user_id=user_id)
            client_id = account.client_id
            client_secret = account.client_secret
        except AvitoAccount.DoesNotExist:
            logging.debug('authorization.py/take_access_token_from_avito')
            logging.debug(f'Нет аккаунта с user_id: {user_id}')
            return 400, 'Нет аккаунта с user_id'

    url = 'https://api.avito.ru/token/'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }

    response = requests.post(url, headers=headers, data=data)
    response_data = response.json()

    if response.status_code == 200 and 'access_token' in response_data:
        access_token = response_data.get('access_token')
        logging.debug('authorization.py/take_access_token_from_avito')
        logging.debug(f'Аутентификация прошла успешно. Токен доступа: {access_token}')
        if save_token_in_db is True:
            save_access_token(access_token, client_id)
        return 200, access_token
    else:
        logging.debug('authorization.py/take_access_token_from_avito')
        logging.debug(f'Ошибка аутентификации. Код: {response.status_code}. Описание {response.text}')
        return 400, response.text


def save_access_token(token, client_id):
    try:
        account = AvitoAccount.objects.get(client_id=client_id)
        account.access_token = token
        account.save()
        logging.debug('authorization.py/save_access_token')
        logging.debug('Токен успешно сохранен в базу данных:')
    except AvitoAccount.DoesNotExist:
        logging.debug('authorization.py/save_access_token')
        logging.debug('Аккаунта с данным client_id не существует')
