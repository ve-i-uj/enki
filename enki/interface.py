"""Client interfaces."""

from __future__ import annotations
import abc
from typing import Any, ClassVar, Tuple, Iterator, List, Type, Optional

from enki import kbetype


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
    def get_field_map(self) -> Iterator[Tuple[Any, kbetype.IKBEType]]:
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


class IEntityRemoteCall:
    """Entity method remote call."""
    pass


class IEntity(abc.ABC):
    CLS_ID: ClassVar[int]

    @abc.abstractproperty
    def id(self) -> int:
        pass

    @abc.abstractproperty
    def cell(self) -> IEntityRemoteCall:
        pass

    @abc.abstractproperty
    def base(self) -> IEntityRemoteCall:
        pass

    @classmethod
    @abc.abstractmethod
    def get_implementation(cls) -> Optional[Type[IEntity]]:
        pass

    @abc.abstractmethod
    def add_pending_msg(self, msg: IMessage):
        pass

    @abc.abstractmethod
    def get_pending_msgs(self) -> list[IMessage]:
        pass

    @abc.abstractmethod
    def clean_pending_msgs(self):
        pass


class IEntityMgr(abc.ABC):
    """Entity manager interface."""

    @abc.abstractmethod
    def get_entity(self, entity_id: int) -> IEntity:
        """Get entity by id."""
        pass

    @abc.abstractmethod
    def remote_call(self, msg: IMessage) -> None:
        """Send remote call message."""
        pass

    @abc.abstractmethod
    def initialize_entity(self, entity_id: int, entity_cls_name: str) -> IEntity:
        pass
