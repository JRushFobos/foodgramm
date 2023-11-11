import re

from rest_framework import validators


def validate_username(value):
    """Валидация username."""
    if value.lower() == 'me':
        raise validators.ValidationError(
            'Нельзя использовать "me" в качестве логина.'
        )
    return value


def validate_name(value):
    """Валидация name."""
    if not re.match(r'^[а-яА-ЯёЁa-zA-Z\s]+$', value):
        raise validators.ValidationError('Введены некорректные символы.')
    return value
