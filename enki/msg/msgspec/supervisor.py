"""Сообщения компонента Supervisor."""

from enki.kbetype.decoders.custom_decoders import (
    BOOL,
    COMPONENT_ID,
    COMPONENT_TYPE,
    SHUTDOWN_STATE,
)
from enki.msg.msg_descr import FIXED, MsgDescr
from enki.msg.msgspec.custom import get_fake_msg_id

onStopComponent = MsgDescr(  # noqa: N816
    id=21001,
    lenght=10,
    name="Supervisor::onStopComponent",
    args_type=FIXED,
    args=(COMPONENT_ID,),
    desc="Уведомление, что компонент начал останавливаться",
)


onReqCloseServer = MsgDescr(  # noqa: N816
    id=get_fake_msg_id(),
    lenght=5,
    name="Supervisor::onReqCloseServer",
    args_type=FIXED,
    args=(BOOL,),
    desc="Пользовательское сообщение описывающие ответ на ::reqCloseServer",
)


lookApp = MsgDescr(  # noqa: N816
    id=10,
    lenght=-1,
    name="Machine::lookApp",
    args_type=FIXED,
    args=(),
    desc="Проверить, что компонент работает и отвечает (в ответ будет стрим с данными)",
)


onLookApp = MsgDescr(  # noqa: N816
    id=get_fake_msg_id(),
    lenght=13,
    name="Supervisor::onLookApp",
    args_type=FIXED,
    args=(COMPONENT_TYPE, COMPONENT_ID, SHUTDOWN_STATE),
    desc="Пользовательское сообщение фиксирующее ответ на Machine::lookApp",
)


SPEC_BY_ID = {
    lookApp.id: lookApp,
    onLookApp.id: onLookApp,
    onReqCloseServer.id: onReqCloseServer,
    onStopComponent.id: onStopComponent,
}

__all__ = [
    "SPEC_BY_ID",
    "lookApp",
    "onLookApp",
    "onReqCloseServer",
    "onStopComponent",
]
