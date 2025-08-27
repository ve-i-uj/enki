"""Пользовательские сообщения (не сгенерированные)."""

import dataclasses
from collections.abc import Generator
from typing import Any, NoReturn

from enki.kbeenum import ComponentType
from enki.kbetype.decoders.basic_data_type_decoders import (
    BOOL,
    INT32,
    UINT8_ARRAY,
    UINT32,
    UINT64,
)
from enki.kbetype.decoders.custom_decoders import (
    COMPONENT_ID,
    COMPONENT_TYPE,
    SHUTDOWN_STATE,
)
from enki.msg.msg_descr import FIXED, MsgDescr


def change_component_owner(descr: MsgDescr, new_owner: ComponentType) -> MsgDescr:
    """Изменить владельца-компонента переданному описанию сообщения.

    Кроме фиксированных сообщений для каждого компонента в Enki вводятся
    ещё пользовательские сообщения, чтобы, описать формат ответа
    от компонента, когда ответ приходит в виде полей без id-сообщения. У такого
    сообщения могут быть разные компоненты-владельцы,
    но одинаковая сигнатура данных. Эта функция нужна, чтобы можно было
    динамически менять владельца в зависимости от того, чей ждём ответ.

    Пользовательского сообщения нет в KBEngine - это механизм для
    ответов именно этой библиотеки.
    Если нужно только описание сериализации, то настоящий id не нужен. Важно
    только, чтобы сериализатор сообщения мог найти описание [пользовательского]
    сообщения.
    """
    new_comp_name = new_owner.name.capitalize()
    dct = dataclasses.asdict(descr)
    dct["name"] = f"{new_comp_name}::{descr.short_name}"

    return MsgDescr(**dct)


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


def _get_fake_msg_id() -> int:
    """Возвращает уникальное значение для фэйкового сообщения.

    Returns:
        int: уникальное значение для фэйкового сообщения

    """
    return next(_gen)


onQueryLoad = MsgDescr(  # noqa: N816
    id=_get_fake_msg_id(),
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
    id=_get_fake_msg_id(),
    lenght=13,
    name="Enki::onLookApp",
    args_type=FIXED,
    args=(COMPONENT_TYPE, COMPONENT_ID, SHUTDOWN_STATE),
    desc="Пользовательское сообщение фиксирующее ответ на ::lookApp",
)

onReqCloseServer = MsgDescr(  # noqa: N816
    id=_get_fake_msg_id(),
    lenght=5,
    name="Enki::onReqCloseServer",
    args_type=FIXED,
    args=(BOOL,),
    desc="Пользовательское сообщение фиксирующее ответ на ::reqCloseServer",
)

onLookAppBaseapp = MsgDescr(  # noqa: N816
    id=_get_fake_msg_id(),
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
    id=_get_fake_msg_id(),
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
