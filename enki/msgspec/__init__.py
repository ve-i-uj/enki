"""Описания KBEngine-сообщений."""

from __future__ import annotations

from enki.kbeenum import ComponentType
from enki.msg.msg_descr import ComponentMsgSpecById, MsgDescr

from . import (
    baseapp,
    baseappmgr,
    cellapp,
    cellappmgr,
    client,
    dbmgr,
    interfaces,
    logger,
    loginapp,
    machine,
    supervisor,
)

# Для упрощённого доступа к описаниям здесь связывается энам компонента и
# маппинг спецификации сообщений

ClientMsgSpecByID = ComponentMsgSpecById(
    ComponentType.CLIENT, client.SPEC_BY_ID
)
MachineMsgSpecByID = ComponentMsgSpecById(
    ComponentType.MACHINE, machine.SPEC_BY_ID
)
LoggerMsgSpecByID = ComponentMsgSpecById(
    ComponentType.LOGGER, logger.SPEC_BY_ID
)
DBMgrMsgSpecByID = ComponentMsgSpecById(ComponentType.DBMGR, dbmgr.SPEC_BY_ID)
InterfacesMsgSpecByID = ComponentMsgSpecById(
    ComponentType.INTERFACES, interfaces.SPEC_BY_ID
)
BaseappMgrMsgSpecByID = ComponentMsgSpecById(
    ComponentType.BASEAPPMGR, baseappmgr.SPEC_BY_ID
)
CellappMgrMsgSpecByID = ComponentMsgSpecById(
    ComponentType.CELLAPPMGR, cellappmgr.SPEC_BY_ID
)
BaseappMsgSpecByID = ComponentMsgSpecById(
    ComponentType.BASEAPP, baseapp.SPEC_BY_ID
)
CellappMsgSpecByID = ComponentMsgSpecById(
    ComponentType.CELLAPP, cellapp.SPEC_BY_ID
)
LoginappMsgSpecByID = ComponentMsgSpecById(
    ComponentType.LOGINAPP, loginapp.SPEC_BY_ID
)

# Supervisor - это расширение компонента Machine и его протокола
_supervisor_spec_by_id = {}
_supervisor_spec_by_id.update(machine.SPEC_BY_ID)
_supervisor_spec_by_id.update(supervisor.SPEC_BY_ID)
SupervisorMsgSpecByID = ComponentMsgSpecById(
    ComponentType.SUPERVISOR, _supervisor_spec_by_id
)

_MSG_COMP_SPEC_BY_COMPONENT: dict[ComponentType, ComponentMsgSpecById] = {
    ComponentType.CLIENT: ClientMsgSpecByID,
    ComponentType.MACHINE: MachineMsgSpecByID,
    ComponentType.LOGGER: LoggerMsgSpecByID,
    ComponentType.DBMGR: DBMgrMsgSpecByID,
    ComponentType.INTERFACES: InterfacesMsgSpecByID,
    ComponentType.BASEAPPMGR: BaseappMgrMsgSpecByID,
    ComponentType.CELLAPPMGR: CellappMgrMsgSpecByID,
    ComponentType.BASEAPP: BaseappMsgSpecByID,
    ComponentType.CELLAPP: CellappMsgSpecByID,
    ComponentType.LOGINAPP: LoginappMsgSpecByID,
    ComponentType.SUPERVISOR: SupervisorMsgSpecByID,
}


def get_comp_msg_specs(comp_type: ComponentType) -> ComponentMsgSpecById:
    return _MSG_COMP_SPEC_BY_COMPONENT[comp_type]


def get_msg_descr_by_name(
    comp_type: ComponentType, name: str
) -> MsgDescr | None:
    msg_spec_by_id = _MSG_COMP_SPEC_BY_COMPONENT[comp_type].msg_spec_by_id
    for msg_descr in msg_spec_by_id.values():
        if msg_descr.short_name == name:
            return msg_descr

    return None
