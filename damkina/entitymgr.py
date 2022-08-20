"""Entity manager."""

import logging
from typing import Type

from damkina import interface
from enki import descr, kbeclient, dcdescr
from enki import kbeentity
from enki.misc import devonly
from enki.interface import IEntity

logger = logging.getLogger(__name__)


class EntityMgr(kbeentity.IEntityMgr):
    """Entity manager."""

    def __init__(self, app: interface.IApp):
        self._entities: dict[int, IEntity] = {}
        self._app = app

        self._prematurely_msgs: dict[int, IEntity] = {}

    def get_entity(self, entity_id: int) -> IEntity:
        """Get entity by id."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if self._entities.get(entity_id) is None:
            entity = kbeentity.Entity(entity_id, self)
            self._entities[entity_id] = entity
            logger.info(f'There is NO entity "{entity_id}". '
                        f'NotInitializedEntity will return.')
            return entity

        entity: IEntity = self._entities.get(entity_id)
        return entity

    def initialize_entity(self, entity_id: int, entity_cls_name: str
                          ) -> IEntity:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        desc: dcdescr.EntityDesc = descr.entity.DESC_BY_NAME.get(entity_cls_name)
        if desc is None:
            msg = f'There is NO entity class name "{entity_cls_name}" ' \
                  f'(entity_id = {entity_id}). Check plugin generated code.'
            raise kbeentity.EntityMgrError(msg)

        assert desc.cls.get_implementation(desc.cls) is not None, \
            f'There is no implementation of "{desc.name}"'

        old_entity: IEntity = self.get_entity(entity_id)
        assert old_entity.CLS_ID == 0, \
            f'The entity "{old_entity}" is already inititialized'

        # There were property update messages before initialization one.
        # We need to replace the not initialized entity instance to instance
        # of class we know now. And then resend to self not handled messages
        # to update properties of the entity.
        ent_cls = desc.cls.get_implementation(desc.cls)
        entity: IEntity = ent_cls(entity_id, entity_mgr=self)
        self._entities[entity_id] = entity

        if old_entity.get_pending_msgs():
            logger.debug('There are pending messages. Resend them ...')
            for msg in old_entity.get_pending_msgs():
                self._app.on_receive_msg(msg)
            old_entity.clean_pending_msgs()

        return entity

    def remote_call(self, msg: kbeclient.Message):
        """Send remote call message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._app.send_message(msg)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(app={self._app})'
