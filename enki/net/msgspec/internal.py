"""The Logger component мessages (not generated)."""

from enki import kbeenum
from enki.net.kbeclient import kbetype
from enki.net.kbeclient.message import MsgDescr


def get_fake_msg_id_gen():
    """Возвращает уникальное значение для фэйкового сообщения.

    В ряде случаев компонент может отвечать не сообщением, а сразу отправлять
    поток данных. Чтобы его обрабатывать можно имитировать получение сообщения. Но для этого нужны пользовательски сообщения."""
    value = 99999999
    while True:
        value -= 1
        yield value


_gen = get_fake_msg_id_gen()
get_fake_msg_id = lambda: next(_gen)

fakeMsgDescr = MsgDescr(
    id=get_fake_msg_id(),
    lenght=0,
    name='Logger::queryLoad',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.UINT8_ARRAY,
    ),
    desc='The dummy message'
)


SPEC_BY_ID = {
    fakeMsgDescr.id: fakeMsgDescr,
}
