"""The API of KBEngine client plugin.

By official kbe documentation
<https://github.com/kbengine/kbengine/blob/master/docs/api/kbengine_api(en).chm>

"""

import abc

from typing import List, Dict, Optional, Callable, Tuple, Any


class _KBEClientPluginAPI:

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
        raise NotImplementedError

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
Entity = KBEngine.IEntity


__all__ = ['KBEngine']
