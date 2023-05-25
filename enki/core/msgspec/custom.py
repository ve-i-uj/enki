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
    value = 99999999
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
    lenght=9,
    name='Enki::onLookApp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.COMPONENT_TYPE,
        kbetype.COMPONENT_ID,
        kbetype.INT8
    ),
    desc='Пользовательское сообщение фиксирующее ответ на ::lookApp'
)


SPEC_BY_ID = {
    onQueryLoad.id: onQueryLoad,
    onLookApp.id: onLookApp,
}
