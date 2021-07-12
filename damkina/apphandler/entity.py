"""Entity message handlers."""

import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional

from enki import descr, kbetype, kbeenum, kbeclient, interface
from enki.misc import devonly

from . import base

logger = logging.getLogger(__name__)


class NotInitializedEntity(descr.entity.Entity):

    def __init__(self, entity_id: int):
        super().__init__(entity_id)
        self._not_handled_messages: list[kbeclient.Message] = []

    def add_not_handled_message(self, msg: kbeclient.Message) -> None:
        self._not_handled_messages.append(msg)

    def get_not_handled_messages(self) -> list[kbeclient.Message]:
        return self._not_handled_messages[:]


class EntityMgrError(Exception):
    pass


class EntityMgr:
    """Entity manager."""

    # TODO: [07.07.2021 burov_alexey@mail.ru]:
    # Возможно должна быть какая-то другая структура модуля, чтобы можно было
    # не интерфейс указывать, а сам класс
    def __init__(self, receiver: interface.IMsgReceiver):
        self._entity: dict[int, descr.entity.Entity] = {}
        self._receiver = receiver

    def get_entity(self, entity_id: int) -> descr.entity.Entity:
        """Get entity by id."""
        if (entity := self._entity.get(entity_id)) is None:
            entity = NotInitializedEntity(entity_id)
            self._entity[entity_id] = entity
            logger.info(f'There is NO entity "{entity_id}". '
                        f'NotInitializedEntity will return.')
        return entity

    def initialize_entity(self, entity_id: int, entity_cls_name: str
                          ) -> descr.entity.Entity:
        desc: descr.entity.EntityDesc = descr.entity.DESC_BY_NAME.get(entity_cls_name)
        if desc is None:
            msg = f'There is NO entity class name "{entity_cls_name}" ' \
                  f'(entity_id = {entity_id}). Check plugin generated code.'
            raise EntityMgrError(msg)
        entity: descr.entity.Entity = desc.cls(entity_id)

        old_entity: NotInitializedEntity = self._entity.get(entity_id)
        if old_entity is None:
            # We got an initialization message before update messages.
            # No action needed.
            return entity

        # There were property update messages before initialization one.
        # We need to replace the not initialized entity instance to instance
        # of class we know now. And then resend to self not handled messages
        # to update properties of the entity.
        self._entity[entity_id] = entity
        not_handled_messages = old_entity.get_not_handled_messages()
        for msg in not_handled_messages:
            self._receiver.on_receive_msg(msg)

        return entity


class _EntityHandler(base.IHandler):

    def __init__(self, entity_mgr: EntityMgr):
        self._entity_mgr = entity_mgr


# *** onUpdatePropertys ***


@dataclass
class OnUpdatePropertysParsedData(base.ParsedMsgData):
    entity_id: int
    properties: Dict[str, Any]


@dataclass
class OnUpdatePropertysHandlerResult(base.HandlerResult):
    success: bool
    msg_id: int = descr.app.client.onUpdatePropertys.id
    result: Optional[OnUpdatePropertysParsedData] = None
    text: Optional[str] = None


class OnUpdatePropertysHandler(_EntityHandler):

    def handle(self, msg: kbeclient.Message) -> OnUpdatePropertysHandlerResult:
        """Handler of `onUpdatePropertys`."""
        logger.debug(f'[{self}] ({devonly.func_args_values()})')
        entity_id, data = msg.get_values()

        entity = self._entity_mgr.get_entity(entity_id)
        if isinstance(entity, NotInitializedEntity):
            entity.add_not_handled_message(msg)
            return OnUpdatePropertysHandlerResult(
                success=False,
                text=f'There is NO entity "{entity_id}". '
                     f'Store the message to handle it in the future.'
            )

        parsed_data = OnUpdatePropertysParsedData(
            entity_id=entity_id,
            properties={}
        )
        entity_desc = descr.entity.DESC_BY_UID[entity.CLS_ID]
        offset = 0
        while data:
            uid, shift = kbetype.UINT16.decode(data)
            data = data[shift:]
            offset += shift
            child_uid, shift = kbetype.UINT16.decode(data)
            data = data[shift:]
            offset += shift

            prop_id = uid or child_uid
            if prop_id == 0:
                logger.warning('There is NO id of the property')
                continue

            if uid == 0 and child_uid in kbeenum.PropertyUType.__members__:
                # It's dimension data
                child_uid = kbeenum.PropertyUType(child_uid)
                if child_uid == kbeenum.PropertyUType.POSITION_XYZ:
                    raise
                elif child_uid == kbeenum.PropertyUType.DIRECTION_ROLL_PITCH_YAW:
                    raise
                elif child_uid == kbeenum.PropertyUType.SPACE_ID:
                    space_id, shift = kbetype.SPACE_ID.decode(data)
                    data = data[shift:]
                    parsed_data.properties['space_id'] = space_id
                    continue

            type_spec = entity_desc.property_desc_by_id[prop_id]
            value, shift = type_spec.kbetype.decode(data)
            data = data[shift:]
            offset += shift

            parsed_data.properties[type_spec.name] = value
            # property_id, shift = kbetype.UINT16.decode(data)
            # data = data[shift:]
            # descr.deftype.TYPE_BY_ID[]

        return OnUpdatePropertysHandlerResult(
            success=True,
            result=parsed_data
        )


@dataclass
class OnCreatedProxiesParsedData(base.ParsedMsgData):
    # After each proxy is created, a uuid is generated by the system,
    # which is used for identification when the front-end re-login
    rnd_uuid: int
    entity_id: int
    cls_name: str  # the class name of the entity


@dataclass
class OnCreatedProxiesHandlerResult(base.HandlerResult):
    success: bool
    result: OnCreatedProxiesParsedData
    msg_id: int = descr.app.client.onCreatedProxies.id
    text: Optional[str] = None


class OnCreatedProxiesHandler(_EntityHandler):

    def handle(self, msg: kbeclient.Message) -> OnCreatedProxiesHandlerResult:
        parsed_data = OnCreatedProxiesParsedData(*msg.get_values())
        try:
            _entity = self._entity_mgr.initialize_entity(
                entity_id=parsed_data.entity_id,
                entity_cls_name=parsed_data.cls_name
            )
        except EntityMgrError as err:
            return OnCreatedProxiesHandlerResult(
                success=False,
                result=parsed_data,
                text=err.args[0]
            )
        return OnCreatedProxiesHandlerResult(
            success=True,
            result=parsed_data
        )
