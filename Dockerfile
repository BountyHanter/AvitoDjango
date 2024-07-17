# Используем официальный образ Python 3.10 в качестве базового образа
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y \
    sqlite3 \
    libsqlite3-dev \
    gcc \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && apt-get clean

# Копируем файл зависимостей в контейнер
COPY requirements.txt /app/

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта в контейнер
COPY . /app/

# Копируем сценарий entrypoint
COPY entrypoint.sh /app/

# Делаем сценарий исполняемым
RUN chmod +x /app/entrypoint.sh

# Открываем порт, который будет использоваться контейнером
EXPOSE 3200

# Устанавливаем сценарий entrypoint.sh как точку входа
ENTRYPOINT ["/app/entrypoint.sh"]

# Команда по умолчанию для запуска Django
CMD ["gunicorn", "--bind", "0.0.0.0:3200", "WhatsappAvitoDjango.wsgi:application"]
