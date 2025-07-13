"""Пользовательские сообщения (не сгенерированные)."""

from typing import NoReturn, Generator
from enki import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr


# TODO: [burov_alexey@mail.ru 04.07.2025 07:33]
# Это должно быть не в объекте, а, например, отдельной функцией в модуле
# с общими сообщениями. Используется только в командах. Пока убираю.
# def change_component_owner(
#     self, comp_type: ComponentType, id: int | None = None
# ) -> MsgDescr:
#     """Изменить владельца-компонента этого сообщения.

#     Кроме фиксированных сообщений для каждого компонента в Enki вводятся
#     ещё пользовательские сообщения, чтобы, например, описать формат ответа
#     от компонента. У такого сообщения могут быть разные компоненты-владельцы,
#     но одинаковая сигнатура. Данный метод вводиться, чтобы можно было
#     динамически менять владельца в зависимости от того, чей ждём ответ.
#     """
#     _comp_name, msg_name = self.name.split("::")
#     new_comp_name = comp_type.name.capitalize()
#     dct = dataclasses.asdict(self)
#     dct["name"] = f"{new_comp_name}::{msg_name}"
#     if id is not None:
#         dct["id"] = id

#     return MsgDescr(**dct)


def get_fake_msg_id_gen() -> Generator[int, kbetype.Any, NoReturn]:
    """Генератор для уникального значения для фэйкового сообщения.

    В ряде случаев компонент может отвечать не сообщением, а сразу отправлять
    поток данных. Чтобы его обрабатывать можно имитировать получение сообщения.
    И для этого нужны пользовательские сообщения.
    """
    value = 59999
    while True:
        value -= 1
        yield value


_gen = get_fake_msg_id_gen()


def get_fake_msg_id() -> int:
    """Возвращает уникальное значение для фэйкового сообщения."""
    return next(_gen)


onQueryLoad = MsgDescr(
    id=get_fake_msg_id(),
    lenght=0,
    name="Enki::onQueryLoad",
    args_type=kbeenum.MsgArgsType.FIXED,
    args=(kbetype.UINT8_ARRAY,),
    desc="Пользовательское сообщение фиксирующее ответ на ::queryLoad",
)

onLookApp = MsgDescr(
    id=get_fake_msg_id(),
    lenght=13,
    name="Enki::onLookApp",
    args_type=kbeenum.MsgArgsType.FIXED,
    args=(kbetype.COMPONENT_TYPE, kbetype.COMPONENT_ID, kbetype.SHUTDOWN_STATE),
    desc="Пользовательское сообщение фиксирующее ответ на ::lookApp",
)

onReqCloseServer = MsgDescr(
    id=get_fake_msg_id(),
    lenght=5,
    name="Enki::onReqCloseServer",
    args_type=kbeenum.MsgArgsType.FIXED,
    args=tuple([kbetype.BOOL]),
    desc="Пользовательское сообщение фиксирующее ответ на ::reqCloseServer",
)

onLookAppBaseapp = MsgDescr(
    id=get_fake_msg_id(),
    lenght=13,
    name="Enki::onLookAppBaseapp",
    args_type=kbeenum.MsgArgsType.FIXED,
    args=(
        kbetype.COMPONENT_TYPE,
        kbetype.COMPONENT_ID,
        kbetype.SHUTDOWN_STATE,
        kbetype.UINT64,  # entitiesSize
        kbetype.INT32,  # numClients
        kbetype.INT32,  # numProxices
        kbetype.UINT32,  # port
    ),
    desc="Пользовательское сообщение фиксирующее ответ на Baseapp::lookApp",
)

onLookAppCellapp = MsgDescr(
    id=get_fake_msg_id(),
    lenght=13,
    name="Enki::onLookAppCellapp",
    args_type=kbeenum.MsgArgsType.FIXED,
    args=(
        kbetype.COMPONENT_TYPE,
        kbetype.COMPONENT_ID,
        kbetype.SHUTDOWN_STATE,
        kbetype.UINT64,  # entitiesSize
        kbetype.INT32,  # SpaceMemorys::size()
        kbetype.UINT32,  # port
    ),
    desc="Пользовательское сообщение фиксирующее ответ на Cellapp::lookApp",
)

SPEC_BY_ID = {
    onQueryLoad.id: onQueryLoad,
    onLookApp.id: onLookApp,
    onLookAppBaseapp.id: onLookAppBaseapp,
    onLookAppCellapp.id: onLookAppCellapp,
    onReqCloseServer.id: onReqCloseServer,
}
