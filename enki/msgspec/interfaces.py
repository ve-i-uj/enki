"""The Interfaces component мessages (not generated)."""

from enki.kbetype import INT32, STRING, UINT16, UINT32
from enki.kbetype.decoders.custom_decoders import (
    COMPONENT_ID,
    COMPONENT_ORDER,
    COMPONENT_TYPE,
)
from enki.msg.msg_descr import FIXED, VARIABLE, MsgDescr

lookApp = MsgDescr(  # noqa: N816
    id=12,
    lenght=-1,
    name="Interfaces::lookApp",
    args_type=FIXED,
    args=(),
    desc="Check the component is alive",
)

onRegisterNewApp = MsgDescr(  # noqa: N816
    id=8,
    lenght=-1,
    name="Interfaces::onRegisterNewApp",
    args_type=FIXED,
    args=(
        INT32,  # uid
        STRING,  # username
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
        COMPONENT_ORDER,  # globalorderID
        COMPONENT_ORDER,  # grouporderID
        UINT32,  # intaddr
        UINT16,  # intport
        UINT32,  # extaddr
        UINT16,  # extport
        STRING,  # extaddrEx
    ),
    desc="???",
)

onAppActiveTick = MsgDescr(  # noqa: N816
    id=55104,
    lenght=12,
    name="Interfaces::onAppActiveTick",
    args_type=FIXED,
    args=(
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
    ),
    desc="Компонент сообщает, что он живой",
)

reqCloseServer = MsgDescr(  # noqa: N816
    id=13,
    lenght=-1,
    name="Interfaces::reqCloseServer",
    args_type=VARIABLE,
    args=(),
    desc="Отправить сигнал компоненту, что ему нужно остановиться",
)

SPEC_BY_ID = {
    lookApp.id: lookApp,
    onRegisterNewApp.id: onRegisterNewApp,
    reqCloseServer.id: reqCloseServer,
    onAppActiveTick.id: onAppActiveTick,
    # KBEngine одно и тоже сообщение гоняет, не меняя отправителя (скорей всего баг)
    55105: onAppActiveTick,
}

__all__ = [
    "SPEC_BY_ID",
    "lookApp",
    "onAppActiveTick",
    "onRegisterNewApp",
    "reqCloseServer",
]
