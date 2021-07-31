"""Entity manager."""

import logging

from damkina import interface
from enki import descr, kbeentity, kbeclient, dcdescr
from enki.misc import devonly

logger = logging.getLogger(__name__)


class NotInitializedEntity(kbeentity.Entity):
    """Object to store unhandled messages."""

    def __init__(self, entity_id: int, entity_mgr: kbeentity.IEntityMgr):
        super().__init__(entity_id, entity_mgr)
        self._not_handled_messages: list[kbeclient.Message] = []

    def add_not_handled_message(self, msg: kbeclient.Message) -> None:
        self._not_handled_messages.append(msg)

    def get_not_handled_messages(self) -> list[kbeclient.Message]:
        return self._not_handled_messages[:]


class EntityMgr(kbeentity.IEntityMgr):
    """Entity manager."""

    # TODO: [07.07.2021 burov_alexey@mail.ru]:
    # Возможно должна быть какая-то другая структура модуля, чтобы можно было
    # не интерфейс указывать, а сам класс
    def __init__(self, app: interface.IApp):
        self._entities: dict[int, kbeentity.Entity] = {}
        self._app = app

    def get_entity(self, entity_id: int) -> kbeentity.Entity:
        """Get entity by id."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if (entity := self._entities.get(entity_id)) is None:
            entity = NotInitializedEntity(entity_id, self)
            self._entities[entity_id] = entity
            logger.info(f'There is NO entity "{entity_id}". '
                        f'NotInitializedEntity will return.')
        return entity

    def initialize_entity(self, entity_id: int, entity_cls_name: str
                          ) -> kbeentity.Entity:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        desc: dcdescr.EntityDesc = descr.entity.DESC_BY_NAME.get(entity_cls_name)
        if desc is None:
            msg = f'There is NO entity class name "{entity_cls_name}" ' \
                  f'(entity_id = {entity_id}). Check plugin generated code.'
            raise kbeentity.EntityMgrError(msg)
        entity: kbeentity.Entity = desc.cls(entity_id, entity_mgr=self)

        # TODO: [25.07.2021 burov_alexey@mail.ru]:
        # Что-то здесь логика мутновата. И с типами не пойми что.
        # Здесь должен прихдить NotInitializedEntity, но может же и не он.
        # Ну по смыслу: если есть, то это сто пудов NotInitializedEntity
        old_entity: NotInitializedEntity = self._entities.get(entity_id)
        self._entities[entity_id] = entity
        if old_entity is None:
            # We got an initialization message before update messages.
            # No action needed.
            return entity

        # There were property update messages before initialization one.
        # We need to replace the not initialized entity instance to instance
        # of class we know now. And then resend to self not handled messages
        # to update properties of the entity.
        logger.debug(f'Entity properties has been already received. '
                     f'Update entity.')
        not_handled_messages = old_entity.get_not_handled_messages()
        for msg in not_handled_messages:
            self._app.on_receive_msg(msg)

        return entity

    def remote_call(self, msg: kbeclient.Message):
        """Send remote call message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._app.send_message(msg)
