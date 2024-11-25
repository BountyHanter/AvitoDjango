import requests

from mainapp.python_scripts.avito.authorization import take_access_token_from_avito


def get_chat_info(*, user_id, chat_id, access_token):

    url = f"https://api.avito.ru/messenger/v2/accounts/{user_id}/chats/{chat_id}"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        chat_data = response.json()
        print('check_client_info.py')
        print(chat_data)
        for user in chat_data.get('users', []):
            if user.get('id') != int(user_id):
                avatar_default = user.get('public_user_profile', {}).get('avatar', {}).get('default')
                name = user.get('name')
                title = chat_data.get('context', {}).get('value', {}).get('title', '')
                if title:
                    name = f"{name} ({title})"
                return avatar_default, name, title
    elif response.status_code == 403:
        status_code, new_access_token = take_access_token_from_avito(user_id=user_id, save_token_in_db=True)
        if status_code == 200:
            avatar_default, name, title = get_chat_info(user_id=user_id, chat_id=chat_id, access_token=new_access_token)
            return avatar_default, name, title
        else:
            print('check_client_info.py')
            print(f"Ошибка получения временного токена: {status_code}")
            print(new_access_token)
            return None, None
        
    else:
        print('check_client_info.py')
        print(f"Ошибка: {response.status_code}")
        print(response.text)
        return None, None
