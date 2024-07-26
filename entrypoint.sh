#!/bin/sh

# Создаем директорию для логов, если ее нет
mkdir -p /app/logs

# Применяем миграции базы данных
python manage.py migrate --noinput

# Собираем статические файлы
python manage.py collectstatic --noinput

# Создаем суперпользователя, если необходимо
if [ "$CREATE_SUPERUSER" = "true" ]; then
  python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
END
fi

# Запускаем сервер
exec gunicorn --bind 0.0.0.0:3200 WhatsappAvitoDjango.wsgi:application

