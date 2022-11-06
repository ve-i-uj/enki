"""The API of KBEngine client plugin.

By official kbe documentation
<https://github.com/kbengine/kbengine/blob/master/docs/api/kbengine_api(en).chm>

"""

from typing import List, Dict, Optional, Callable, Tuple

from enki import kbetype, interface


class _KBEClientPluginAPI:

    class Entity(interface.IKBEClientEntity):

        @property
        def direction(self) -> kbetype.Direction:
            """This attribute describes the orientation of the Entity in world space.

            Data is synchronized from the server to the client.

            Type:
                Vector3, which contains (roll, pitch, yaw) in radians.
            """
            return kbetype.Direction()

        @property
        def id(self) -> int:
            """The entity id."""
            return 0

        @property
        def position(self) -> kbetype.Position:
            """The coordinates (x,y,z) of this entity in world space.

            The data is synchronized from the server to the client.
            """
            return kbetype.Position()

        @property
        def spaceID(self) -> int:
            """
            The ID of the Space where the entity controlled by the current
            client is located (also can be understood as the corresponding scene,
            room, and copy).
            """
            return 0

        @property
        def isOnGround(self) -> bool:
            """
            If the value of this attribute is True, the Entity is on the ground,
            otherwise it is False.

            If it is a client-controlled entity, this attribute will be synchronized
            to the server when changed, and other entities will be synchronized
            to the client by the server. The client can determine
            this value to avoid the overhead of accuracy.
            """
            return False

        @property
        def inWorld(self) -> bool:
            return False

        @property
        def className(self) -> str:
            """The class name of the entity."""
            return ''

        def baseCall(self, methodName: str, *methodArgs):
            """The method to call the base part of the entity.

            Note:
                The entity must have a base part on the server side.
                Only client entities controlled by the client can access this method.

            Example:
                entity.baseCall("reqCreateAvatar", roleType, name);

            parameters:
                methodName	string, method name.
                methodArgs	objects, method parameter list.
            """
            pass

        def cellCall(self, methodName: str, *methodArgs):
            """The method to call the cell part of this entity.

            Note:
                The entity must have a cell part on the server.
                Only client entities controlled by the client can access this method.

            Example:
                entity.cellCall("xxx", roleType, name);

            parameters:
                methodName	string, method name.
                methodArgs	objects, method parameter list.

            return:
                Because it is a remote call, it is not possible to block
                waiting for a return, so there is no return value.
            """
            pass

        def onDestroy(self):
            """
            Called when the entity is destroyed
            """
            pass

        def onEnterWorld(self):
            """
            If the entity is not client-controlled, it indicates that
            the entity has entered the view scope of the client-controlled entity
            on the server, at which point the client can see the entity.

            If the entity is client controlled, it indicates that
            the entity has created a cell on the server and entered the Space.
            """
            pass

        def onLeaveWorld(self):
            """
            If the entity is not client-controlled, it indicates that
            the entity has left the view scope of the client-controlled entity
            on the server side, and the client cannot see this entity at this time.

            If the entity is client controlled, it indicates that
            the entity has already destroyed the cell on the server and left the Space.
            """
            pass

        def onEnterSpace(self):
            """The client-controlled entity enters a new space."""
            pass

        def onLeaveSpace(self):
            """The client-controlled entity leaves the current space."""
            pass

        def isPlayer(self) -> bool:
            """Is the entity is the player controlled by the current client."""
            return False

        def getComponent(self, componentName: str, all: bool
                        ) -> List[interface.IKBEClientEntityComponent]:
            """Gets a component instance of the specified type attached to the entity.

            parameters:
                componentName	string, The component type name.
                all	bool, if True, Returns all instances of the same type
                    of component, otherwise only returns the first or empty list.
            """
            return []

        def fireEvent(self, eventName: str, *args):
            """Trigger entity events.

            parameters:
                eventName	string, the name of the event to trigger.
                args	The event datas to be attached, variable parameters.
            """
            pass

        def registerEvent(self, eventName: str, callback: Callable):
            """Register entity events.

            parameters:
                eventName	string, the name of the event to be registered
                    for listening.
                callback	The callback method used to respond to the event
                    when the event fires.
            """
            pass

        def deregisterEvent(self, eventName: str, callback: Callable):
            """Deregister entity events.

            parameters:
                eventName	string, the name of the event to be deregister.
                callback	The callback method to deregister of the listener.
            """
            pass

    @property
    def component(self) -> str:
        """Returns the component name."""
        return 'client'

    @property
    def entities(self) -> Dict[int, Entity]:
        """Return a dictionary-like object that contains all entities."""
        return {}

    @property
    def entity_uuid(self) -> int:
        """
        The uuid of the entity. Change the ID and entity to bind to this login.
        When using the heavy login function, the server compares this ID
        and determines the validity.
        """
        return 0

    @property
    def entity_id(self) -> int:
        """The ID of the entity controlled by the current client."""
        return 0

    @property
    def spaceID(self) -> int:
        """
        The ID of the Space where the entity controlled by the current
        client is located (also can be understood as the corresponding scene,
        room, and copy).
        """
        return 0

    def login(self, username: str, password: str):
        """Login account to KBEngine server.

        Note: If the plug-in and the UI layer use event interaction mode,
        do not call directly from the UI layer. Please trigger a "login" event
        to the plug-in. The event is accompanied by the data username and password.

        parameters:
            username	string, username.
            password	string, password.
        """
        pass


    def createAccount(self, username: str, password: str):
        """Request to create a login account on the KBEngine server.

        Note:
            If the plug-in and the UI layer use the event interaction mode,
            do not call directly from the UI layer. Please trigger
            a "createAccount" event to the plug-in. The event is accompanied
            by the data username and password.

        parameters:
            username	string, username.
            password	string, password.
        """
        pass


    def reloginBaseapp(self):
        """Requests to re-login to the KBEngine server

        Usually used after a dropped connection in order to connect
        to the server more quickly and continue to control the server role.

        Note:
            If the plug-in and the UI layer use event interaction mode,
            do not call directly from the UI layer, please trigger
            a "reloginBaseapp" event to the plug-in, and the incidental
            data is empty.
        """
        pass


    def player(self) -> Optional[Entity]:
        """Gets the entity that the current client controls.

        return:
            Entity, return controlled entity, if it does not exist (e.g.: failed
            to connect to the server) returns null.
        """
        pass


    def resetPassword(self, username: str):
        """Asks loginapp to reset the password of the account.

        The server will send a password reset email (usually the forgotten
        password function) to the email address to which the account is bound.

        parameters:
            username	string, username.
        """
        pass


    def bindAccountEmail(self, emailaddress: str):
        """Requests Baseapp to bind the email address of the account.

        parameters:
        emailaddress	string, email address.
        """
        pass


    def newPassword(self, oldpassword: str, newpassword: str):
        """Requests to set a new password for the account.

        parameters:
            oldpassword	string, old password
            newpassword	string, new password
        """
        pass


    def findEntity(self, entityID: int) -> Entity:
        """Return the entity by id."""
        return self.Entity()


    def getSpaceData(self, key: str) -> str:
        """
        Gets the space data for the specified key.
        The space data is set by the user on the server through setSpaceData.

        parameters:
        key	string, a keyword

        returns:
        string, specifies the value at the key
        """
        return ''


KBEngine = _KBEClientPluginAPI()
Entity = KBEngine.Entity


__all__ = ['KBEngine']
