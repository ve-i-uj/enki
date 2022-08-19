"""Entity message handlers."""

import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional

from enki import descr, kbetype, kbeclient, dcdescr
from enki import kbeentity
from enki.misc import devonly

from damkina import entitymgr
from damkina.apphandler import base

logger = logging.getLogger(__name__)


class _EntityHandler(base.IHandler):

    def __init__(self, entity_mgr: entitymgr.EntityMgr):
        self._entity_mgr = entity_mgr

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'


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
        if isinstance(entity, entitymgr.NotInitializedEntity):
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
        while data:
            if entity_desc.is_optimized_prop_uid:
                component_uid, shift = kbetype.UINT8.decode(data)
                data = data[shift:]
                child_uid, shift = kbetype.UINT8.decode(data)
                data = data[shift:]
            else:
                component_uid, shift = kbetype.UINT16.decode(data)
                data = data[shift:]
                child_uid, shift = kbetype.UINT16.decode(data)
                data = data[shift:]

            prop_id = component_uid or child_uid
            assert prop_id != 0, 'There is NO id of the property'

            type_spec = entity_desc.property_desc_by_id[prop_id]
            value, shift = type_spec.kbetype.decode(data)
            data = data[shift:]

            parsed_data.properties[type_spec.name] = value

        entity.__update_properties__(parsed_data.properties)
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
        except kbeentity.EntityMgrError as err:
            return OnCreatedProxiesHandlerResult(
                success=False,
                result=parsed_data,
                text=err.args[0]
            )

        return OnCreatedProxiesHandlerResult(
            success=True,
            result=parsed_data
        )


@dataclass
class OnRemoteMethodCallParsedData(base.ParsedMsgData):
    entity_id: int
    method_name: str
    arguments: list


@dataclass
class OnRemoteMethodCallHandlerResult(base.HandlerResult):
    success: bool
    result: OnRemoteMethodCallParsedData
    msg_id: int = descr.app.client.onRemoteMethodCall.id
    text: Optional[str] = None


class OnRemoteMethodCallHandler(_EntityHandler):

    def handle(self, msg: kbeclient.Message) -> OnRemoteMethodCallHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        data: memoryview = msg.get_values()[0]
        entity_id, offset = kbetype.ENTITY_ID.decode(data)
        data = data[offset:]

        entity = self._entity_mgr.get_entity(entity_id)
        entity_desc = descr.entity.DESC_BY_UID[entity.CLS_ID]

        if entity_desc.is_optimized_cl_method_uid:
            _component_id, offset = kbetype.UINT8.decode(data)  # componentPropertyAliasID
            data = data[offset:]
            method_id, offset = kbetype.UINT8.decode(data)
        else:
            _component_id, offset = kbetype.UINT16.decode(data)  # componentPropertyAliasID
            data = data[offset:]
            method_id, offset = kbetype.UINT16.decode(data)
        data = data[offset:]

        method_desc = entity_desc.client_methods[method_id]
        arguments = []
        for kbe_type in method_desc.kbetypes:
            value, offset = kbe_type.decode(data)
            data = data[offset:]
            arguments.append(value)

        entity.__on_remote_call__(method_desc.name, arguments)

        parsed_data = OnRemoteMethodCallParsedData(
            entity_id=entity_id,
            method_name=method_desc.name,
            arguments=arguments
        )
        return OnRemoteMethodCallHandlerResult(
            success=True,
            result=parsed_data
        )


@dataclass
class OnEntityDestroyedParsedData(base.ParsedMsgData):
    entity_id: int


@dataclass
class OnEntityDestroyedHandlerResult(base.HandlerResult):
    success: bool
    result: OnEntityDestroyedParsedData
    msg_id: int = descr.app.client.onEntityDestroyed.id
    text: Optional[str] = None


class OnEntityDestroyedHandler(_EntityHandler):

    def handle(self, msg: kbeclient.Message) -> OnEntityDestroyedHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        entity_id = msg.get_values()
        return OnEntityDestroyedHandlerResult(
            success=True,
            result=OnEntityDestroyedParsedData(entity_id)
        )
