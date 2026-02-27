"""Декодеры / энкодеры для данные message типов KBEngine."""

from __future__ import annotations

from typing import TypeAlias

from enki.kbetype.decoders.basic_data_type_decoders import *
from enki.kbetype.pytypes.basic_data_types import *

# TODO: [burov_alexey@mail.ru 06.07.2025 07:49]
# Модуль, возможно, стоит перенести в его предметную область. Где он будет
# расширять пакет.


# TODO: [burov_alexey@mail.ru 06.07.2025 05:43]
# Хз
# KBE_DATATYPE2ID_MAX: _TODOType = _TODOType("KBE_DATATYPE2ID_MAX")
# ENTITY_COMPONENT: _EntityComponent = _EntityComponent("ENTITY_COMPONENT")


# pylint: disable=invalid-name

# Id of type from types.xml
DATATYPE_UID: TypeAlias = UINT16

ENTITY_ID: TypeAlias = INT32
KBEEntityId: TypeAlias = KBEInt32

ENTITY_TYPE_NAME: TypeAlias = STRING
KBEEntityTypeName: TypeAlias = KBEString

# *** Application defined types ***

SPACE_ID: TypeAlias = UINT32
KBESpaceId: TypeAlias = KBEUInt32

SERVER_ERROR_CODE: TypeAlias = UINT16
KBEServerErrorCode: TypeAlias = KBEUInt16

ENTITY_PROPERTY_UID: TypeAlias = UINT16
ENTITY_METHOD_UID: TypeAlias = UINT16

# id типа компонента
COMPONENT_TYPE: TypeAlias = INT32
KBEComponentType: TypeAlias = KBEInt32

# id компонентов
COMPONENT_ID: TypeAlias = UINT64
KBEComponentId: TypeAlias = KBEUInt64

# TODO: [burov_alexey@mail.ru 13.07.2025 18:55]
# Хз что это
COMPONENT_ORDER: TypeAlias = INT32
KBEComponentOrderId: TypeAlias = KBEInt32

# TODO: [burov_alexey@mail.ru 13.07.2025 18:55]
# Хз что это
COMPONENT_GUS: TypeAlias = INT32
KBEComponentGusId: TypeAlias = KBEInt32

SHUTDOWN_STATE: TypeAlias = INT8
KBEShutdownState: TypeAlias = KBEInt8

GAME_TIME: TypeAlias = UINT32
KBEGameTime: TypeAlias = KBEUInt32

CALLBACK_ID: TypeAlias = UINT32
KBECallbackId: TypeAlias = KBEUInt32

ENTITY_SCRIPT_UID: TypeAlias = UINT16

DBID: TypeAlias = UINT64
KBEDbid: TypeAlias = KBEUInt64

UID_: TypeAlias = INT32
KBEUid_: TypeAlias = KBEInt32

USERNAME: TypeAlias = STRING
KBEUsername: TypeAlias = KBEString

INTADDR: TypeAlias = UINT32
KBEIntAddr: TypeAlias = KBEUInt32

INTPORT: TypeAlias = UINT16
KBEIntPort: TypeAlias = KBEUInt16

EXTADDREX: TypeAlias = STRING
KBEExtAddrEx: TypeAlias = KBEString

PID: TypeAlias = INT32
KBEPid: TypeAlias = KBEUInt32

CPU: TypeAlias = FLOAT
KBECpu: TypeAlias = KBEFloat

MEM: TypeAlias = FLOAT
KBEMem: TypeAlias = KBEFloat

USEDMEM: TypeAlias = UINT32
KBEUsedMem: TypeAlias = KBEUInt32

STATE: TypeAlias = INT8
KBEStateId: TypeAlias = KBEInt8

MACHINEID: TypeAlias = UINT32
KBEMachineId: TypeAlias = KBEUInt32

EXTRADATA: TypeAlias = UINT64
KBEExtraData: TypeAlias = KBEUInt64

MACMD5 = INT32
KBEMacMd5 = KBEInt32

MESSAGE_ID: TypeAlias = UINT16
KBEMessageId: TypeAlias = KBEUInt16

KBE_STREAM_ID: TypeAlias = INT16
KBEStreamId: TypeAlias = KBEInt16

KBEAccountType: TypeAlias = KBEUInt8
ACCOUNT_TYPE: TypeAlias = UINT8

# pylint: enable=invalid-name
