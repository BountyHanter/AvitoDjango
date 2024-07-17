from asgiref.sync import sync_to_async

from mainapp.models import AvitoAccount


def load_access_token(*, client_id=None, user_id=None):
    try:
        if client_id is not None:
            account = AvitoAccount.objects.filter(client_id=client_id).first()
            if account:
                return account.access_token
            else:
                print('another_avito_scripts.py')
                print(f"Токен для client_id '{client_id}' не найден.")
                return None
        elif user_id is not None:
            account = AvitoAccount.objects.filter(user_id=user_id).first()
            if account:
                return account.access_token
            else:
                print('another_avito_scripts.py')
                print(f"Токен для user_id '{user_id}' не найден.")
                return None
        else:
            raise ValueError("Необходимо передать либо 'client_id', либо 'user_id'.")
    except Exception as e:
        print('another_avito_scripts.py')
        print(f'Ошибка при работе с базой данных: {e}')
        return None
