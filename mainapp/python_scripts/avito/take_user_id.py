import logging

import requests


def get_authorized_user_info(access_token):
    url = "https://api.avito.ru/core/v1/accounts/self"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            user_info = response.json()
            return user_info.get('id')
        elif response.status_code == 401:
            logging.debug('take_user_id.py')
            logging.debug("Требуется аутентификация")
        elif response.status_code == 403:
            logging.debug('take_user_id.py')
            logging.debug("Неверный Token/Oauth Scope")
            return 403
        elif response.status_code == 500:
            logging.debug('take_user_id.py')
            logging.debug("Внутренняя ошибка метода API")
        elif response.status_code == 503:
            logging.debug('take_user_id.py')
            logging.debug("Метод API временно недоступен")
        else:
            logging.debug('take_user_id.py')
            logging.debug(f"Неожиданный статус ответа: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logging.debug('take_user_id.py')
        logging.debug(f"Ошибка при выполнении запроса: {e}")
    return None