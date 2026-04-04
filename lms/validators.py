import re
from rest_framework.serializers import ValidationError


def validate_youtube_link(value):
    """
    Валидатор для проверки, что ссылка ведет на youtube.com
    """
    if not value:
        return value

    # Регулярное выражение для проверки youtube ссылок
    youtube_pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/'

    if not re.match(youtube_pattern, value):
        raise ValidationError(
            "Разрешены только ссылки на youtube.com. "
            "Ссылки на сторонние ресурсы запрещены."
        )

    return value
