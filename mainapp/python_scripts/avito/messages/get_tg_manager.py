from mainapp.models import AvitoAccount

from django.core.exceptions import ObjectDoesNotExist


def get_tg_manager(user_id):
    """
    Получает tg_manager для данного user_id из таблицы AvitoAccount.

    :param user_id: Идентификатор пользователя для поиска.
    :return: Значение поля tg_manager или None, если пользователь не найден.
    """
    try:
        account = AvitoAccount.objects.get(user_id=user_id)
        return account.tg_manager
    except ObjectDoesNotExist:
        return None
