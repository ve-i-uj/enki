"""NetProxyEntity manager."""

from __future__ import annotations

import collections
import logging
from typing import Optional, Type

from enki import devonly, gedescr
from enki.gedescr import EntityDesc

from enki.net.msgspec import default_kbenginexml
from enki.net.kbeclient import Message
from enki.net.netentity import IEntityRPCSerializer

from enki.app.iapp import IApp

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


class EntityHelper:
    """Помогает находить описания, типы, id и т.д. сущностей."""

    def __init__(self, app: IApp,
                 entity_desc_by_uid: dict[int, gedescr.EntityDesc],
                 entity_serializer_by_uid: dict[int, Type[IEntityRPCSerializer]]):
        self._app = app
        self._entity_desc_by_uid: dict[int, EntityDesc] = entity_desc_by_uid
        self._entity_desc_by_name: dict[str, EntityDesc] = {
            d.name: d for d in entity_desc_by_uid.values()
        }
        self._entity_serializer_by_uid = entity_serializer_by_uid
        self._entity_id_by_alias_id = EnityIdByAliasId()

        self._pending_msgs_by_entity_id: dict[int, list[Message]] = collections.defaultdict(list)

        self._cls_name_by_entity_id: dict[int, str] = {}

    @property
    def is_entitydefAliasID(self) -> bool:
        return self.get_kbenginexml().cellapp.entitydefAliasID \
            and len(self._entity_desc_by_uid) <= 255

    @property
    def is_aliasEntityID(self) -> bool:
        return self.get_kbenginexml().cellapp.aliasEntityID \
            and self.can_use_alias_for_ent_id()

    def get_entity_descr_by_eid(self, entity_id: int) -> EntityDesc:
        cls_name = self.get_entity_cls_name_by_eid(entity_id)
        assert cls_name is not None
        return self.get_entity_descr_by_cls_name(cls_name)

    def get_entity_cls_name_by_eid(self, entity_id: int) -> Optional[str]:
        """Связывание id и типа сущности происходит только в момент создания.

        Поэтому нужно запоминать, какой id соответствует какому типу.
        """
        return self._cls_name_by_entity_id.get(entity_id)

    def get_entity_descr_by_uid(self, uid: int) -> EntityDesc:
        """Возвращает описание сущности по её уникальному идентификатору.

        Идентификатор задаётся на сервере и на клиенте становится известен
        во время кодогенерации.
        """
        assert self._entity_desc_by_uid.get(uid) is not None
        return self._entity_desc_by_uid[uid]

    def get_entity_descr_by_cls_name(self, name: str) -> EntityDesc:
        """Возвращает описание по имени типа сущности."""
        assert self._entity_desc_by_name.get(name) is not None
        return self._entity_desc_by_name[name]

    def get_kbenginexml(self) -> default_kbenginexml.root:
        return self._app.get_kbenginexml()

    def can_use_alias_for_ent_id(self) -> bool:
        # Сущностей уже создано больше, чем может вместить один байт (uint8).
        # Оптимизация на id сущностей больше не возможна.
        return not self._entity_id_by_alias_id.is_full()

    def get_entity_id_by(self, alias_id: int) -> int:
        return self._entity_id_by_alias_id.get_by(alias_id)

    def on_entity_created(self, entity_id: int, entity_cls_name: str, is_player: bool):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if is_player:
            self.set_player_id(entity_id)
        if not self.is_player(entity_id) and self.can_use_alias_for_ent_id():
            self._entity_id_by_alias_id.add_new(entity_id)

        self._cls_name_by_entity_id[entity_id] = entity_cls_name

    def on_entity_leave_world(self, entity_id: int):
        self._entity_id_by_alias_id.delete(entity_id)

    def on_entity_destroyed(self, entity_id: int):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        del self._cls_name_by_entity_id[entity_id]

    def get_player_id(self) -> int:
        return self._player_id

    def set_player_id(self, entity_id: int):
        self._player_id = entity_id

    def is_player(self, entity_id: int) -> bool:
        return self._player_id == entity_id

    def set_relogin_data(self, rnd_uuid: int, entity_id: int):
        self._app.set_relogin_data(rnd_uuid, entity_id)

    def add_pending_msg(self, entity_id: int, msg: Message):
        self._pending_msgs_by_entity_id[entity_id].append(msg)

    def get_pending_msgs(self, entity_id: int) -> list[Message]:
        return self._pending_msgs_by_entity_id[entity_id][:]

    def clean_pending_msgs(self, entity_id: int):
        self._pending_msgs_by_entity_id.pop(entity_id)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(app={self._app})'
