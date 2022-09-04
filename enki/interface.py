"""Client interfaces."""

from __future__ import annotations
import abc
from dataclasses import dataclass
import logging
from typing import Any, Callable, ClassVar, Tuple, Iterator, List, Type, \
    Optional

from enki import kbetype

logger = logging.getLogger(__name__)


@dataclass
class IResult:
    success: bool
    result: Any
    text: str = ''


class IMessage(abc.ABC):
    """Wrapper around client-server communication data."""

    @property
    @abc.abstractmethod
    def id(self) -> int:
        """Message id (see messages_fixed_defaults.xml)."""
        pass

    @property
    @abc.abstractmethod
    def need_calc_length(self) -> bool:
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

    @abc.abstractmethod
    def on_end_receive_msg(self):
        pass


class IClient(abc.ABC):

    @abc.abstractmethod
    def set_msg_receiver(self, receiver: IMsgReceiver) -> None:
        """Set the receiver of message."""
        pass

    @abc.abstractmethod
    async def send(self, msg: IMessage) -> None:
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

    These properties, methods and callbacks is the user API.
    """

    @property
    @abc.abstractmethod
    def id(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def direction(self) -> kbetype.Direction:
        pass

    @property
    @abc.abstractmethod
    def position(self) -> kbetype.Position:
        pass

    @property
    @abc.abstractmethod
    def spaceID(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def isDestroyed(self) -> bool:
        pass

    @property
    @abc.abstractmethod
    def inWorld(self) -> bool:
        pass

    @abc.abstractmethod
    def className(self) -> str:
        return self.__class__.__name__

    @abc.abstractmethod
    def baseCall(self, methodName: str, methodArgs: list[Any]) -> None:
        pass

    @abc.abstractmethod
    def cellCall(self, methodName: str, methodArgs: list[Any]) -> None:
        pass

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

    @property
    @abc.abstractmethod
    def owner(self) -> IKBEClientEntity:
        pass

    @property
    @abc.abstractmethod
    def ownerID(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def isDestroyed(self) -> bool:
        pass

    @abc.abstractmethod
    def onAttached(self, owner: IKBEClientEntity):
        pass

    @abc.abstractmethod
    def onDetached(self, owner: IKBEClientEntity):
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


class IPluginEntity(abc.ABC):
    """The entity interface of the plugin application."""
    CLS_ID: ClassVar[int]

    @property
    @abc.abstractmethod
    def id(self) -> int:
        pass

    # TODO: [2022-08-29 10:04 burov_alexey@mail.ru]:
    # Не понял, зачем нужно это значение, поэтому пока просто его сохранять.
    @property
    @abc.abstractmethod
    def is_on_ground(self) -> bool:
        pass

    @abc.abstractmethod
    def set_on_ground(self, value: bool):
        pass

    @property
    @abc.abstractmethod
    def cell(self) -> IEntityRemoteCall:
        pass

    @property
    @abc.abstractmethod
    def base(self) -> IEntityRemoteCall:
        pass

    @property
    @abc.abstractmethod
    def is_destroyed(self) -> bool:
        pass

    @property
    @abc.abstractmethod
    def is_initialized(self) -> bool:
        """The entity is ready to be used in the game."""
        pass

    @abc.abstractmethod
    def on_initialized(self):
        pass

    @abc.abstractmethod
    def on_destroyed(self):
        pass

    @abc.abstractmethod
    def on_enter_world(self):
        pass

    @abc.abstractmethod
    def on_leave_world(self):
        pass

    @abc.abstractmethod
    def on_enter_space(self):
        pass

    @abc.abstractmethod
    def on_leave_space(self):
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
    def can_use_alias_for_ent_id(self) -> bool:
        """
        The optimization is only applied to the first 255 entities.
        Further continue to read from int32.
        """
        pass

    @abc.abstractmethod
    def get_entity_by(self, alias_id: int) -> IEntity:
        pass

    @abc.abstractmethod
    def get_entity(self, entity_id: int) -> IEntity:
        """Get entity by id."""
        pass

    @abc.abstractmethod
    def initialize_entity(self, entity_id: int, entity_cls_name: str, is_player: bool) -> IEntity:
        pass

    @abc.abstractmethod
    def on_entity_leave_world(self, entity_id: int):
        pass

    @abc.abstractmethod
    def on_entity_destroyed(self, entity_id: int):
        pass

    @abc.abstractmethod
    def get_player(self) -> IEntity:
        """Return the proxy entity controlled by the client."""
        pass

    @abc.abstractmethod
    def set_player(self, entity_id: int):
        """Set the proxy entity controlled by the client."""
        pass

    @abc.abstractmethod
    def is_player(self, entity_id: int) -> bool:
        """The entity is controlled by the client."""
        pass

    @abc.abstractmethod
    def remote_call(self, msg: IMessage) -> None:
        """Send remote call message."""
        pass

    @abc.abstractmethod
    def set_relogin_data(self, rnd_uuid: int, entity_id: int):
        pass


class ICommand(abc.ABC):

    @abc.abstractmethod
    def execute(self) -> Any:
        pass


class IApp(IMsgReceiver):
    """Application interface."""

    @property
    @abc.abstractmethod
    def client(self) -> IClient:
        """The client connected to the server."""
        pass

    @abc.abstractmethod
    def send_message(self, msg: IMessage) -> None:
        """Send the message to the server."""
        pass

    @abc.abstractmethod
    def send_command(self, cmd: ICommand) -> Any:
        pass

    @abc.abstractmethod
    async def stop(self):
        """Stop the application."""
        pass

    @abc.abstractmethod
    async def start(self, account_name: str, password: str) -> IResult:
        """Start the application."""
        pass

    @abc.abstractmethod
    def set_relogin_data(self, rnd_uuid: int, entity_id: int):
        """Set data that is necessary for relogin of application."""
        pass
