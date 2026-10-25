"""Консольная точка входа: python main.py."""

from src.controller import Controller
from src.database import RegistrationDatabase
from src.external_service import SimulatedSender
from src.user_interaction import ConsoleUserInput
from src.validator import RegistrationValidator


def main() -> None:
    database = RegistrationDatabase()
    try:
        sender = SimulatedSender()
        controller = Controller(
            ConsoleUserInput(), RegistrationValidator(), database, sender
        )
        success, message = controller.run()
        print("Успех" if success else "Ошибка")
        if message:
            print(message)
        print("Имитация отправки:", sender.sent_messages[-1])
    finally:
        database.close()


if __name__ == "__main__":
    main()
