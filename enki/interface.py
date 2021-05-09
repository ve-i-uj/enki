"""External interfaces."""

from __future__ import annotations
import abc
from typing import Any, Tuple, Iterator, List, Union, Awaitable

# TODO: [05.02.2021 11:33]
# Здесь должны быть интерфейсы направленные во вне. Т.е. это интерфейс классов
# фреймворка.


class IKBEType(abc.ABC):
    """Type of KBE client-server communication of KBEngine.

    It's a server data decoder / encoder.
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
        """Create alias of the "self" type."""
        pass

    @abc.abstractmethod
    def to_string(self) -> str:
        """Return string representation of the python type instance.

        It's a string of value returned by "self.default".
        """
        pass


class IMessage(abc.ABC):
    """Wrapper around client-server communication data."""

    @property
    @abc.abstractmethod
    def id(self) -> int:
        """Message id (see messages_fixed_defaults.xml)."""
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Message name (see messages_fixed_defaults.xml)."""
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

    @abc.abstractmethod
    def set_msg_receiver(self, receiver: IMsgReceiver):
        """Set the receiver of message."""
        pass

    @abc.abstractmethod
    def send(self, msg: IMessage) -> None:
        """Send the message."""
        pass

    @abc.abstractmethod
    def start(self) -> None:
        """Start this client."""
        pass

    @abc.abstractmethod
    def stop(self) -> None:
        """Stop this client."""
        pass


class PluginType(abc.ABC):
    """Abstract class for inner implemented class of the application.

    This abstract class exists to distinguish built-in types of python
    and inner defined ones in generated code.
    """
