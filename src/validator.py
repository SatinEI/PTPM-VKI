from src.lab_1 import validate_registration


class RegistrationValidator:

    def validate(self, login: str, password: str, confirmation: str) -> tuple[bool, str]:
        return validate_registration(login, password, confirmation)
