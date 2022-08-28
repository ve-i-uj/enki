"""Entity message handlers."""

import dataclasses
import logging
import sys
from dataclasses import dataclass
from typing import ClassVar, Dict, Any, Optional, Type

from enki import descr, kbeenum, kbetype, kbeclient, dcdescr
from enki import kbeentity, settings
from enki.app.entitymgr import EntityMgr
from enki.misc import devonly
from enki.dcdescr import EntityDesc
from enki.interface import IEntity, IEntityMgr

from enki.app.handlers import base

logger = logging.getLogger(__name__)

_SAVE_MSG_TEMPL = 'There is NO entity "{entity_id}". Save the message to handle it in the future.'

@dataclass
class _GetEntityIDResult:
    entity_id: int
    data: memoryview


@dataclass
class PoseData:
    x: float = sys.float_info.max
    y: float = sys.float_info.max
    z: float = sys.float_info.max
    yaw: float = sys.float_info.max
    pitch: float = sys.float_info.max
    roll: float = sys.float_info.max

    @property
    def position(self) -> kbetype.Position:
        return kbetype.Position(self.x, self.y, self.z)

    @property
    def direction(self) -> kbetype.Direction:
        return kbetype.Direction(self.roll, self.pitch, self.yaw)


class EntityHandler(base.IHandler):

    def __init__(self, entity_mgr: EntityMgr):
        self._entity_mgr = entity_mgr

    def get_entity_id(self, data: memoryview) -> _GetEntityIDResult:
        entity_id, offset = kbetype.ENTITY_ID.decode(data)
        data = data[offset:]

        return _GetEntityIDResult(entity_id, data)

    def set_pose(self, entity_id: int, pose_data: PoseData):
        entity = self._entity_mgr.get_entity(entity_id)
        assert entity.is_initialized
        pose_data.x = pose_data.x if pose_data.x != sys.float_info.max \
            else entity.position.x
        pose_data.y = pose_data.y if pose_data.y != sys.float_info.max \
            else entity.position.y
        pose_data.z = pose_data.z if pose_data.z != sys.float_info.max \
            else entity.position.z
        pose_data.yaw = pose_data.yaw if pose_data.yaw != sys.float_info.max \
            else entity.direction.yaw
        pose_data.pitch = pose_data.pitch if pose_data.pitch != sys.float_info.max \
            else entity.direction.pitch
        pose_data.roll = pose_data.roll if pose_data.roll != sys.float_info.max \
            else entity.direction.roll

        entity.__update_properties__({
            'position': pose_data.position,
            'direction': pose_data.direction,
        })

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'


class _OptimizedHandlerMixin:
    _entity_mgr: IEntityMgr

    def get_optimized_entity_id(self, data: memoryview) -> _GetEntityIDResult:
        if not descr.kbenginexml.root.cellapp.aliasEntityID \
                or not self._entity_mgr.can_entity_aliased():
            entity_id, offset = kbetype.INT32.decode(data)
            data = data[offset:]
            return _GetEntityIDResult(entity_id, data)

        alias_id, offset = kbetype.UINT8.decode(data)
        data = data[offset:]
        entity = self._entity_mgr.get_entity_by(alias_id)

        return _GetEntityIDResult(entity.id, data)


@dataclass
class OnUpdatePropertysParsedData(base.ParsedMsgData):
    entity_id: int
    properties: Dict[str, Any]


@dataclass
class OnUpdatePropertysHandlerResult(base.HandlerResult):
    result: OnUpdatePropertysParsedData
    msg_id: int = descr.app.client.onUpdatePropertys.id


class OnUpdatePropertysHandler(EntityHandler):

    def handle(self, msg: kbeclient.Message) -> OnUpdatePropertysHandlerResult:
        """Handler of `onUpdatePropertys`."""
        logger.debug(f'[{self}] ({devonly.func_args_values()})')
        data: memoryview = msg.get_values()[0]

        res = self.get_entity_id(data)
        entity_id = res.entity_id
        data = res.data

        entity = self._entity_mgr.get_entity(entity_id)
        if not entity.is_initialized:
            entity.add_pending_msg(msg)
            return OnUpdatePropertysHandlerResult(
                success=False,
                result=OnUpdatePropertysParsedData(settings.NO_ENTITY_ID, {}),
                text=_SAVE_MSG_TEMPL.format(entity_id=entity.id)
            )

        parsed_data = OnUpdatePropertysParsedData(
            entity_id=entity_id,
            properties={}
        )
        entity_desc = descr.entity.DESC_BY_UID[entity.CLS_ID]
        while data:
            if descr.kbenginexml.root.cellapp.entitydefAliasID \
                    and len(entity_desc.property_desc_by_id) <= 255:
                component_uid, shift = kbetype.UINT8.decode(data)
                data = data[shift:]
                property_uid, shift = kbetype.UINT8.decode(data)
                data = data[shift:]
            else:
                component_uid, shift = kbetype.UINT16.decode(data)
                data = data[shift:]
                property_uid, shift = kbetype.UINT16.decode(data)
                data = data[shift:]

            prop_id = component_uid or property_uid
            assert prop_id != 0, 'There is NO id of the property'

            type_spec = entity_desc.property_desc_by_id[prop_id]
            value, shift = type_spec.kbetype.decode(data)
            data = data[shift:]

            if isinstance(getattr(entity, type_spec.name), kbeentity.EntityComponent):
                # Это значит,то свойство на самом деле компонент (т.е. отдельный тип)
                ec_data: kbetype.EntityComponentData = value
                comp_desc = descr.entity.DESC_BY_UID[value.component_ent_id]
                while ec_data.count > 0:
                    if descr.kbenginexml.root.cellapp.entitydefAliasID \
                            and len(comp_desc.property_desc_by_id) <= 255:
                        _component_uid, shift = kbetype.UINT8.decode(data)
                        data = data[shift:]
                        property_uid, shift = kbetype.UINT8.decode(data)
                        data = data[shift:]
                    else:
                        _component_uid, shift = kbetype.UINT16.decode(data)
                        data = data[shift:]
                        property_uid, shift = kbetype.UINT16.decode(data)
                        data = data[shift:]
                    type_spec = comp_desc.property_desc_by_id[property_uid]
                    v, shift = type_spec.kbetype.decode(data)
                    data = data[shift:]
                    ec_data.properties[type_spec.name] = v
                    ec_data.count -= 1
                    # ec_data is value variable

            parsed_data.properties[type_spec.name] = value

        entity.__update_properties__(parsed_data.properties)

        return OnUpdatePropertysHandlerResult(
            success=True,
            result=parsed_data
        )


@dataclass
class OnUpdatePropertysOptimizedHandlerResult(OnUpdatePropertysHandlerResult):
    msg_id: int = descr.app.client.onUpdatePropertysOptimized.id


class OnUpdatePropertysOptimizedHandler(OnUpdatePropertysHandler,
                                        _OptimizedHandlerMixin):

    def get_entity_id(self, data: memoryview) -> _GetEntityIDResult:
        return self.get_optimized_entity_id(data)

    def handle(self, msg: kbeclient.Message) -> OnUpdatePropertysHandlerResult:
        res = super().handle(msg)
        return OnUpdatePropertysOptimizedHandlerResult(
            success=True,
            result=res.result
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
    result: OnCreatedProxiesParsedData
    msg_id: int = descr.app.client.onCreatedProxies.id


class OnCreatedProxiesHandler(EntityHandler):

    def handle(self, msg: kbeclient.Message) -> OnCreatedProxiesHandlerResult:
        parsed_data = OnCreatedProxiesParsedData(*msg.get_values())
        try:
            entity = self._entity_mgr.initialize_entity(
                entity_id=parsed_data.entity_id,
                entity_cls_name=parsed_data.cls_name
            )
        except kbeentity.EntityMgrError as err:
            return OnCreatedProxiesHandlerResult(
                success=False,
                result=parsed_data,
                text=err.args[0]
            )

        self._entity_mgr.set_player(entity.id)

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
    result: OnRemoteMethodCallParsedData
    msg_id: int = descr.app.client.onRemoteMethodCall.id


class OnRemoteMethodCallHandler(EntityHandler):

    def handle(self, msg: kbeclient.Message) -> OnRemoteMethodCallHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        data: memoryview = msg.get_values()[0]
        entity_id, offset = kbetype.ENTITY_ID.decode(data)
        data = data[offset:]

        entity = self._entity_mgr.get_entity(entity_id)
        entity_desc = descr.entity.DESC_BY_UID[entity.CLS_ID]

        if entity_desc.is_optimized_cl_method_uid:
            # componentPropertyAliasID
            component_prop_id, offset = kbetype.UINT8.decode(data)
            data = data[offset:]
        else:
            component_prop_id, offset = kbetype.UINT16.decode(data)
            data = data[offset:]

        ent_component = None
        if component_prop_id != settings.NO_ID:
            # It's a component remote method call. The call address to
            # the entity property. Get descriptsion of this property.
            comp_prop_desc = entity_desc.property_desc_by_id[component_prop_id]
            ent_component: kbeentity.EntityComponent = getattr(entity, comp_prop_desc.name)
            # It's an instance of the component-entity (e.g "Test" entity in the demo)
            assert ent_component and isinstance(ent_component, kbeentity.EntityComponent)
            entity_desc: EntityDesc = descr.entity.DESC_BY_NAME[ent_component.className()]

        if entity_desc.is_optimized_cl_method_uid:
            method_id, offset = kbetype.UINT8.decode(data)
            data = data[offset:]
        else:
            method_id, offset = kbetype.UINT16.decode(data)
            data = data[offset:]

        method_desc = entity_desc.client_methods[method_id]

        arguments = []
        for kbe_type in method_desc.kbetypes:
            value, offset = kbe_type.decode(data)
            data = data[offset:]
            arguments.append(value)

        if ent_component is None:
            entity.__on_remote_call__(method_desc.name, arguments)
        else:
            ent_component.__on_remote_call__(method_desc.name, arguments)

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
    result: OnEntityDestroyedParsedData
    msg_id: int = descr.app.client.onEntityDestroyed.id


class OnEntityDestroyedHandler(EntityHandler):

    def handle(self, msg: kbeclient.Message) -> OnEntityDestroyedHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        entity_id = msg.get_values()[0]
        entity = self._entity_mgr.get_entity(entity_id)

        entity.__update_properties__({
            'isDestroyed': True,
        })
        self._entity_mgr.on_entity_destroyed(entity.id)

        return OnEntityDestroyedHandlerResult(
            success=True,
            result=OnEntityDestroyedParsedData(entity_id)
        )


@dataclass
class OnEntityEnterWorldParsedData(base.ParsedMsgData):
    entity_id: int = 0
    entity_type_id: int = 0
    isOnGround: bool = False


@dataclass
class OnEntityEnterWorldHandlerResult(base.HandlerResult):
    result: OnEntityEnterWorldParsedData
    msg_id: int = descr.app.client.onEntityEnterWorld.id


class OnEntityEnterWorldHandler(EntityHandler):

    def handle(self, msg: kbeclient.Message) -> OnEntityEnterWorldHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        data = msg.get_values()[0]
        entity_id, offset = kbetype.ENTITY_ID.decode(data)
        data = data[offset:]

        entity = self._entity_mgr.get_entity(entity_id)
        if not entity.is_initialized:
            entity.add_pending_msg(msg)
            return OnEntityEnterWorldHandlerResult(
                success=False,
                result=OnEntityEnterWorldParsedData(),
                text=_SAVE_MSG_TEMPL.format(entity_id=entity.id)
            )

        if descr.kbenginexml.root.cellapp.entitydefAliasID \
                and len(descr.entity.DESC_BY_NAME) <= 255:
            entity_type_id, offset = kbetype.UINT8.decode(data)
            data = data[offset:]
        else:
            entity_type_id, offset = kbetype.UINT16.decode(data)
            data = data[offset:]

        isOnGround = False  # noqa
        if data:
            isOnGround, offset = kbetype.BOOL.decode(data)
            data = data[offset:]

        entity: IEntity = self._entity_mgr.get_entity(entity_id)
        if not entity.isPlayer():
            # The proxy entity (aka player) is initialized while onCreatedProxies
            self._entity_mgr.initialize_entity(
                entity_id, descr.entity.DESC_BY_UID[entity_type_id].name
            )
        entity.__update_properties__({'isOnGround': isOnGround})
        entity.onEnterWorld()
        entity.on_enter_world()

        return OnEntityEnterWorldHandlerResult(
            success=True,
            result=OnEntityEnterWorldParsedData(entity_id, entity_type_id, isOnGround)
        )


@dataclass
class OnSetEntityPosAndDirParsedData(base.ParsedMsgData):
    entity_id: int
    position: kbetype.Position
    direction: kbetype.Direction


@dataclass
class OnSetEntityPosAndDirHandlerResult(base.HandlerResult):
    result: OnSetEntityPosAndDirParsedData
    msg_id: int = descr.app.client.onSetEntityPosAndDir.id


class OnSetEntityPosAndDirHandler(EntityHandler):

    def handle(self, msg: kbeclient.Message) -> OnSetEntityPosAndDirHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        data: memoryview = msg.get_values()[0]
        entity_id, offset = kbetype.ENTITY_ID.decode(data)

        position = kbetype.Position()
        position.x, offset = kbetype.FLOAT.decode(data)
        data = data[offset:]
        position.y, offset = kbetype.FLOAT.decode(data)
        data = data[offset:]
        position.z, offset = kbetype.FLOAT.decode(data)
        data = data[offset:]

        direction = kbetype.Direction()
        direction.x, offset = kbetype.FLOAT.decode(data)
        data = data[offset:]
        direction.y, offset = kbetype.FLOAT.decode(data)
        data = data[offset:]
        direction.z, offset = kbetype.FLOAT.decode(data)
        data = data[offset:]

        pd = OnSetEntityPosAndDirParsedData(
            entity_id, position, direction
        )

        entity: IEntity = self._entity_mgr.get_entity(entity_id)
        entity.__update_properties__({
            'position': pd.position,
            'direction': pd.direction,
        })
        return OnSetEntityPosAndDirHandlerResult(
            success=True,
            result=pd
        )


@dataclass
class OnEntityEnterSpaceParsedData(base.ParsedMsgData):
    entity_id: int
    space_id: int
    isOnGround: bool


@dataclass
class OnEntityEnterSpaceHandlerResult(base.HandlerResult):
    result: OnEntityEnterSpaceParsedData
    msg_id: int = descr.app.client.onEntityEnterSpace.id


class OnEntityEnterSpaceHandler(EntityHandler):

    def handle(self, msg: kbeclient.Message) -> OnEntityEnterSpaceHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        data: memoryview = msg.get_values()[0]
        entity_id, offset = kbetype.ENTITY_ID.decode(data)
        data = data[offset:]

        space_id, offset = kbetype.SPACE_ID.decode(data)
        data = data[offset:]

        isOnGround = False
        if data:
            isOnGround, offset = kbetype.BOOL.decode(data)
            data = data[offset:]

        pd = OnEntityEnterSpaceParsedData(entity_id, space_id, isOnGround)

        entity = self._entity_mgr.get_entity(entity_id)
        entity.onEnterSpace()

        return OnEntityEnterSpaceHandlerResult(True, pd)


@dataclass
class OnUpdateBasePosParsedData(base.ParsedMsgData):
    position: kbetype.Position


@dataclass
class OnUpdateBasePosHandlerResult(base.HandlerResult):
    result: OnUpdateBasePosParsedData
    msg_id: int = descr.app.client.onUpdateBasePos.id


class OnUpdateBasePosHandler(EntityHandler):

    def handle(self, msg: kbeclient.Message) -> OnUpdateBasePosHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        entity = self._entity_mgr.get_player()

        pd = OnUpdateBasePosParsedData(
            kbetype.Position(*msg.get_values())
        )

        entity.__update_properties__({'position': pd.position})

        return OnUpdateBasePosHandlerResult(True, pd)


@dataclass
class OnUpdateBasePosXZParsedData(base.ParsedMsgData):
    x: float
    z: float


@dataclass
class OnUpdateBasePosXZHandlerResult(base.HandlerResult):
    result: OnUpdateBasePosXZParsedData
    msg_id: int = descr.app.client.onUpdateBasePosXZ.id


class OnUpdateBasePosXZHandler(EntityHandler):

    def handle(self, msg: kbeclient.Message) -> OnUpdateBasePosXZHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        entity = self._entity_mgr.get_player()
        pd = OnUpdateBasePosXZParsedData(*msg.get_values())

        entity.__update_properties__({
            'position': kbetype.Position(pd.x, entity.position.x, pd.z)
        })

        return OnUpdateBasePosXZHandlerResult(True, pd)


@dataclass
class _PoseParsedData(base.ParsedMsgData):
    pass


@dataclass
class _PoseHandlerResult(base.HandlerResult):
    result: _PoseParsedData
    msg_id: int = settings.NO_ID


class _PoseHandlerBase(EntityHandler, _OptimizedHandlerMixin):
    _parsed_data_cls: ClassVar[Type[_PoseParsedData]]
    _handler_result_cls: ClassVar[Type[_PoseHandlerResult]]

    def get_entity_id(self, data: memoryview) -> _GetEntityIDResult:
        return self.get_optimized_entity_id(data)

    def handle(self, msg: kbeclient.Message) -> _PoseHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        data = msg.get_values()[0]
        res = self.get_entity_id(data)
        data = res.data
        entity = self._entity_mgr.get_entity(res.entity_id)

        values = []
        for _ in range(len(dataclasses.fields(self._parsed_data_cls))):
            value, offset = kbetype.FLOAT.decode(data)
            data = data[offset:]
            values.append(value)
        pd = self._parsed_data_cls(*values)

        pose_data = PoseData(**{
            f.name: getattr(pd, f.name) for f
            in dataclasses.fields(self._parsed_data_cls)
        })
        self.set_pose(entity.id, pose_data)

        return self._handler_result_cls(True, pd)


@dataclass
class OnUpdateData_XZ_ParsedData(_PoseParsedData):
    x: float
    z: float


@dataclass
class OnUpdateData_XZ_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_XZ_ParsedData
    msg_id: int = descr.app.client.onUpdateData_xz.id


class OnUpdateData_XZ_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_XZ_ParsedData
    _handler_result_cls = OnUpdateData_XZ_HandlerResult


@dataclass
class OnUpdateData_YPR_ParsedData(_PoseParsedData):
    yaw: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_YPR_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_YPR_ParsedData
    msg_id: int = descr.app.client.onUpdateData_ypr.id


class OnUpdateData_YPR_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_YPR_ParsedData
    _handler_result_cls = OnUpdateData_YPR_HandlerResult


@dataclass
class OnUpdateData_YP_ParsedData(_PoseParsedData):
    yaw: float
    pitch: float


@dataclass
class OnUpdateData_YP_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_YP_ParsedData
    msg_id: int = descr.app.client.onUpdateData_yp.id


class OnUpdateData_YP_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_YP_ParsedData
    _handler_result_cls = OnUpdateData_YP_HandlerResult


@dataclass
class OnUpdateData_YR_ParsedData(_PoseParsedData):
    yaw: float
    roll: float


@dataclass
class OnUpdateData_YR_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_YR_ParsedData
    msg_id: int = descr.app.client.onUpdateData_yr.id


class OnUpdateData_YR_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_YR_ParsedData
    _handler_result_cls = OnUpdateData_YR_HandlerResult


@dataclass
class OnUpdateData_PR_ParsedData(_PoseParsedData):
    pitch: float
    roll: float


@dataclass
class OnUpdateData_PR_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_PR_ParsedData
    msg_id: int = descr.app.client.onUpdateData_pr.id


class OnUpdateData_PR_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_PR_ParsedData
    _handler_result_cls = OnUpdateData_PR_HandlerResult


@dataclass
class OnUpdateData_Y_ParsedData(_PoseParsedData):
    yaw: float


@dataclass
class OnUpdateData_Y_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_Y_ParsedData
    msg_id: int = descr.app.client.onUpdateData_y.id


class OnUpdateData_Y_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_Y_ParsedData
    _handler_result_cls = OnUpdateData_Y_HandlerResult


@dataclass
class OnUpdateData_P_ParsedData(_PoseParsedData):
    pitch: float


@dataclass
class OnUpdateData_P_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_P_ParsedData
    msg_id: int = descr.app.client.onUpdateData_p.id


class OnUpdateData_P_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_P_ParsedData
    _handler_result_cls = OnUpdateData_P_HandlerResult


@dataclass
class OnUpdateData_R_ParsedData(_PoseParsedData):
    roll: float


@dataclass
class OnUpdateData_R_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_R_ParsedData
    msg_id: int = descr.app.client.onUpdateData_r.id


class OnUpdateData_R_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_R_ParsedData
    _handler_result_cls = OnUpdateData_R_HandlerResult


@dataclass
class OnUpdateData_XZ_YPR_ParsedData(_PoseParsedData):
    x: float
    z: float
    yaw: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_XZ_YPR_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_XZ_YPR_ParsedData
    msg_id: int = descr.app.client.onUpdateData_xz_ypr.id


class OnUpdateData_XZ_YPR_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_XZ_YPR_ParsedData
    _handler_result_cls = OnUpdateData_XZ_YPR_HandlerResult


@dataclass
class OnUpdateData_XZ_YP_ParsedData(_PoseParsedData):
    x: float
    z: float
    yaw: float
    pitch: float


@dataclass
class OnUpdateData_XZ_YP_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_XZ_YP_ParsedData
    msg_id: int = descr.app.client.onUpdateData_xz_yp.id


class OnUpdateData_XZ_YP_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_XZ_YP_ParsedData
    _handler_result_cls = OnUpdateData_XZ_YP_HandlerResult


@dataclass
class OnUpdateData_XZ_YR_ParsedData(_PoseParsedData):
    x: float
    z: float
    yaw: float
    roll: float


@dataclass
class OnUpdateData_XZ_YR_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_XZ_YR_ParsedData
    msg_id: int = descr.app.client.onUpdateData_xz_ypr.id


class OnUpdateData_XZ_YR_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_XZ_YR_ParsedData
    _handler_result_cls = OnUpdateData_XZ_YR_HandlerResult


@dataclass
class OnUpdateData_XZ_PR_ParsedData(_PoseParsedData):
    x: float
    z: float
    yaw: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_XZ_PR_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_XZ_PR_ParsedData
    msg_id: int = descr.app.client.onUpdateData_xz_pr.id


class OnUpdateData_XZ_PR_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_XZ_PR_ParsedData
    _handler_result_cls = OnUpdateData_XZ_PR_HandlerResult


@dataclass
class OnUpdateData_XZ_Y_ParsedData(_PoseParsedData):
    x: float
    z: float
    yaw: float


@dataclass
class OnUpdateData_XZ_Y_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_XZ_Y_ParsedData
    msg_id: int = descr.app.client.onUpdateData_xz_y.id


class OnUpdateData_XZ_Y_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_XZ_Y_ParsedData
    _handler_result_cls = OnUpdateData_XZ_Y_HandlerResult


@dataclass
class OnUpdateData_XZ_P_ParsedData(_PoseParsedData):
    x: float
    z: float
    pitch: float


@dataclass
class OnUpdateData_XZ_P_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_XZ_P_ParsedData
    msg_id: int = descr.app.client.onUpdateData_xz_p.id


class OnUpdateData_XZ_P_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_XZ_P_ParsedData
    _handler_result_cls = OnUpdateData_XZ_P_HandlerResult


@dataclass
class OnUpdateData_XZ_R_ParsedData(_PoseParsedData):
    x: float
    z: float
    roll: float


@dataclass
class OnUpdateData_XZ_R_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_XZ_R_ParsedData
    msg_id: int = descr.app.client.onUpdateData_xz_r.id


class OnUpdateData_XZ_R_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_XZ_R_ParsedData
    _handler_result_cls = OnUpdateData_XZ_R_HandlerResult


@dataclass
class OnUpdateData_XYZ_ParsedData(_PoseParsedData):
    x: float
    z: float
    y: float


@dataclass
class OnUpdateData_XYZ_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_XYZ_ParsedData
    msg_id: int = descr.app.client.onUpdateData_xyz.id


class OnUpdateData_XYZ_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_XYZ_ParsedData
    _handler_result_cls = OnUpdateData_XYZ_HandlerResult


@dataclass
class OnUpdateData_XYZ_YPR_ParsedData(_PoseParsedData):
    x: float
    z: float
    y: float
    yaw: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_XYZ_YPR_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_XYZ_YPR_ParsedData
    msg_id: int = descr.app.client.onUpdateData_xyz_ypr.id


class OnUpdateData_XYZ_YPR_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_XYZ_YPR_ParsedData
    _handler_result_cls = OnUpdateData_XYZ_YPR_HandlerResult


@dataclass
class OnUpdateData_XYZ_YP_ParsedData(_PoseParsedData):
    x: float
    z: float
    y: float
    yaw: float
    pitch: float


@dataclass
class OnUpdateData_XYZ_YP_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_XYZ_YP_ParsedData
    msg_id: int = descr.app.client.onUpdateData_xyz_yp.id


class OnUpdateData_XYZ_YP_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_XYZ_YP_ParsedData
    _handler_result_cls = OnUpdateData_XYZ_YP_HandlerResult


@dataclass
class OnUpdateData_XYZ_YR_ParsedData(_PoseParsedData):
    x: float
    z: float
    y: float
    yaw: float
    pitch: float


@dataclass
class OnUpdateData_XYZ_YR_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_XYZ_YR_ParsedData
    msg_id: int = descr.app.client.onUpdateData_xyz_yr.id


class OnUpdateData_XYZ_YR_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_XYZ_YR_ParsedData
    _handler_result_cls = OnUpdateData_XYZ_YR_HandlerResult


@dataclass
class OnUpdateData_XYZ_PR_ParsedData(_PoseParsedData):
    x: float
    z: float
    y: float
    pitch: float
    roll: float


@dataclass
class OnUpdateData_XYZ_PR_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_XYZ_PR_ParsedData
    msg_id: int = descr.app.client.onUpdateData_xyz_pr.id


class OnUpdateData_XYZ_PR_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_XYZ_PR_ParsedData
    _handler_result_cls = OnUpdateData_XYZ_PR_HandlerResult


@dataclass
class OnUpdateData_XYZ_Y_ParsedData(_PoseParsedData):
    x: float
    z: float
    y: float
    yaw: float


@dataclass
class OnUpdateData_XYZ_Y_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_XYZ_Y_ParsedData
    msg_id: int = descr.app.client.onUpdateData_xyz_y.id


class OnUpdateData_XYZ_Y_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_XYZ_Y_ParsedData
    _handler_result_cls = OnUpdateData_XYZ_Y_HandlerResult


@dataclass
class OnUpdateData_XYZ_P_ParsedData(_PoseParsedData):
    x: float
    z: float
    y: float
    pitch: float


@dataclass
class OnUpdateData_XYZ_P_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_XYZ_P_ParsedData
    msg_id: int = descr.app.client.onUpdateData_xyz_p.id


class OnUpdateData_XYZ_P_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_XYZ_P_ParsedData
    _handler_result_cls = OnUpdateData_XYZ_P_HandlerResult


@dataclass
class OnUpdateData_XYZ_R_ParsedData(_PoseParsedData):
    x: float
    z: float
    y: float
    pitch: float


@dataclass
class OnUpdateData_XYZ_R_HandlerResult(_PoseHandlerResult):
    result: OnUpdateData_XYZ_R_ParsedData
    msg_id: int = descr.app.client.onUpdateData_xyz_r.id


class OnUpdateData_XYZ_R_Handler(_PoseHandlerBase):
    _parsed_data_cls = OnUpdateData_XYZ_R_ParsedData
    _handler_result_cls = OnUpdateData_XYZ_R_HandlerResult


__all__ = [
    'EntityHandler',
    'OnCreatedProxiesHandler',
    'OnEntityEnterSpaceHandler',
    'OnSetEntityPosAndDirHandler',

    'OnUpdatePropertysHandler',
    'OnUpdatePropertysOptimizedHandler',

    'OnRemoteMethodCallHandler',
    'OnEntityDestroyedHandler',
    'OnEntityEnterWorldHandler',

    'OnUpdateBasePosHandler',
    'OnUpdateBasePosXZHandler',

    'OnUpdateData_YPR_Handler',
    'OnUpdateData_YP_Handler',
    'OnUpdateData_YR_Handler',
    'OnUpdateData_PR_Handler',
    'OnUpdateData_Y_Handler',
    'OnUpdateData_P_Handler',
    'OnUpdateData_R_Handler',

    'OnUpdateData_XZ_Handler',
    'OnUpdateData_XZ_YPR_Handler',
    'OnUpdateData_XZ_YP_Handler',
    'OnUpdateData_XZ_YR_Handler',
    'OnUpdateData_XZ_PR_Handler',
    'OnUpdateData_XZ_Y_Handler',
    'OnUpdateData_XZ_P_Handler',
    'OnUpdateData_XZ_R_Handler',

    'OnUpdateData_XYZ_Handler',
    'OnUpdateData_XYZ_YPR_Handler',
    'OnUpdateData_XYZ_YP_Handler',
    'OnUpdateData_XYZ_YR_Handler',
    'OnUpdateData_XYZ_PR_Handler',
    'OnUpdateData_XYZ_Y_Handler',
    'OnUpdateData_XYZ_P_Handler',
    'OnUpdateData_XYZ_R_Handler',

]
