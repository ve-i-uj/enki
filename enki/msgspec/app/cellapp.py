"""Messages of the CellApp component.

These messages are predefined by the plugin (not generated).
"""

from enki import kbetype, dcdescr, kbeenum


onRemoteMethodCall = dcdescr.MessageDescr(
    id=302,
    lenght=-1,
    name='Entity::onRemoteMethodCall',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onLoseWitness = dcdescr.MessageDescr(
    id=44,
    lenght=-1,
    name='Entity::onLoseWitness',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.ENTITY_ID,
    ),
    desc=''
)

onGetWitnessFromBase = dcdescr.MessageDescr(
    id=43,
    lenght=-1,
    name='Entity::onGetWitnessFromBase',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.ENTITY_ID,
    ),
    desc=''
)

setPosition_XYZ_float = dcdescr.MessageDescr(
    id=42,
    lenght=14,
    name='Entity::setPosition_XYZ_float',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.ENTITY_ID,
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
    ),
    desc=''
)

setPosition_XZ_float = dcdescr.MessageDescr(
    id=41,
    lenght=12,
    name='Entity::setPosition_XZ_float',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.ENTITY_ID,
        kbetype.FLOAT,
        kbetype.FLOAT,
    ),
    desc=''
)

setPosition_XYZ_int = dcdescr.MessageDescr(
    id=40,
    lenght=-1,
    name='Entity::setPosition_XYZ_int',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.ENTITY_ID,
        kbetype.INT32,
        kbetype.INT32,
        kbetype.INT32,
    ),
    desc=''
)

setPosition_XZ_int = dcdescr.MessageDescr(
    id=39,
    lenght=-1,
    name='Entity::setPosition_XZ_int',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.ENTITY_ID,
        kbetype.INT32,
        kbetype.INT32,
    ),
    desc=''
)

