from abc import ABC, abstractmethod


class brokerConnection(ABC):
    # Interface for broker connection implementations

    @abstractmethod
    def close_connection(self) -> None:
        pass

    @abstractmethod
    def connection_msg(self) -> str:
        pass
