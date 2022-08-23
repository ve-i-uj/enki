"""Client interfaces."""

from __future__ import annotations
import abc
import logging
from typing import Any, Callable, ClassVar, Tuple, Iterator, List, Type, \
    Optional

from enki import kbetype

logger = logging.getLogger(__name__)


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
    def set_msg_receiver(self, receiver: IMsgReceiver) -> None:
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


class IKBEClientEntity(abc.ABC):
    """The kbe client API like in the documentation.

    See <https://github.com/kbengine/kbengine/blob/master/docs/api/kbengine_api(en).chm>
    """

    @abc.abstractproperty
    def id(self) -> int:
        pass

    @abc.abstractproperty
    def direction(self) -> kbetype.Vector3Data:
        pass

    @abc.abstractproperty
    def position(self) -> kbetype.Vector3Data:
        pass

    @abc.abstractproperty
    def spaceID(self) -> int:
        pass

    @abc.abstractproperty
    def isDestroyed(self) -> bool:
        pass

    @abc.abstractproperty
    def isOnGround(self) -> bool:
        pass

    @abc.abstractproperty
    def inWorld(self) -> bool:
        pass

    @abc.abstractmethod
    def className(self) -> str:
        return self.__class__.__name__

    @abc.abstractmethod
    def baseCall(self, methodName: str, methodArgs: list[Any]) -> None:
        method: Optional[Callable] = getattr(self._base, methodName, None)
        if method is None:
            logger.warning(f'There is no method "{methodName}"')
            return

        method(*methodArgs)

    @abc.abstractmethod
    def cellCall(self, methodName: str, methodArgs: list[Any]) -> None:
        method: Optional[Callable] = getattr(self._cell, methodName, None)
        if method is None:
            logger.warning(f'There is no method "{methodName}"')
            return

        method(*methodArgs)

    @abc.abstractmethod
    def isPlayer(self) -> bool:
        pass

    @abc.abstractmethod
    def getComponent(self, componentName: str, all: bool):
        pass

    @abc.abstractmethod
    def fireEvent(self, eventName, *args):
        pass

    @abc.abstractmethod
    def registerEvent(self, eventName, callback):
        pass

    @abc.abstractmethod
    def deregisterEvent(self, eventName, callback):
        pass

    @abc.abstractmethod
    def onDestroy(self):
        pass

    @abc.abstractmethod
    def onEnterWorld(self):
        pass

    @abc.abstractmethod
    def onLeaveWorld(self):
        pass

    @abc.abstractmethod
    def onEnterSpace(self):
        pass

    @abc.abstractmethod
    def onLeaveSpace(self):
        pass


class IKBEClientEntityComponent(abc.ABC):
    """KBEngine client entity component API."""

    @abc.abstractproperty
    def owner(self) -> IKBEClientEntity:
        pass

    @abc.abstractproperty
    def ownerID(self) -> int:
        pass

    @abc.abstractproperty
    def name(self) -> str:
        pass

    @abc.abstractproperty
    def isDestroyed(self) -> bool:
        pass

    @abc.abstractmethod
    def onAttached(self, owner: IKBEClientEntity):
        pass

    @abc.abstractmethod
    def onDetached(self, owner: IKBEClientEntity):
        pass

    @abc.abstractmethod
    def onEnterworld(self):
        pass

    @abc.abstractmethod
    def onLeaveworld(self):
        pass

    @abc.abstractmethod
    def onGetBase(self):
        pass

    @abc.abstractmethod
    def onGetCell(self):
        pass

    @abc.abstractmethod
    def onLoseCell(self):
        pass


class IPluginEntity(abc.ABC):
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

    @abc.abstractproperty
    def isDestroyed(self) -> bool:
        pass

    @classmethod
    @abc.abstractmethod
    def get_implementation(cls) -> Optional[Type[IPluginEntity]]:
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

    @abc.abstractmethod
    def __update_properties__(self, properties: dict[str, Any]):
        """Update property of the entity.

        The method is only using by message handlers. It's not supposed
        to call the method from the game logic layer.
        """
        pass

    @abc.abstractmethod
    def __remote_call__(self, msg: IMessage):
        """Call the server remote method of the entity.

        The method is only using by message handlers. It's not supposed
        to call the method from the game logic layer.
        """
        pass

    @abc.abstractmethod
    def __on_remote_call__(self, method_name: str, arguments: list) -> None:
        """The callback fires when method has been called on the server.

        The method is only using by message handlers. It's not supposed
        to call the method from the game logic layer.
        """
        pass


class IEntity(IPluginEntity, IKBEClientEntity):
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
