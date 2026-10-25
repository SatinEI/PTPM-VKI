from abc import ABC, abstractmethod


class UserInput(ABC):
    @abstractmethod
    def get_registration_data(self) -> tuple[str, str, str]:
        """логин, пароль и подтверждение пароля."""


class ConsoleUserInput(UserInput):
    def get_registration_data(self) -> tuple[str, str, str]:
        login = input("Логин: ")
        password = input("Пароль: ")
        confirmation = input("Подтверждение пароля: ")
        return login, password, confirmation
