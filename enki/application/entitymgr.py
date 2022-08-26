"""Entity manager."""

import logging
from typing import Type

from enki.application import interface
from enki import descr, kbeclient, dcdescr, settings
from enki import kbeentity
from enki.misc import devonly
from enki.interface import IEntity, IEntityMgr
from enki.kbeentity import Entity


logger = logging.getLogger(__name__)


class EntityMgr(IEntityMgr):
    """Entity manager."""

    def __init__(self, app: interface.IApp):
        self._entities: dict[int, IEntity] = {}
        self._app = app
        self._prematurely_msgs: dict[int, Entity] = {}
        self._player_id = settings.NO_ENTITY_ID
        self._initialized_entity_ids: list[int] = []

    def can_entity_aliased(self) -> bool:
        # Сущностей уже создано больше, чем может вместить один байт (uint8).
        # Оптимизация на id сущностей больше не возможна.
        return len(self._initialized_entity_ids) <= 255

    def get_entity_by(self, alias_id: int) -> IEntity:
        entity_id = self._initialized_entity_ids[alias_id]
        return self.get_entity(entity_id)

    def get_entity(self, entity_id: int) -> IEntity:
        """Get entity by id."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if self._entities.get(entity_id) is None:
            entity = kbeentity.Entity(entity_id, self)
            self._entities[entity_id] = entity
            logger.debug('[%s] There is NO entity "%s", not initialized entity'
                         ' will return', self, entity_id)
            return entity

        entity: IEntity = self._entities[entity_id]
        return entity

    def initialize_entity(self, entity_id: int, entity_cls_name: str
                          ) -> IEntity:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if descr.entity.DESC_BY_NAME.get(entity_cls_name) is None:
            msg = f'There is NO entity class name "{entity_cls_name}" ' \
                  f'(entity_id = {entity_id}). Check plugin generated code.'
            raise kbeentity.EntityMgrError(msg)
        desc = descr.entity.DESC_BY_NAME[entity_cls_name]

        assert desc.cls.get_implementation() is not None, \
            f'There is no implementation of "{desc.name}"'

        old_entity: IEntity = self.get_entity(entity_id)
        if old_entity.is_initialized:
            logger.warning(f'[{self}] The entity "{old_entity}" is already inititialized')
            return old_entity

        # There were property update messages before initialization one.
        # We need to replace the not initialized entity instance to instance
        # of class we know now. And then resend to self not handled messages
        # to update properties of the entity.
        ent_cls = desc.cls.get_implementation()
        entity: IEntity = ent_cls(entity_id, entity_mgr=self)  # type: ignore
        self._entities[entity_id] = entity

        if old_entity.get_pending_msgs():
            logger.debug('There are pending messages. Resend them ...')
            for msg in old_entity.get_pending_msgs():
                self._app.on_receive_msg(msg)
            old_entity.clean_pending_msgs()

        self._initialized_entity_ids.append(entity.id)
        return entity

    def destroy_entity(self, entity_id: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def get_player(self) -> IEntity:
        return self.get_entity(self._player_id)

    def set_player(self, entity_id: int):
        self._player_id = entity_id

    def is_player(self, entity_id: int) -> bool:
        return self._player_id == entity_id

    def remote_call(self, msg: kbeclient.Message):
        """Send remote call message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._app.send_message(msg)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(app={self._app})'
