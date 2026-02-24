"""API of the KBEngine client plugin.

Based on the official KBEngine documentation:
https://github.com/kbengine/kbengine/blob/master/docs/api/kbengine_api(en).chm

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

if TYPE_CHECKING:
    from enki.vectors import Direction, Position


_E = TypeVar("_E", bound="IKBEClientEntity")
_CO = TypeVar("_CO", bound="IKBEClientEntityComponent")


class IKBEClientEntity(ABC, Generic[_CO]):
    """Interface for a KBEngine entity.

    Based on the official KBEngine documentation:
    https://github.com/kbengine/kbengine/blob/master/docs/api/kbengine_api(en).chm

    """

    @property
    @abstractmethod
    def direction(self) -> Direction:
        """Orientation of the entity in world space.

        Data is synchronized from the server to the client.

        Type:
            Vector3, containing (roll, pitch, yaw) in radians.

        """

    @property
    @abstractmethod
    def id(self) -> int:
        """Entity identifier."""

    @property
    @abstractmethod
    def position(self) -> Position:
        """Coordinates (x, y, z) of the entity in world space.

        Data is synchronized from the server to the client.

        """

    @property
    @abstractmethod
    def spaceID(self) -> int:  # noqa: N802
        """Identifier of the space where the entity is located.

        Can be understood as a scene, room, or instance.

        """

    @property
    @abstractmethod
    def isOnGround(self) -> bool:  # noqa: N802
        """Whether the entity is on the ground.

        For client-controlled entities, the value is synchronized to the server
        when changed. For other entities, it's synchronized from server to client.

        """

    @property
    @abstractmethod
    def inWorld(self) -> bool:  # noqa: N802
        """Whether the entity is in the world."""

    @property
    @abstractmethod
    def className(self) -> str:  # noqa: N802
        """Entity class name."""

    @property
    @abstractmethod
    def isDestroyed(self) -> bool:  # noqa: N802
        """Whether the entity is destroyed."""

    @abstractmethod
    def baseCall(self, methodName: str, methodArgs: list[Any]) -> None:
        """Call a method on the base part of the entity.

        Note:
            The entity must have a base part on the server.
            Only client-controlled entities can use this method.

        Example:
            entity.baseCall("reqCreateAvatar", roleType, name)

        Parameters
        ----------
        methodName : str
            Method name
        methodArgs : list[Any]
            List of method arguments

        """

    @abstractmethod
    def cellCall(self, methodName: str, methodArgs: list[Any]) -> None:
        """Call a method on the cell part of the entity.

        Note:
            The entity must have a cell part on the server.
            Only client-controlled entities can use this method.

        Example:
            entity.cellCall("attack", target_id, damage)

        Parameters
        ----------
        methodName : str
            Method name
        methodArgs : list[Any]
            List of method arguments

        Returns
        -------
        None
            Remote calls cannot block waiting for return, so no return value.

        """

    @abstractmethod
    def onDestroy(self) -> None:  # noqa: N802
        """Fire when the entity is destroyed."""

    @abstractmethod
    def onEnterWorld(self) -> None:  # noqa: N802
        """Fire when the entity enters the world.

        For non-client-controlled entities: indicates the entity has entered
        the view scope of the client-controlled entity on the server.

        For client-controlled entities: indicates the entity has created
        a cell on the server and entered the space.

        """

    @abstractmethod
    def onLeaveWorld(self) -> None:  # noqa: N802
        """Fire when the entity leaves the world.

        For non-client-controlled entities: indicates the entity has left
        the view scope of the client-controlled entity on the server.

        For client-controlled entities: indicates the entity has destroyed
        the cell on the server and left the space.

        """

    @abstractmethod
    def onEnterSpace(self) -> None:  # noqa: N802
        """Fire when the client-controlled entity enters a new space."""

    @abstractmethod
    def onLeaveSpace(self) -> None:  # noqa: N802
        """Fire when the client-controlled entity leaves the current space."""

    @abstractmethod
    def isPlayer(self) -> bool:  # noqa: N802
        """Check if the entity is the player controlled by the current client.

        Returns
        -------
        bool
            True if the entity is the player, False otherwise.

        """

    @abstractmethod
    def getComponent(  # noqa: N802
        self,
        componentName: str,  # noqa: N803
        all: bool,  # noqa: A002, FBT001
    ) -> list[_CO]:
        """Get component instances of the specified type attached to the entity.

        Parameters
        ----------
        componentName : str
            The component type name
        all : bool
            If True, returns all instances of the same type of component,
            otherwise returns only the first instance or empty list

        Returns
        -------
        list[IKBEClientGameEntityComponent]
            List of component instances

        """

    @abstractmethod
    def fireEvent(self, eventName: str, *args: Any) -> None:
        """Trigger entity events.

        Parameters
        ----------
        eventName : str
            Name of the event to trigger
        *args : Any
            Event data to be attached (variable parameters)

        """

    @abstractmethod
    def registerEvent(self, eventName: str, callback: Callable) -> None:
        """Register entity event listeners.

        Parameters
        ----------
        eventName : str
            Name of the event to listen for
        callback : Callable
            Callback method to execute when the event fires

        """

    @abstractmethod
    def deregisterEvent(self, eventName: str, callback: Callable) -> None:
        """Deregister entity event listeners.

        Parameters
        ----------
        eventName : str
            Name of the event to stop listening for
        callback : Callable
            Callback method to remove from event listeners

        """


class IKBEClientEntityComponent(ABC, Generic[_E]):
    """KBEngine client entity component API."""

    @property
    @abstractmethod
    def owner(self) -> _E:
        """Get the owner entity of this component.

        Returns
        -------
        IKBEClientGameEntity
            The entity that owns this component

        """

    @property
    @abstractmethod
    def ownerID(self) -> int:  # noqa: N802
        """Get the ID of the owner entity.

        Returns
        -------
        int
            ID of the entity that owns this component

        """

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this component.

        Returns
        -------
        str
            Component name

        """

    @property
    @abstractmethod
    def isDestroyed(self) -> bool:  # noqa: N802
        """Check if the component is destroyed.

        Returns
        -------
        bool
            True if destroyed, False otherwise

        """

    @abstractmethod
    def onAttached(self, owner: _E) -> None:  # noqa: N802
        """Fire when the component is attached to an entity.

        Parameters
        ----------
        owner : IKBEClientGameEntity
            The entity that this component is being attached to

        """

    @abstractmethod
    def onDetached(self, owner: _E) -> None:  # noqa: N802
        """Fire when the component is detached from an entity.

        Parameters
        ----------
        owner : IKBEClientGameEntity
            The entity that this component is being detached from

        """

    @abstractmethod
    def onEnterWorld(self) -> None:  # noqa: N802
        """Fire when the owner entity enters the world."""

    @abstractmethod
    def onLeaveWorld(self) -> None:  # noqa: N802
        """Fire when the owner entity leaves the world."""

    @abstractmethod
    def onEnterSpace(self) -> None:  # noqa: N802
        """Fire when the owner entity enters a space."""

    @abstractmethod
    def onLeaveSpace(self) -> None:  # noqa: N802
        """Fire when the owner entity leaves a space."""


class IKBEClientKBEngineModule(ABC, Generic[_E, _CO]):
    """The interface of the KBEngine module."""

    Entity: type[_E]
    EntityComponent: type[_CO]

    @property
    @abstractmethod
    def component(self) -> str:
        """Get the component name.

        Returns
        -------
        str
            Component name ("client")

        """

    @property
    @abstractmethod
    def entities(self) -> dict[int, _E]:
        """Get all entities in the client.

        Returns
        -------
        dict[int, IKBEClientGameEntity]
            Dictionary mapping entity IDs to entity instances

        """

    @property
    @abstractmethod
    def entity_uuid(self) -> int:
        """Get the UUID of the entity for login binding.

        When using the relogin functionality, the server compares this ID
        to determine validity.

        Returns
        -------
        int
            Entity UUID

        """

    @property
    @abstractmethod
    def entity_id(self) -> int:
        """Get the ID of the entity controlled by the current client.

        Returns
        -------
        int
            Controlled entity ID, or 0 if no entity is controlled

        """

    @property
    @abstractmethod
    def spaceID(self) -> int:  # noqa: N802
        """Get the ID of the space where the controlled entity is located.

        Returns
        -------
        int
            Space ID, or 0 if not in any space

        """

    @abstractmethod
    def login(self, username: str, password: str) -> None:
        """Login to the KBEngine server.

        Note: If using event interaction mode with the UI layer,
        trigger a "login" event instead of calling directly.

        Parameters
        ----------
        username : str
            Account username
        password : str
            Account password

        """

    @abstractmethod
    def createAccount(self, username: str, password: str) -> None:  # noqa: N802
        """Create a new account on the KBEngine server.

        Note: If using event interaction mode with the UI layer,
        trigger a "createAccount" event instead of calling directly.

        Parameters
        ----------
        username : str
            Desired username
        password : str
            Desired password

        """

    @abstractmethod
    def reloginBaseapp(self) -> None:  # noqa: N802
        """Re-login to the KBEngine server after connection loss.

        Used to reconnect to the server quickly and continue controlling
        the server character.

        Note: If using event interaction mode with the UI layer,
        trigger a "reloginBaseapp" event instead of calling directly.

        """

    @abstractmethod
    def player(self) -> _E | None:
        """Get the entity controlled by the current client.

        Returns
        -------
        IKBEClientGameEntity | None
            Controlled entity, or None if it doesn't exist
            (e.g., failed to connect to server)

        """

    @abstractmethod
    def resetPassword(self, username: str) -> None:  # noqa: N802
        """Request password reset for an account.

        The server will send a password reset email to the account's
        bound email address.

        Parameters
        ----------
        username : str
            Username of the account

        """

    @abstractmethod
    def bindAccountEmail(self, emailaddress: str) -> None:  # noqa: N802
        """Bind an email address to the account.

        Parameters
        ----------
        emailaddress : str
            Email address to bind

        """

    @abstractmethod
    def newPassword(self, oldpassword: str, newpassword: str) -> None:
        """Set a new password for the account.

        Parameters
        ----------
        oldpassword : str
            Current password
        newpassword : str
            New password

        """

    @abstractmethod
    def findEntity(self, entityID: int) -> _E | None:
        """Find an entity by its ID.

        Parameters
        ----------
        entityID : int
            Entity ID to search for

        Returns
        -------
        IKBEClientGameEntity | None
            Found entity, or None if not found

        """

    @abstractmethod
    def getSpaceData(self, key: str) -> str | None:  # noqa: N802
        """Get space data for the specified key.

        Space data is set by the user on the server through setSpaceData.

        Parameters
        ----------
        key : str
            Data key

        Returns
        -------
        str | None
            Value associated with the key, or None if key doesn't exist

        """
