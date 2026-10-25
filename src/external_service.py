from abc import ABC, abstractmethod


class Sender(ABC):
    @abstractmethod
    def send(self, text: str) -> None:
        """Отправить строку результата стороннему процессу."""


class SimulatedSender(Sender):

    def __init__(self) -> None:
        self.sent_messages: list[str] = []

    def send(self, text: str) -> None:
        self.sent_messages.append(text)
