"""External interfaces."""

from __future__ import annotations
import abc
from typing import Any, Tuple, Iterator, List, Union

from enki import settings

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
        """Default value of the type."""
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


class IClient(abc.ABC):

    @abc.abstractmethod
    def on_receive_data(self, data: memoryview) -> None:
        """Handle incoming data from a server."""
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
    def connect(self, addr: settings.AppAddr, component: settings.ComponentEnum
                ) -> None:
        """Connect to a server component."""
        pass

    @abc.abstractmethod
    def stop(self) -> None:
        """Stop this client."""
        pass

    @abc.abstractmethod
    def fire(self, event: str, values: Tuple[Any, ...]) -> Any:
        """Call the method of a communication protocol."""
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
