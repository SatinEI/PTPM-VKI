import re
import logging
import sys

ALLOWED_PASSWORD_CHARS = set(
    "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    "0123456789"
    "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
)
UPPERCASE_CHARS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
LOWERCASE_CHARS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
DIGITS = "0123456789"

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_REGEX = re.compile(r"^\+[0-9]-[0-9]{3}-[0-9]{3}-[0-9]{4}$")
STRING_LOGIN_REGEX = re.compile(r"^[A-Za-z0-9_]{5,}$")

BLACKLIST = {"admin", "test", "user", "administrator", "moderator", "guest", "mod"}

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def validate_registration(login, password, confirm_password):
    params_log = "параметры не прошли проверку"
    try:
        if not isinstance(password, str):
            raise TypeError("Пароль должен быть строкой")
        masked_password = "*" * len(password)
        params_log = f"login='{login}', password='{masked_password}'"
        if not login:
            error_msg = "Логин не может быть пустым"
            logger.error(f"Error. Параметры: {params_log}. Причина: {error_msg}")
            return False, error_msg

        if login.lower() in BLACKLIST:
            error_msg = "Логин находится в черном списке запрещенных имен"
            logger.error(f"Error. Параметры: {params_log}. Причина: {error_msg}")
            return False, error_msg

        is_phone = PHONE_REGEX.fullmatch(login)
        is_email = EMAIL_REGEX.fullmatch(login)
        is_string = STRING_LOGIN_REGEX.fullmatch(login)

        if not is_phone and not is_email and not is_string:
            error_msg = ("логин должен быть телефоном (+x-xxx-xxx-xxxx), "
                         "email или строкой от 5 символов, допустимые символы (латиница, цифры, _)")
            logger.error(f"Error. Параметры: {params_log}. Причина: {error_msg}")
            return False, error_msg

        login_type = "phone" if is_phone else "email" if is_email else "string"
        logger.info(f"Логин распознан как {login_type}. login='{login}'")

        if not password:
            error_msg = "Пароль не может быть пустым"
            logger.error(f"Error. Параметры: {params_log}. Причина: {error_msg}")
            return False, error_msg

        logger.debug("Проверка на пустой пароль пройдена")

        if password != confirm_password:
            error_msg = "Пароль и подтверждение пароля не совпадают"
            logger.error(f"Error. Параметры: {params_log}. Причина: {error_msg}")
            return False, error_msg

        if len(password) < 7:
            error_msg = "Длина пароля меньше 7 символов"
            logger.error(f"Error. Параметры: {params_log}. Причина: {error_msg}")
            return False, error_msg

        if not all(ch in ALLOWED_PASSWORD_CHARS for ch in password):
            error_msg = "Пароль содержит недопустимые символы"
            logger.error(f"Error. Параметры: {params_log}. Причина: {error_msg}")
            return False, error_msg

        if not any(ch in UPPERCASE_CHARS for ch in password):
            error_msg = "Пароль должен содержать хотя бы одну заглавную букву"
            logger.error(f"Error. Параметры: {params_log}. Причина: {error_msg}")
            return False, error_msg

        if not any(ch in LOWERCASE_CHARS for ch in password):
            error_msg = "Пароль должен содержать хотя бы одну строчную букву"
            logger.error(f"Error. Параметры: {params_log}. Причина: {error_msg}")
            return False, error_msg

        if not any(ch in DIGITS for ch in password):
            error_msg = "Пароль должен содержать хотя бы одну цифру"
            logger.error(f"Error. Параметры: {params_log}. Причина: {error_msg}")
            return False, error_msg

        if not any(ch in SPECIAL_CHARS for ch in password):
            error_msg = "Пароль должен содержать хотя бы один спецсимвол"
            logger.error(f"Error. Параметры: {params_log}. Причина: {error_msg}")
            return False, error_msg
        if all(ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" for ch in login):
            error_msg = "Логин состоит только из заглавных букв"
            logger.warning(f"Warning. Параметры: {params_log}. Причина: {error_msg}")
            return True, error_msg

        logger.info(f"Успешный запрос. Параметры: {params_log}. True, Регистрация успешна.")
        return True, ""


    except Exception as e:
        error_msg = "Произошла ошибка"
        logger.error(f"Error. Параметры: {params_log}. False. Исключение: {e}")
        return False, error_msg


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    file_handler = logging.FileHandler("registration.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    try:
        is_success, message = validate_registration(
            "+7-913-521-1523", "абвгдЕ123!", "абвгд123!"
        )
        print(is_success)
        print(message)
    finally:
        file_handler.close()
        logger.removeHandler(file_handler)
