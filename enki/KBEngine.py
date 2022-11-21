"""Реализация официального API KBEngine."""

from typing import Optional

from enki import layer, settings
from enki.kbeapi import IKBEClientGameEntity, IKBEClientKBEngineModule
from enki.app.gameentity import GameEntity, GameEntityComponent
from enki.app.thlayer import ThreadedGameLayer, ThreadedNetLayer, GameState


class _KBEngine(IKBEClientKBEngineModule):

    Entity = GameEntity
    EntityComponent = GameEntityComponent

    @property
    def _game(self) -> ThreadedGameLayer:
        return layer.get_game_layer()  # type: ignore

    @property
    def _game_state(self) -> GameState:
        return self._game.get_game_state()

    @property
    def _net(self) -> ThreadedNetLayer:
        return layer.get_net_layer()  # type: ignore

    @property
    def component(self) -> str:
        """Returns the component name."""
        return 'client'

    @property
    def entities(self) -> dict[int, GameEntity]:
        """Return a dictionary-like object that contains all entities."""
        return self._game_state.get_entities()

    @property
    def entity_uuid(self) -> int:
        """
        The uuid of the entity. Change the ID and entity to bind to this login.
        When using the heavy login function, the server compares this ID
        and determines the validity.
        """
        # TODO: [2022-11-21 10:46 burov_alexey@mail.ru]:
        # Это App._relogin_data.rnd_uuid в игре это ни к чему. Повторный логин
        # сделает приложение само. Но можно передавать при создании сущности.
        return settings.NO_ID

    @property
    def entity_id(self) -> int:
        """The ID of the entity controlled by the current client."""
        return self._game_state.get_player_id()

    @property
    def spaceID(self) -> int:
        """
        The ID of the Space where the entity controlled by the current
        client is located (also can be understood as the corresponding scene,
        room, and copy).
        """
        player = self.player()
        if player is None:
            return settings.NO_ID
        return player.spaceID

    def login(self, username: str, password: str):
        """Login account to KBEngine server.

        Note: If the plug-in and the UI layer use event interaction mode,
        do not call directly from the UI layer. Please trigger a "login" event
        to the plug-in. The event is accompanied by the data username and password.

        parameters:
            username	string, username.
            password	string, password.
        """
        self._net.call_login(username, password)

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
        self._net.call_create_account(username, password)

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
        # TODO: [2022-11-21 11:30 burov_alexey@mail.ru]:
        # Пока, думаю, он не нужен, т.к. перелогином должно заниматься
        # приложение, а не игровой слой.
        raise NotImplementedError

    def player(self) -> Optional[IKBEClientGameEntity]:
        """Gets the entity that the current client controls.

        return:
            Entity, return controlled entity, if it does not exist (e.g.: failed
            to connect to the server) returns null.
        """
        if self.entity_id is settings.NO_ENTITY_ID:
            return None
        return self._game_state.get_entities()[self.entity_id]

    def resetPassword(self, username: str):
        """Asks loginapp to reset the password of the account.

        The server will send a password reset email (usually the forgotten
        password function) to the email address to which the account is bound.

        parameters:
            username	string, username.
        """
        self._net.call_reset_password(username)

    def bindAccountEmail(self, emailaddress: str):
        """Requests Baseapp to bind the email address of the account.

        parameters:
        emailaddress	string, email address.
        """
        assert self.player() is not None, 'You need to login at first'
        self._net.call_bind_account_email(
            self.entity_id, self._game_state.get_password(), emailaddress
        )

    def newPassword(self, oldpassword: str, newpassword: str):
        """Requests to set a new password for the account.

        parameters:
            oldpassword	string, old password
            newpassword	string, new password
        """
        assert self.player() is not None
        self._net.call_set_new_password(self.entity_id, oldpassword, newpassword)

    def findEntity(self, entityID: int) -> Optional[IKBEClientGameEntity]:
        """Return the entity by id."""
        return self.entities.get(entityID)

    def getSpaceData(self, key: str) -> Optional[str]:
        """
        Gets the space data for the specified key.
        The space data is set by the user on the server through setSpaceData.

        parameters:
        key	string, a keyword

        returns:
        string, specifies the value at the key
        """
        if self.spaceID is settings.NO_ID:
            return None
        return self._game_state.space_data.get(self.spaceID, {}).get(key, None)


KBEngine = _KBEngine()
