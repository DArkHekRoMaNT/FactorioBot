from abc import ABC, abstractmethod


class ChatBot(ABC):
    @abstractmethod
    def send_message(self, msg: str):
        pass
