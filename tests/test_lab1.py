import unittest

from src.lab_1 import validate_registration


VALID_PASSWORD = "Абвг12!"
INVALID_LOGIN_MESSAGE = (
    "логин должен быть телефоном (+x-xxx-xxx-xxxx), "
    "email или строкой от 5 символов, допустимые символы (латиница, цифры, _)"
)


class TestRegistration(unittest.TestCase):
    def test_valid_string_login(self):
        result = validate_registration("abc12", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result, (True, ""))

    def test_valid_email_and_phone(self):
        self.assertEqual(
            validate_registration("name@example.ru", VALID_PASSWORD, VALID_PASSWORD),
            (True, ""),
        )
        self.assertEqual(
            validate_registration("+7-913-521-1523", VALID_PASSWORD, VALID_PASSWORD),
            (True, ""),
        )

    def test_empty_and_blacklisted_login(self):
        self.assertEqual(
            validate_registration("", VALID_PASSWORD, VALID_PASSWORD),
            (False, "Логин не может быть пустым"),
        )
        self.assertEqual(
            validate_registration("AdMiN", VALID_PASSWORD, VALID_PASSWORD),
            (False, "Логин находится в черном списке запрещенных имен"),
        )

    def test_invalid_login_format(self):
        result = validate_registration("abcd", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result, (False, INVALID_LOGIN_MESSAGE))

    def test_empty_password(self):
        result = validate_registration("abcde", "", "")
        self.assertEqual(result, (False, "Пароль не может быть пустым"))

    def test_password_confirmation_does_not_match(self):
        result = validate_registration("abcde", VALID_PASSWORD, "Абвг13!")
        self.assertEqual(result, (False, "Пароль и подтверждение пароля не совпадают"))

    def test_short_and_invalid_password(self):
        self.assertEqual(
            validate_registration("abcde", "Абв12!", "Абв12!"),
            (False, "Длина пароля меньше 7 символов"),
        )
        self.assertEqual(
            validate_registration("abcde", "Abвг12!", "Abвг12!"),
            (False, "Пароль содержит недопустимые символы"),
        )

    def test_password_requires_all_character_groups(self):
        self.assertEqual(
            validate_registration("abcde", "абвг12!", "абвг12!"),
            (False, "Пароль должен содержать хотя бы одну заглавную букву"),
        )
        self.assertEqual(
            validate_registration("abcde", "АБВГ12!", "АБВГ12!"),
            (False, "Пароль должен содержать хотя бы одну строчную букву"),
        )
        self.assertEqual(
            validate_registration("abcde", "Абвгде!", "Абвгде!"),
            (False, "Пароль должен содержать хотя бы одну цифру"),
        )
        self.assertEqual(
            validate_registration("abcde", "Абвг123", "Абвг123"),
            (False, "Пароль должен содержать хотя бы один спецсимвол"),
        )

    def test_uppercase_login_returns_warning(self):
        result = validate_registration("ABCDE", VALID_PASSWORD, VALID_PASSWORD)
        self.assertEqual(result, (True, "Логин состоит только из заглавных букв"))

    def test_invalid_password_type_returns_error(self):
        result = validate_registration("abcde", None, None)
        self.assertEqual(result, (False, "Произошла ошибка"))


if __name__ == "__main__":
    unittest.main()
