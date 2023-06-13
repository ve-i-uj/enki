"""The Logger component мessages (not generated)."""

from enki.core import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr


def get_fake_msg_id_gen():
    """Возвращает уникальное значение для фэйкового сообщения.

    В ряде случаев компонент может отвечать не сообщением, а сразу отправлять
    поток данных. Чтобы его обрабатывать можно имитировать получение сообщения.
    И для этого нужны пользовательски сообщения.
    """
    value = 59999
    while True:
        value -= 1
        yield value


_gen = get_fake_msg_id_gen()
get_fake_msg_id = lambda: next(_gen)

onQueryLoad = MsgDescr(
    id=get_fake_msg_id(),
    lenght=0,
    name='Enki::onQueryLoad',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT8_ARRAY,
    ),
    desc='Пользовательское сообщение фиксирующее ответ на ::queryLoad'
)

onLookApp = MsgDescr(
    id=get_fake_msg_id(),
    lenght=13,
    name='Enki::onLookApp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.COMPONENT_TYPE,
        kbetype.COMPONENT_ID,
        kbetype.SHUTDOWN_STATE
    ),
    desc='Пользовательское сообщение фиксирующее ответ на ::lookApp'
)

onLookAppBaseapp = MsgDescr(
    id=get_fake_msg_id(),
    lenght=13,
    name='Enki::onLookAppBaseapp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.COMPONENT_TYPE,
        kbetype.COMPONENT_ID,
        kbetype.SHUTDOWN_STATE,
        kbetype.UINT64,  # entitiesSize
        kbetype.INT32,  # numClients
        kbetype.INT32,  # numProxices
        kbetype.UINT32,  # port
    ),
    desc='Пользовательское сообщение фиксирующее ответ на Baseapp::lookApp'
)

onLookAppCellapp = MsgDescr(
    id=get_fake_msg_id(),
    lenght=13,
    name='Enki::onLookAppCellapp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.COMPONENT_TYPE,
        kbetype.COMPONENT_ID,
        kbetype.SHUTDOWN_STATE,
        kbetype.UINT64,  # entitiesSize
        kbetype.INT32,  # SpaceMemorys::size()
        kbetype.UINT32,  # port
    ),
    desc='Пользовательское сообщение фиксирующее ответ на Cellapp::lookApp'
)

SPEC_BY_ID = {
    onQueryLoad.id: onQueryLoad,
    onLookApp.id: onLookApp,
    onLookAppBaseapp.id: onLookAppBaseapp,
    onLookAppCellapp.id: onLookAppCellapp,
}
