"""Entity manager."""

import logging
from types import ModuleType
from typing import Type

from enki import msgspec, kbeclient, settings, dcdescr
from enki.dcdescr import EntityDesc
from enki import kbeentity
from enki.misc import devonly
from enki.interface import IEntity, IEntityMgr, IApp, IKBEClientEntity
from enki.kbeentity import Entity

from enki.msgspec import default_kbenginexml

logger = logging.getLogger(__name__)


class EnityIdByAliasId:

    def __init__(self) -> None:
        self._initialized_entity_ids: list[int] = []

    def get_by(self, alias_id: int) -> int:
        """Получить идентификатор сущности по alias_id.

        Значение alias_id - это порядок вызова onCreatedProxies и сдвиг
        всех сущностей на -1 при onEntityLeaveWorld (т.е. из списка элемент
        удаляется). Player сущности (прокси) в алиасы не добавляются, т.к.
        сервер выделяет им id меньше 256 и идентификатор сущности умещается
        в один байт.
        """
        return self._initialized_entity_ids[alias_id]

    def add_new(self, entity_id: int):
        self._initialized_entity_ids.append(entity_id)

    def delete(self, entity_id: int):
        if entity_id not in self._initialized_entity_ids:
            logger.warning(f'[{self}] There is no entity id "{entity_id}"')
            return
        self._initialized_entity_ids.remove(entity_id)

    def is_full(self) -> bool:
        return len(self._initialized_entity_ids) > 255

    def is_empty(self) -> bool:
        return not self._initialized_entity_ids


class EntityMgr(IEntityMgr):
    """Entity manager."""

    def __init__(self, app: IApp,
                 entity_desc_by_uid: dict[int, dcdescr.EntityDesc],
                 entity_impl_by_uid: dict[int, Type[IEntity]]):
        self._app = app
        self._entity_desc_by_uid = entity_desc_by_uid
        self._entity_desc_by_name = {
            d.name: d for d in entity_desc_by_uid.values()
        }
        self._entity_impl_by_uid = entity_impl_by_uid

        self._entities: dict[int, IEntity] = {}
        self._prematurely_msgs: dict[int, IEntity] = {}
        self._player_id = settings.NO_ENTITY_ID
        # TODO: [2022-08-30 08:30 burov_alexey@mail.ru]:
        # Нужно что-то производительней, чем список с удалением и добавлением.
        # Поэтому пока добавил отдельный объект, чтобы удобней было реализацию
        # позже поменять.
        self._entity_id_by_alias_id = EnityIdByAliasId()

    @property
    def is_entitydefAliasID(self) -> bool:
        return self.get_kbenginexml().cellapp.entitydefAliasID \
            and len(self._entity_desc_by_uid) <= 255

    @property
    def is_aliasEntityID(self) -> bool:
        return self.get_kbenginexml().cellapp.aliasEntityID \
            and self.can_use_alias_for_ent_id()

    def get_entity_descr_by(self, uid: int) -> EntityDesc:
        assert self._entity_desc_by_uid.get(uid) is not None
        return self._entity_desc_by_uid[uid]

    def get_kbenginexml(self) -> default_kbenginexml.root:
        return self._app.get_kbenginexml()

    def can_use_alias_for_ent_id(self) -> bool:
        # Сущностей уже создано больше, чем может вместить один байт (uint8).
        # Оптимизация на id сущностей больше не возможна.
        return not self._entity_id_by_alias_id.is_full()

    def get_entity_by(self, alias_id: int) -> IEntity:
        entity_id = self._entity_id_by_alias_id.get_by(alias_id)
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

    def initialize_entity(self, entity_id: int, entity_cls_name: str,
                          is_player: bool) -> IEntity:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        assert self._entity_desc_by_name.get(entity_cls_name), \
            f'There is NO entity class name "{entity_cls_name}" ' \
            f'(entity_id = {entity_id}). Check plugin generated code.'
        desc = self._entity_desc_by_name[entity_cls_name]
        assert self._entity_impl_by_uid.get(desc.uid), \
            f'There is NO implementation of the "{entity_cls_name}" entity ' \
            f'(entity_id = {entity_id}).'
        ent_impl = self._entity_impl_by_uid[desc.uid]

        old_entity: IEntity = self.get_entity(entity_id)
        if old_entity.is_initialized:
            logger.warning(f'[{self}] The entity "{old_entity}" is already inititialized')
            return old_entity

        entity = ent_impl(entity_id, entity_mgr=self)  # type: ignore
        self._entities[entity_id] = entity
        if is_player:
            self.set_player(entity.id)
        entity.on_initialized()

        if not self.is_player(entity.id) and self.can_use_alias_for_ent_id():
            self._entity_id_by_alias_id.add_new(entity.id)

        # There were property update messages before initialization one.
        # We need to replace the not initialized entity instance to instance
        # of class we know now. And then resend to self not handled messages
        # to update properties of the entity.
        if old_entity.get_pending_msgs():
            logger.debug('There are pending messages. Resend them ...')
            for msg in old_entity.get_pending_msgs():
                self._app.on_receive_msg(msg)
            old_entity.clean_pending_msgs()

        return entity

    def on_entity_leave_world(self, entity_id: int):
        self._entity_id_by_alias_id.delete(entity_id)

    def on_entity_destroyed(self, entity_id: int):
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

    def set_relogin_data(self, rnd_uuid: int, entity_id: int):
        self._app.set_relogin_data(rnd_uuid, entity_id)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(app={self._app})'
