from google_auth_oauthlib.flow import InstalledAppFlow
import json

# Путь к файлу client_secret.json и имя для токена
CLIENT_SECRET_FILE = 'client_secret.json'
TOKEN_FILE = 'token.json'

# Укажите scope, необходимый для вашего приложения
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def create_token():
    """Создаёт токен и сохраняет его в JSON."""
    # Инициализируем процесс авторизации
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    # Сохраняем токен в файл token.json
    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }
    with open(TOKEN_FILE, 'w') as token_file:
        json.dump(token_data, token_file)

    print(f"Токен успешно создан и сохранён в {TOKEN_FILE}")

if __name__ == '__main__':
    create_token()
