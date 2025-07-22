"""Пользовательские сообщения (не сгенерированные)."""

from collections.abc import Generator
from typing import Any, NoReturn

from enki.kbetype.decoders.basic_data_type_decoders import INT32, UINT32, UINT64
from enki.kbetype.decoders.custom_decoders import (
    BOOL,
    COMPONENT_ID,
    COMPONENT_TYPE,
    SHUTDOWN_STATE,
    UINT8_ARRAY,
)
from enki.msg.msg_descr import FIXED, MsgDescr

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


def _get_fake_msg_id_gen() -> Generator[int, Any, NoReturn]:
    """Генератор для уникального значения для фэйкового сообщения.

    В ряде случаев компонент может отвечать не сообщением, а сразу отправлять
    поток данных. Чтобы его обрабатывать, можно имитировать ответное сообщения.
    Для этого нужны пользовательские сообщения, описывающие ответ.

    Yields:
        Generator[int, Any, NoReturn]: уникальное значение для фэйкового
            сообщения

    """
    value = 59999
    while True:
        value -= 1
        yield value


_gen = _get_fake_msg_id_gen()


def get_fake_msg_id() -> int:
    """Возвращает уникальное значение для фэйкового сообщения.

    Returns:
        int: уникальное значение для фэйкового сообщения

    """
    return next(_gen)


onQueryLoad = MsgDescr(  # noqa: N816
    id=get_fake_msg_id(),
    lenght=0,
    name="Enki::onQueryLoad",
    args_type=FIXED,
    args=(UINT8_ARRAY,),
    desc="Пользовательское сообщение фиксирующее ответ на ::queryLoad",
)

# TODO: [2025-07-22 07:50 burov_alexey@mail.ru]:
# Ответ на сообщение ::lookApp отправляется с разным содержанием у компонентов.
# Нужно каждому добавить свой этот ответ на сообщние.
onLookApp = MsgDescr(  # noqa: N816
    id=get_fake_msg_id(),
    lenght=13,
    name="Enki::onLookApp",
    args_type=FIXED,
    args=(COMPONENT_TYPE, COMPONENT_ID, SHUTDOWN_STATE),
    desc="Пользовательское сообщение фиксирующее ответ на ::lookApp",
)

onReqCloseServer = MsgDescr(  # noqa: N816
    id=get_fake_msg_id(),
    lenght=5,
    name="Enki::onReqCloseServer",
    args_type=FIXED,
    args=(BOOL,),
    desc="Пользовательское сообщение фиксирующее ответ на ::reqCloseServer",
)

onLookAppBaseapp = MsgDescr(  # noqa: N816
    id=get_fake_msg_id(),
    lenght=13,
    name="Enki::onLookAppBaseapp",
    args_type=FIXED,
    args=(
        COMPONENT_TYPE,
        COMPONENT_ID,
        SHUTDOWN_STATE,
        UINT64,  # entitiesSize
        INT32,  # numClients
        INT32,  # numProxices
        UINT32,  # port
    ),
    desc="Пользовательское сообщение фиксирующее ответ на Baseapp::lookApp",
)

onLookAppCellapp = MsgDescr(  # noqa: N816
    id=get_fake_msg_id(),
    lenght=13,
    name="Enki::onLookAppCellapp",
    args_type=FIXED,
    args=(
        COMPONENT_TYPE,
        COMPONENT_ID,
        SHUTDOWN_STATE,
        UINT64,  # entitiesSize
        INT32,  # SpaceMemorys::size()
        UINT32,  # port
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
