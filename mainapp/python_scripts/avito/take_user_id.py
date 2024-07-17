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
            print('take_user_id.py')
            print("Требуется аутентификация")
        elif response.status_code == 403:
            print('take_user_id.py')
            print("Неверный Token/Oauth Scope")
            return 403
        elif response.status_code == 500:
            print('take_user_id.py')
            print("Внутренняя ошибка метода API")
        elif response.status_code == 503:
            print('take_user_id.py')
            print("Метод API временно недоступен")
        else:
            print('take_user_id.py')
            print(f"Неожиданный статус ответа: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print('take_user_id.py')
        print(f"Ошибка при выполнении запроса: {e}")
    return None