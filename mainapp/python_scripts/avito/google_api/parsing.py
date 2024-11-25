import json

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

from WhatsappAvitoDjango.settings import BASE_DIR

# Загрузка переменных из файла .env
load_dotenv()

# Названия файлов токена и ID таблицы
TOKEN_FILE =  os.path.join(BASE_DIR, 'mainapp', 'python_scripts', 'avito', 'google_api', 'token.json')# Путь к файлу токена
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')  # ID вашей таблицы
SHEET_NAME = os.getenv('SHEET_NAME')  # Название листа

def load_credentials():
    """Загружает токен из файла token.json."""
    with open(TOKEN_FILE, 'r') as token_file:
        token_data = json.load(token_file)
        return Credentials.from_authorized_user_info(token_data)

def parse_table():
    """Парсит указанный лист таблицы."""
    # Загружаем токен
    creds = load_credentials()

    # Подключаемся к Google Sheets API
    service = build('sheets', 'v4', credentials=creds)

    # Указываем диапазон в формате 'Лист'
    range_name = SHEET_NAME  # Читаем весь лист
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name
    ).execute()

    # Получаем данные
    values = result.get('values', [])
    if not values:
        print(f'Лист "{SHEET_NAME}" пуст.')
    else:
        print(f'Данные листа "{SHEET_NAME}" успешно загружены.')
    return values

def get_product_info(product_name, account_name, fields=None):
    """
    Получает данные о товаре по названию товара и аккаунту.

    :param product_name: Название товара
    :param account_name: Название аккаунта (Ivan, Vspishka, pro-lasers)
    :param fields: Список запрашиваемых полей, например: ["Цена", "Наличие", "Видео"]
                   Если не указан, возвращает "Название товара", "Цена", "Наличие", "Описание"
    """
    data = parse_table()

    # Сопоставление колонок для цены и видео в зависимости от аккаунта
    account_columns = {
        'Ivan': {'price': 1, 'video': 6},
        'Vspishka': {'price': 2, 'video': 5},
        'pro-lasers': {'price': 3, 'video': 7}
    }

    # Проверяем, есть ли такой аккаунт в списке
    if account_name not in account_columns:
        raise ValueError(f"Неизвестное название аккаунта: {account_name}")

    # Получаем индексы колонок для данного аккаунта
    price_column = account_columns[account_name]['price']
    video_column = account_columns[account_name]['video']

    # Приводим название товара к нижнему регистру для сравнения
    product_name = product_name.strip().lower()

    # Поиск товара
    for row in data:
        # Приводим название товара в таблице к нижнему регистру и убираем лишние пробелы
        row_product_name = row[0].strip().lower()

        if row_product_name == product_name:  # Сравнение без учёта регистра и пробелов
            # Проверяем длину строки перед доступом к элементам
            product = row[0].strip() if len(row) > 0 else "Не указано"
            price = row[price_column].strip() if len(row) > price_column and row[price_column].strip() else "Не указано"
            availability = row[4].strip() if len(row) > 4 and row[4].strip() else "Не указано"
            video = row[video_column].strip() if len(row) > video_column and row[video_column].strip() else "Не указано"
            description = row[8].strip() if len(row) > 8 and row[8].strip() else "Не указано"
            characteristics = row[9].strip() if len(row) > 9 and row[9].strip() else "Не указано"

            # Все доступные данные
            all_data = {
                'Название товара': product,
                'Цена': price,
                'Наличие': availability,
                'Видео': video,
                'Описание': description,
                'Характеристики': characteristics
            }

            # Если fields не передан, возвращаем только дефолтные поля
            if fields is None:
                fields = ["Название товара", "Цена", "Наличие", "Описание"]

            # Возвращаем только запрашиваемые поля
            return {key: all_data[key] for key in fields if key in all_data}

    # Если товар не найден
    return f"Товар с названием '{product_name}' не найден. Уточните название в файле"

if __name__ == '__main__':
    # Пример использования функции get_product_info
    try:
        product_info = get_product_info('Аппарат BBL лазер', 'Ivan')
        print("Найденные данные о товаре:")
        print(product_info)
    except ValueError as e:
        print(f"Ошибка: {e}")
