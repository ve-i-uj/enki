"""This generated module contains entity descriptions."""

from enki import kbeenum
from enki.kbeentity.entity_descr import EntityDesc, MethodDesc, PropertyDesc

from . import deftype

DESC_BY_UID = {
    1: EntityDesc(
        name='Account',
        uid=1,
        property_desc_by_id={
            40000: PropertyDesc(
                uid=40000,
                name='position',
                decoder=deftype.VECTOR3,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            40001: PropertyDesc(
                uid=40001,
                name='direction',
                decoder=deftype.VECTOR3,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            40002: PropertyDesc(
                uid=40002,
                name='spaceID',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.CELL_PRIVATE,
                alias_id=-1,
                component_type_name=''
            ),
            2: PropertyDesc(
                uid=2,
                name='lastSelCharacter',
                decoder=deftype.UINT64,
                distribution_flag=kbeenum.DistributionFlag.BASE_AND_CLIENT,
                alias_id=-1,
                component_type_name=''
            ),
        },
        client_methods={
            10005: MethodDesc(
                uid=10005,
                alias_id=-1,
                name='onCreateAvatarResult',
                decoders=[
                    deftype.UINT8,
                    deftype.AVATAR_INFOS,
                ]
            ),
            3: MethodDesc(
                uid=3,
                alias_id=-1,
                name='onRemoveAvatar',
                decoders=[
                    deftype.UINT64,
                ]
            ),
            10003: MethodDesc(
                uid=10003,
                alias_id=-1,
                name='onReqAvatarList',
                decoders=[
                    deftype.AVATAR_INFOS_LIST,
                ]
            ),
        },
        base_methods={
            10001: MethodDesc(
                uid=10001,
                alias_id=-1,
                name='reqAvatarList',
                decoders=[
                ]
            ),
            10002: MethodDesc(
                uid=10002,
                alias_id=-1,
                name='reqCreateAvatar',
                decoders=[
                    deftype.UINT8,
                    deftype.UNICODE,
                ]
            ),
            1: MethodDesc(
                uid=1,
                alias_id=-1,
                name='reqRemoveAvatar',
                decoders=[
                    deftype.UNICODE,
                ]
            ),
            2: MethodDesc(
                uid=2,
                alias_id=-1,
                name='reqRemoveAvatarDBID',
                decoders=[
                    deftype.UINT64,
                ]
            ),
            10004: MethodDesc(
                uid=10004,
                alias_id=-1,
                name='selectAvatarGame',
                decoders=[
                    deftype.UINT64,
                ]
            ),
        },
        cell_methods={
        },
    ),
    2: EntityDesc(
        name='Avatar',
        uid=2,
        property_desc_by_id={
            40000: PropertyDesc(
                uid=40000,
                name='position',
                decoder=deftype.VECTOR3,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            40001: PropertyDesc(
                uid=40001,
                name='direction',
                decoder=deftype.VECTOR3,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            40002: PropertyDesc(
                uid=40002,
                name='spaceID',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.CELL_PRIVATE,
                alias_id=-1,
                component_type_name=''
            ),
            47001: PropertyDesc(
                uid=47001,
                name='HP',
                decoder=deftype.INT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            47002: PropertyDesc(
                uid=47002,
                name='HP_Max',
                decoder=deftype.INT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            47003: PropertyDesc(
                uid=47003,
                name='MP',
                decoder=deftype.INT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            47004: PropertyDesc(
                uid=47004,
                name='MP_Max',
                decoder=deftype.INT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            16: PropertyDesc(
                uid=16,
                name='component1',
                decoder=deftype.ENTITY_COMPONENT,
                distribution_flag=kbeenum.DistributionFlag.COMPONENT_1,
                alias_id=-1,
                component_type_name='Test'
            ),
            21: PropertyDesc(
                uid=21,
                name='component2',
                decoder=deftype.ENTITY_COMPONENT,
                distribution_flag=kbeenum.DistributionFlag.COMPONENT_2,
                alias_id=-1,
                component_type_name='Test'
            ),
            22: PropertyDesc(
                uid=22,
                name='component3',
                decoder=deftype.ENTITY_COMPONENT,
                distribution_flag=kbeenum.DistributionFlag.COMPONENT_3,
                alias_id=-1,
                component_type_name='TestNoBase'
            ),
            47005: PropertyDesc(
                uid=47005,
                name='forbids',
                decoder=deftype.INT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            41002: PropertyDesc(
                uid=41002,
                name='level',
                decoder=deftype.UINT16,
                distribution_flag=kbeenum.DistributionFlag.CELL_PUBLIC_AND_OWN,
                alias_id=-1,
                component_type_name=''
            ),
            41006: PropertyDesc(
                uid=41006,
                name='modelID',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            41007: PropertyDesc(
                uid=41007,
                name='modelScale',
                decoder=deftype.UINT8,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            11: PropertyDesc(
                uid=11,
                name='moveSpeed',
                decoder=deftype.UINT8,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            41003: PropertyDesc(
                uid=41003,
                name='name',
                decoder=deftype.UNICODE,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            6: PropertyDesc(
                uid=6,
                name='own_val',
                decoder=deftype.UINT16,
                distribution_flag=kbeenum.DistributionFlag.OWN_CLIENT,
                alias_id=-1,
                component_type_name=''
            ),
            41001: PropertyDesc(
                uid=41001,
                name='spaceUType',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.CELL_PUBLIC_AND_OWN,
                alias_id=-1,
                component_type_name=''
            ),
            47006: PropertyDesc(
                uid=47006,
                name='state',
                decoder=deftype.INT8,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            47007: PropertyDesc(
                uid=47007,
                name='subState',
                decoder=deftype.UINT8,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            41004: PropertyDesc(
                uid=41004,
                name='uid',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            41005: PropertyDesc(
                uid=41005,
                name='utype',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
        },
        client_methods={
            10101: MethodDesc(
                uid=10101,
                alias_id=-1,
                name='dialog_addOption',
                decoders=[
                    deftype.UINT8,
                    deftype.UINT32,
                    deftype.UNICODE,
                    deftype.INT32,
                ]
            ),
            10104: MethodDesc(
                uid=10104,
                alias_id=-1,
                name='dialog_close',
                decoders=[
                ]
            ),
            10102: MethodDesc(
                uid=10102,
                alias_id=-1,
                name='dialog_setText',
                decoders=[
                    deftype.UNICODE,
                    deftype.UINT8,
                    deftype.UINT32,
                    deftype.UNICODE,
                ]
            ),
            12: MethodDesc(
                uid=12,
                alias_id=-1,
                name='onAddSkill',
                decoders=[
                    deftype.INT32,
                ]
            ),
            7: MethodDesc(
                uid=7,
                alias_id=-1,
                name='onJump',
                decoders=[
                ]
            ),
            13: MethodDesc(
                uid=13,
                alias_id=-1,
                name='onRemoveSkill',
                decoders=[
                    deftype.INT32,
                ]
            ),
            16: MethodDesc(
                uid=16,
                alias_id=-1,
                name='recvDamage',
                decoders=[
                    deftype.INT32,
                    deftype.INT32,
                    deftype.INT32,
                    deftype.INT32,
                ]
            ),
        },
        base_methods={
        },
        cell_methods={
            11003: MethodDesc(
                uid=11003,
                alias_id=-1,
                name='dialog',
                decoders=[
                    deftype.INT32,
                    deftype.UINT32,
                ]
            ),
            5: MethodDesc(
                uid=5,
                alias_id=-1,
                name='jump',
                decoders=[
                ]
            ),
            4: MethodDesc(
                uid=4,
                alias_id=-1,
                name='relive',
                decoders=[
                    deftype.UINT8,
                ]
            ),
            11: MethodDesc(
                uid=11,
                alias_id=-1,
                name='requestPull',
                decoders=[
                ]
            ),
            11001: MethodDesc(
                uid=11001,
                alias_id=-1,
                name='useTargetSkill',
                decoders=[
                    deftype.INT32,
                    deftype.INT32,
                ]
            ),
        },
    ),
    3: EntityDesc(
        name='Test',
        uid=3,
        property_desc_by_id={
            40000: PropertyDesc(
                uid=40000,
                name='position',
                decoder=deftype.VECTOR3,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            40001: PropertyDesc(
                uid=40001,
                name='direction',
                decoder=deftype.VECTOR3,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            40002: PropertyDesc(
                uid=40002,
                name='spaceID',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.CELL_PRIVATE,
                alias_id=-1,
                component_type_name=''
            ),
            18: PropertyDesc(
                uid=18,
                name='own',
                decoder=deftype.INT32,
                distribution_flag=kbeenum.DistributionFlag.CELL_PUBLIC_AND_OWN,
                alias_id=-1,
                component_type_name=''
            ),
            17: PropertyDesc(
                uid=17,
                name='state',
                decoder=deftype.INT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
        },
        client_methods={
            28: MethodDesc(
                uid=28,
                alias_id=-1,
                name='helloCB',
                decoders=[
                    deftype.INT32,
                ]
            ),
        },
        base_methods={
            27: MethodDesc(
                uid=27,
                alias_id=-1,
                name='say',
                decoders=[
                    deftype.INT32,
                ]
            ),
        },
        cell_methods={
            26: MethodDesc(
                uid=26,
                alias_id=-1,
                name='hello',
                decoders=[
                    deftype.INT32,
                ]
            ),
        },
    ),
    4: EntityDesc(
        name='TestNoBase',
        uid=4,
        property_desc_by_id={
            40000: PropertyDesc(
                uid=40000,
                name='position',
                decoder=deftype.VECTOR3,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            40001: PropertyDesc(
                uid=40001,
                name='direction',
                decoder=deftype.VECTOR3,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            40002: PropertyDesc(
                uid=40002,
                name='spaceID',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.CELL_PRIVATE,
                alias_id=-1,
                component_type_name=''
            ),
            24: PropertyDesc(
                uid=24,
                name='own',
                decoder=deftype.INT32,
                distribution_flag=kbeenum.DistributionFlag.CELL_PUBLIC_AND_OWN,
                alias_id=-1,
                component_type_name=''
            ),
            23: PropertyDesc(
                uid=23,
                name='state',
                decoder=deftype.INT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
        },
        client_methods={
            30: MethodDesc(
                uid=30,
                alias_id=-1,
                name='helloCB',
                decoders=[
                    deftype.INT32,
                ]
            ),
        },
        base_methods={
        },
        cell_methods={
            29: MethodDesc(
                uid=29,
                alias_id=-1,
                name='hello',
                decoders=[
                    deftype.INT32,
                ]
            ),
        },
    ),
    5: EntityDesc(
        name='Monster',
        uid=5,
        property_desc_by_id={
            40000: PropertyDesc(
                uid=40000,
                name='position',
                decoder=deftype.VECTOR3,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            40001: PropertyDesc(
                uid=40001,
                name='direction',
                decoder=deftype.VECTOR3,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            40002: PropertyDesc(
                uid=40002,
                name='spaceID',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.CELL_PRIVATE,
                alias_id=-1,
                component_type_name=''
            ),
            47001: PropertyDesc(
                uid=47001,
                name='HP',
                decoder=deftype.INT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            47002: PropertyDesc(
                uid=47002,
                name='HP_Max',
                decoder=deftype.INT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            47003: PropertyDesc(
                uid=47003,
                name='MP',
                decoder=deftype.INT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            47004: PropertyDesc(
                uid=47004,
                name='MP_Max',
                decoder=deftype.INT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            51007: PropertyDesc(
                uid=51007,
                name='entityNO',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            47005: PropertyDesc(
                uid=47005,
                name='forbids',
                decoder=deftype.INT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            41006: PropertyDesc(
                uid=41006,
                name='modelID',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            41007: PropertyDesc(
                uid=41007,
                name='modelScale',
                decoder=deftype.UINT8,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            32: PropertyDesc(
                uid=32,
                name='moveSpeed',
                decoder=deftype.UINT8,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            41003: PropertyDesc(
                uid=41003,
                name='name',
                decoder=deftype.UNICODE,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            47006: PropertyDesc(
                uid=47006,
                name='state',
                decoder=deftype.INT8,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            47007: PropertyDesc(
                uid=47007,
                name='subState',
                decoder=deftype.UINT8,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            41004: PropertyDesc(
                uid=41004,
                name='uid',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            41005: PropertyDesc(
                uid=41005,
                name='utype',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
        },
        client_methods={
            34: MethodDesc(
                uid=34,
                alias_id=-1,
                name='recvDamage',
                decoders=[
                    deftype.INT32,
                    deftype.INT32,
                    deftype.INT32,
                    deftype.INT32,
                ]
            ),
        },
        base_methods={
        },
        cell_methods={
        },
    ),
    6: EntityDesc(
        name='NPC',
        uid=6,
        property_desc_by_id={
            40000: PropertyDesc(
                uid=40000,
                name='position',
                decoder=deftype.VECTOR3,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            40001: PropertyDesc(
                uid=40001,
                name='direction',
                decoder=deftype.VECTOR3,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            40002: PropertyDesc(
                uid=40002,
                name='spaceID',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.CELL_PRIVATE,
                alias_id=-1,
                component_type_name=''
            ),
            51007: PropertyDesc(
                uid=51007,
                name='entityNO',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            41006: PropertyDesc(
                uid=41006,
                name='modelID',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            41007: PropertyDesc(
                uid=41007,
                name='modelScale',
                decoder=deftype.UINT8,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            43: PropertyDesc(
                uid=43,
                name='moveSpeed',
                decoder=deftype.UINT8,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            41003: PropertyDesc(
                uid=41003,
                name='name',
                decoder=deftype.UNICODE,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            41004: PropertyDesc(
                uid=41004,
                name='uid',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            41005: PropertyDesc(
                uid=41005,
                name='utype',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
        },
        client_methods={
        },
        base_methods={
        },
        cell_methods={
        },
    ),
    7: EntityDesc(
        name='Gate',
        uid=7,
        property_desc_by_id={
            40000: PropertyDesc(
                uid=40000,
                name='position',
                decoder=deftype.VECTOR3,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            40001: PropertyDesc(
                uid=40001,
                name='direction',
                decoder=deftype.VECTOR3,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            40002: PropertyDesc(
                uid=40002,
                name='spaceID',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.CELL_PRIVATE,
                alias_id=-1,
                component_type_name=''
            ),
            51007: PropertyDesc(
                uid=51007,
                name='entityNO',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            41006: PropertyDesc(
                uid=41006,
                name='modelID',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            41007: PropertyDesc(
                uid=41007,
                name='modelScale',
                decoder=deftype.UINT8,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            41003: PropertyDesc(
                uid=41003,
                name='name',
                decoder=deftype.UNICODE,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            41004: PropertyDesc(
                uid=41004,
                name='uid',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
            41005: PropertyDesc(
                uid=41005,
                name='utype',
                decoder=deftype.UINT32,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=-1,
                component_type_name=''
            ),
        },
        client_methods={
        },
        base_methods={
        },
        cell_methods={
        },
    ),
}

__all__ = ['DESC_BY_UID']