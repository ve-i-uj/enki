"""External interfaces."""

from __future__ import annotations
import abc
from typing import Any, Tuple, Iterator, List, Union, Awaitable

# TODO: [05.02.2021 11:33]
# Здесь должны быть интерфейсы направленные во вне. Т.е. это интерфейс классов
# фреймворка.


class IKBEType(abc.ABC):
    """Type of KBE client-server communication of KBEngine.

    This type is used in def files.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Type name"""
        pass

    @property
    @abc.abstractmethod
    def default(self) -> Any:
        """Default value of the python type."""
        pass

    @abc.abstractmethod
    def decode(self, data: memoryview) -> Tuple[Any, int]:
        """Decode bytes to a python type.

        Returns decoded data and offset
        """
        pass

    @abc.abstractmethod
    def encode(self, value: Any) -> bytes:
        """Encode a python type to bytes."""
        pass

    @abc.abstractmethod
    def alias(self, alias_name: str) -> IKBEType:
        """Create alias of that type."""
        pass


class IMessage(abc.ABC):
    """Wrapper around client-server communication data."""

    @property
    @abc.abstractmethod
    def id(self) -> int:
        """Message id (see messages_fixed_defaults.xml)."""
        pass

    @abc.abstractmethod
    def get_field_map(self) -> Iterator[Tuple[Any, IKBEType]]:
        """Return map of field values to its KBE type"""
        pass

    @abc.abstractmethod
    def get_values(self) -> List[Any]:
        """Return values of message fields."""
        pass


class IMsgReceiver(abc.ABC):
    """Message receiver interface."""

    @abc.abstractmethod
    def on_receive_msg(self, msg: IMessage) -> bool:
        """Call on receive message.

        Returns message's handled or not.
        """
        pass


class IClient(abc.ABC):

    # TODO: [23.02.2021 11:44 burov_alexey@mail.ru]
    # Это метод не публичного интерфейса (для приложения), а внутреннего
    # взаимодействия с Connection. Нужно убрать этот метод в их взаимодействие
    # (Connection <--> Client)
    # TODO: [27.02.2021 11:29 burov_alexey@mail.ru]
    # А может такие вещи в обще нужно просто убирать из интерфейсов. Это же
    # часть реализации клиента и его взаимодействия с IConnection
    @abc.abstractmethod
    def on_receive_data(self, data: memoryview) -> None:
        """Handle incoming bytes data from a server."""
        pass

    @abc.abstractmethod
    def set_msg_receiver(self, receiver: IMsgReceiver):
        """Set the receiver of message."""
        pass

    @abc.abstractmethod
    def send(self, msg: IMessage) -> None:
        """Send a message."""
        pass

    @abc.abstractmethod
    def start(self) -> None:
        """Start this client."""
        pass

    @abc.abstractmethod
    def stop(self) -> None:
        """Stop this client."""
        pass


class ICommunicationProtocol(abc.ABC):

    @abc.abstractmethod
    def on_receive_msg(self, msg: IMessage) -> None:
        pass

    @abc.abstractmethod
    def on_connected(self):
        """Fire after success connecting."""
        pass

    @abc.abstractmethod
    def fini(self):
        pass

    @abc.abstractmethod
    async def _waiting_for(self, msg_id_or_ids: Union[int, List[int]],
                           timeout: int):
        pass


class IReturningCommand(abc.ABC):
    """Interface of a command returning result from execute method."""

    @abc.abstractmethod
    def execute(self) -> Any:
        pass


class IMsgRespAwaitable(abc.ABC):
    """Interface for messages waiting to be replied."""

    @abc.abstractmethod
    def send(self, msg: IMessage) -> None:
        """Send the message."""
        pass

    @abc.abstractmethod
    def waiting_for(self, success_msg_spec: int, error_msg_specs: List[int], timeout: int
                    ) -> Awaitable[IMessage]:
        """Waiting for a response to the sent message."""
        pass


class PluginType(abc.ABC):
    """Abstract class for inner implemented class of application.

    This abstract class exists to distinguish built-in types of python
    and inner defined ones in generated code.
    """
