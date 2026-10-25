from src.database import RegistrationDatabase
from src.external_service import Sender
from src.user_interaction import UserInput
from src.validator import RegistrationValidator


class Controller:
    def __init__(
        self,
        user_input: UserInput,
        validator: RegistrationValidator,
        database: RegistrationDatabase,
        sender: Sender,
    ) -> None:
        self._user_input = user_input
        self._validator = validator
        self._database = database
        self._sender = sender

    def run(self) -> tuple[bool, str]:
        login, password, confirmation = self._user_input.get_registration_data()
        result = self._database.get_record(login, password, confirmation)
        if result is None:
            result = self._validator.validate(login, password, confirmation)
            self._database.add_record(login, password, confirmation, result)

        success, message = result
        text = "Регистрация успешна" if success else "Регистрация отклонена"
        if message:
            text += f": {message}"
        self._sender.send(text)
        return result
