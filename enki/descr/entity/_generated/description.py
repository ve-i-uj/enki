"""This generated module contains entity descriptions."""

from .Account import AccountBase
from .Avatar import AvatarBase
from .Gate import GateBase
from .Monster import MonsterBase
from .NPC import NPCBase
from .Test import TestBase
from .TestNoBase import TestNoBaseBase

from enki import dcdescr, kbeenum
from enki.descr import deftype

DESC_BY_UID = {
    1: dcdescr.EntityDesc(
        name='Account',
        uid=1,
        cls=AccountBase,
        property_desc_by_id={
            1: dcdescr.PropertyDesc(
                uid=40000,
                name='position',
                kbetype=deftype.DIRECTION3D_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=1
            ),
            2: dcdescr.PropertyDesc(
                uid=40001,
                name='direction',
                kbetype=deftype.DIRECTION3D_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=2
            ),
            3: dcdescr.PropertyDesc(
                uid=40002,
                name='spaceID',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.CELL_PRIVATE,
                alias_id=3
            ),
            4: dcdescr.PropertyDesc(
                uid=2,
                name='lastSelCharacter',
                kbetype=deftype.UID_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.BASE_AND_CLIENT,
                alias_id=4
            ),
        },
        client_methods={
            1: dcdescr.MethodDesc(
                uid=10005,
                alias_id=1,
                name='onCreateAvatarResult',
                kbetypes=[
                    deftype.ENTITY_SUBSTATE_SPEC.kbetype,deftype.AVATAR_INFOS_SPEC.kbetype,
                ]
            ),
            2: dcdescr.MethodDesc(
                uid=3,
                alias_id=2,
                name='onRemoveAvatar',
                kbetypes=[
                    deftype.UID_SPEC.kbetype,
                ]
            ),
            3: dcdescr.MethodDesc(
                uid=10003,
                alias_id=3,
                name='onReqAvatarList',
                kbetypes=[
                    deftype.AVATAR_INFOS_LIST_SPEC.kbetype,
                ]
            ),
        },
        base_methods={
            1: dcdescr.MethodDesc(
                uid=1,
                alias_id=-1,
                name='reqRemoveAvatar',
                kbetypes=[
                    deftype.UNICODE_SPEC.kbetype,
                ]
            ),
            2: dcdescr.MethodDesc(
                uid=2,
                alias_id=-1,
                name='reqRemoveAvatarDBID',
                kbetypes=[
                    deftype.UID_SPEC.kbetype,
                ]
            ),
            10001: dcdescr.MethodDesc(
                uid=10001,
                alias_id=-1,
                name='reqAvatarList',
                kbetypes=[
                    
                ]
            ),
            10002: dcdescr.MethodDesc(
                uid=10002,
                alias_id=-1,
                name='reqCreateAvatar',
                kbetypes=[
                    deftype.ENTITY_SUBSTATE_SPEC.kbetype,deftype.UNICODE_SPEC.kbetype,
                ]
            ),
            10004: dcdescr.MethodDesc(
                uid=10004,
                alias_id=-1,
                name='selectAvatarGame',
                kbetypes=[
                    deftype.UID_SPEC.kbetype,
                ]
            ),
        },
        cell_methods={
        },
    ),


    2: dcdescr.EntityDesc(
        name='Avatar',
        uid=2,
        cls=AvatarBase,
        property_desc_by_id={
            1: dcdescr.PropertyDesc(
                uid=40000,
                name='position',
                kbetype=deftype.DIRECTION3D_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=1
            ),
            2: dcdescr.PropertyDesc(
                uid=40001,
                name='direction',
                kbetype=deftype.DIRECTION3D_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=2
            ),
            3: dcdescr.PropertyDesc(
                uid=40002,
                name='spaceID',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.CELL_PRIVATE,
                alias_id=3
            ),
            4: dcdescr.PropertyDesc(
                uid=47001,
                name='HP',
                kbetype=deftype.ENTITY_FORBIDS_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=4
            ),
            5: dcdescr.PropertyDesc(
                uid=47002,
                name='HP_Max',
                kbetype=deftype.ENTITY_FORBIDS_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=5
            ),
            6: dcdescr.PropertyDesc(
                uid=47003,
                name='MP',
                kbetype=deftype.ENTITY_FORBIDS_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=6
            ),
            7: dcdescr.PropertyDesc(
                uid=47004,
                name='MP_Max',
                kbetype=deftype.ENTITY_FORBIDS_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=7
            ),
            8: dcdescr.PropertyDesc(
                uid=16,
                name='component1',
                kbetype=deftype.ENTITY_COMPONENT_33_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.COMPONENT_1,
                alias_id=8
            ),
            9: dcdescr.PropertyDesc(
                uid=21,
                name='component2',
                kbetype=deftype.ENTITY_COMPONENT_34_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.COMPONENT_2,
                alias_id=9
            ),
            10: dcdescr.PropertyDesc(
                uid=22,
                name='component3',
                kbetype=deftype.ENTITY_COMPONENT_35_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.COMPONENT_3,
                alias_id=10
            ),
            11: dcdescr.PropertyDesc(
                uid=47005,
                name='forbids',
                kbetype=deftype.ENTITY_FORBIDS_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=11
            ),
            12: dcdescr.PropertyDesc(
                uid=41002,
                name='level',
                kbetype=deftype.UINT16_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.CELL_PUBLIC_AND_OWN,
                alias_id=12
            ),
            13: dcdescr.PropertyDesc(
                uid=41006,
                name='modelID',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=13
            ),
            14: dcdescr.PropertyDesc(
                uid=41007,
                name='modelScale',
                kbetype=deftype.ENTITY_SUBSTATE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=14
            ),
            15: dcdescr.PropertyDesc(
                uid=11,
                name='moveSpeed',
                kbetype=deftype.ENTITY_SUBSTATE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=15
            ),
            16: dcdescr.PropertyDesc(
                uid=41003,
                name='name',
                kbetype=deftype.UNICODE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=16
            ),
            17: dcdescr.PropertyDesc(
                uid=6,
                name='own_val',
                kbetype=deftype.UINT16_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.OWN_CLIENT,
                alias_id=17
            ),
            18: dcdescr.PropertyDesc(
                uid=41001,
                name='spaceUType',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.CELL_PUBLIC_AND_OWN,
                alias_id=18
            ),
            19: dcdescr.PropertyDesc(
                uid=47006,
                name='state',
                kbetype=deftype.ENTITY_STATE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=19
            ),
            20: dcdescr.PropertyDesc(
                uid=47007,
                name='subState',
                kbetype=deftype.ENTITY_SUBSTATE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=20
            ),
            21: dcdescr.PropertyDesc(
                uid=41004,
                name='uid',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=21
            ),
            22: dcdescr.PropertyDesc(
                uid=41005,
                name='utype',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=22
            ),
        },
        client_methods={
            1: dcdescr.MethodDesc(
                uid=10101,
                alias_id=1,
                name='dialog_addOption',
                kbetypes=[
                    deftype.ENTITY_SUBSTATE_SPEC.kbetype,deftype.ENTITY_UTYPE_SPEC.kbetype,deftype.UNICODE_SPEC.kbetype,deftype.ENTITY_FORBIDS_SPEC.kbetype,
                ]
            ),
            2: dcdescr.MethodDesc(
                uid=10104,
                alias_id=2,
                name='dialog_close',
                kbetypes=[
                    
                ]
            ),
            3: dcdescr.MethodDesc(
                uid=10102,
                alias_id=3,
                name='dialog_setText',
                kbetypes=[
                    deftype.UNICODE_SPEC.kbetype,deftype.ENTITY_SUBSTATE_SPEC.kbetype,deftype.ENTITY_UTYPE_SPEC.kbetype,deftype.UNICODE_SPEC.kbetype,
                ]
            ),
            4: dcdescr.MethodDesc(
                uid=12,
                alias_id=4,
                name='onAddSkill',
                kbetypes=[
                    deftype.ENTITY_FORBIDS_SPEC.kbetype,
                ]
            ),
            5: dcdescr.MethodDesc(
                uid=7,
                alias_id=5,
                name='onJump',
                kbetypes=[
                    
                ]
            ),
            6: dcdescr.MethodDesc(
                uid=13,
                alias_id=6,
                name='onRemoveSkill',
                kbetypes=[
                    deftype.ENTITY_FORBIDS_SPEC.kbetype,
                ]
            ),
            7: dcdescr.MethodDesc(
                uid=16,
                alias_id=7,
                name='recvDamage',
                kbetypes=[
                    deftype.ENTITY_FORBIDS_SPEC.kbetype,deftype.ENTITY_FORBIDS_SPEC.kbetype,deftype.ENTITY_FORBIDS_SPEC.kbetype,deftype.ENTITY_FORBIDS_SPEC.kbetype,
                ]
            ),
        },
        base_methods={
        },
        cell_methods={
            4: dcdescr.MethodDesc(
                uid=4,
                alias_id=-1,
                name='relive',
                kbetypes=[
                    deftype.ENTITY_SUBSTATE_SPEC.kbetype,
                ]
            ),
            5: dcdescr.MethodDesc(
                uid=5,
                alias_id=-1,
                name='jump',
                kbetypes=[
                    
                ]
            ),
            11: dcdescr.MethodDesc(
                uid=11,
                alias_id=-1,
                name='requestPull',
                kbetypes=[
                    
                ]
            ),
            11001: dcdescr.MethodDesc(
                uid=11001,
                alias_id=-1,
                name='useTargetSkill',
                kbetypes=[
                    deftype.ENTITY_FORBIDS_SPEC.kbetype,deftype.ENTITY_FORBIDS_SPEC.kbetype,
                ]
            ),
            11003: dcdescr.MethodDesc(
                uid=11003,
                alias_id=-1,
                name='dialog',
                kbetypes=[
                    deftype.ENTITY_FORBIDS_SPEC.kbetype,deftype.ENTITY_UTYPE_SPEC.kbetype,
                ]
            ),
        },
    ),


    3: dcdescr.EntityDesc(
        name='Test',
        uid=3,
        cls=TestBase,
        property_desc_by_id={
            1: dcdescr.PropertyDesc(
                uid=40000,
                name='position',
                kbetype=deftype.DIRECTION3D_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=1
            ),
            2: dcdescr.PropertyDesc(
                uid=40001,
                name='direction',
                kbetype=deftype.DIRECTION3D_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=2
            ),
            3: dcdescr.PropertyDesc(
                uid=40002,
                name='spaceID',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.CELL_PRIVATE,
                alias_id=3
            ),
            4: dcdescr.PropertyDesc(
                uid=18,
                name='own',
                kbetype=deftype.ENTITY_FORBIDS_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.CELL_PUBLIC_AND_OWN,
                alias_id=4
            ),
            5: dcdescr.PropertyDesc(
                uid=17,
                name='state',
                kbetype=deftype.ENTITY_FORBIDS_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=5
            ),
        },
        client_methods={
            1: dcdescr.MethodDesc(
                uid=28,
                alias_id=1,
                name='helloCB',
                kbetypes=[
                    deftype.ENTITY_FORBIDS_SPEC.kbetype,
                ]
            ),
        },
        base_methods={
            27: dcdescr.MethodDesc(
                uid=27,
                alias_id=-1,
                name='say',
                kbetypes=[
                    deftype.ENTITY_FORBIDS_SPEC.kbetype,
                ]
            ),
        },
        cell_methods={
            26: dcdescr.MethodDesc(
                uid=26,
                alias_id=-1,
                name='hello',
                kbetypes=[
                    deftype.ENTITY_FORBIDS_SPEC.kbetype,
                ]
            ),
        },
    ),


    4: dcdescr.EntityDesc(
        name='TestNoBase',
        uid=4,
        cls=TestNoBaseBase,
        property_desc_by_id={
            1: dcdescr.PropertyDesc(
                uid=40000,
                name='position',
                kbetype=deftype.DIRECTION3D_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=1
            ),
            2: dcdescr.PropertyDesc(
                uid=40001,
                name='direction',
                kbetype=deftype.DIRECTION3D_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=2
            ),
            3: dcdescr.PropertyDesc(
                uid=40002,
                name='spaceID',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.CELL_PRIVATE,
                alias_id=3
            ),
            4: dcdescr.PropertyDesc(
                uid=24,
                name='own',
                kbetype=deftype.ENTITY_FORBIDS_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.CELL_PUBLIC_AND_OWN,
                alias_id=4
            ),
            5: dcdescr.PropertyDesc(
                uid=23,
                name='state',
                kbetype=deftype.ENTITY_FORBIDS_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=5
            ),
        },
        client_methods={
            1: dcdescr.MethodDesc(
                uid=30,
                alias_id=1,
                name='helloCB',
                kbetypes=[
                    deftype.ENTITY_FORBIDS_SPEC.kbetype,
                ]
            ),
        },
        base_methods={
        },
        cell_methods={
            29: dcdescr.MethodDesc(
                uid=29,
                alias_id=-1,
                name='hello',
                kbetypes=[
                    deftype.ENTITY_FORBIDS_SPEC.kbetype,
                ]
            ),
        },
    ),


    5: dcdescr.EntityDesc(
        name='Monster',
        uid=5,
        cls=MonsterBase,
        property_desc_by_id={
            1: dcdescr.PropertyDesc(
                uid=40000,
                name='position',
                kbetype=deftype.DIRECTION3D_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=1
            ),
            2: dcdescr.PropertyDesc(
                uid=40001,
                name='direction',
                kbetype=deftype.DIRECTION3D_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=2
            ),
            3: dcdescr.PropertyDesc(
                uid=40002,
                name='spaceID',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.CELL_PRIVATE,
                alias_id=3
            ),
            4: dcdescr.PropertyDesc(
                uid=47001,
                name='HP',
                kbetype=deftype.ENTITY_FORBIDS_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=4
            ),
            5: dcdescr.PropertyDesc(
                uid=47002,
                name='HP_Max',
                kbetype=deftype.ENTITY_FORBIDS_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=5
            ),
            6: dcdescr.PropertyDesc(
                uid=47003,
                name='MP',
                kbetype=deftype.ENTITY_FORBIDS_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=6
            ),
            7: dcdescr.PropertyDesc(
                uid=47004,
                name='MP_Max',
                kbetype=deftype.ENTITY_FORBIDS_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=7
            ),
            8: dcdescr.PropertyDesc(
                uid=51007,
                name='entityNO',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=8
            ),
            9: dcdescr.PropertyDesc(
                uid=47005,
                name='forbids',
                kbetype=deftype.ENTITY_FORBIDS_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=9
            ),
            10: dcdescr.PropertyDesc(
                uid=41006,
                name='modelID',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=10
            ),
            11: dcdescr.PropertyDesc(
                uid=41007,
                name='modelScale',
                kbetype=deftype.ENTITY_SUBSTATE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=11
            ),
            12: dcdescr.PropertyDesc(
                uid=32,
                name='moveSpeed',
                kbetype=deftype.ENTITY_SUBSTATE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=12
            ),
            13: dcdescr.PropertyDesc(
                uid=41003,
                name='name',
                kbetype=deftype.UNICODE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=13
            ),
            14: dcdescr.PropertyDesc(
                uid=47006,
                name='state',
                kbetype=deftype.ENTITY_STATE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=14
            ),
            15: dcdescr.PropertyDesc(
                uid=47007,
                name='subState',
                kbetype=deftype.ENTITY_SUBSTATE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=15
            ),
            16: dcdescr.PropertyDesc(
                uid=41004,
                name='uid',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=16
            ),
            17: dcdescr.PropertyDesc(
                uid=41005,
                name='utype',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=17
            ),
        },
        client_methods={
            1: dcdescr.MethodDesc(
                uid=34,
                alias_id=1,
                name='recvDamage',
                kbetypes=[
                    deftype.ENTITY_FORBIDS_SPEC.kbetype,deftype.ENTITY_FORBIDS_SPEC.kbetype,deftype.ENTITY_FORBIDS_SPEC.kbetype,deftype.ENTITY_FORBIDS_SPEC.kbetype,
                ]
            ),
        },
        base_methods={
        },
        cell_methods={
        },
    ),


    6: dcdescr.EntityDesc(
        name='NPC',
        uid=6,
        cls=NPCBase,
        property_desc_by_id={
            1: dcdescr.PropertyDesc(
                uid=40000,
                name='position',
                kbetype=deftype.DIRECTION3D_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=1
            ),
            2: dcdescr.PropertyDesc(
                uid=40001,
                name='direction',
                kbetype=deftype.DIRECTION3D_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=2
            ),
            3: dcdescr.PropertyDesc(
                uid=40002,
                name='spaceID',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.CELL_PRIVATE,
                alias_id=3
            ),
            4: dcdescr.PropertyDesc(
                uid=51007,
                name='entityNO',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=4
            ),
            5: dcdescr.PropertyDesc(
                uid=41006,
                name='modelID',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=5
            ),
            6: dcdescr.PropertyDesc(
                uid=41007,
                name='modelScale',
                kbetype=deftype.ENTITY_SUBSTATE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=6
            ),
            7: dcdescr.PropertyDesc(
                uid=43,
                name='moveSpeed',
                kbetype=deftype.ENTITY_SUBSTATE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=7
            ),
            8: dcdescr.PropertyDesc(
                uid=41003,
                name='name',
                kbetype=deftype.UNICODE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=8
            ),
            9: dcdescr.PropertyDesc(
                uid=41004,
                name='uid',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=9
            ),
            10: dcdescr.PropertyDesc(
                uid=41005,
                name='utype',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=10
            ),
        },
        client_methods={
        },
        base_methods={
        },
        cell_methods={
        },
    ),


    7: dcdescr.EntityDesc(
        name='Gate',
        uid=7,
        cls=GateBase,
        property_desc_by_id={
            1: dcdescr.PropertyDesc(
                uid=40000,
                name='position',
                kbetype=deftype.DIRECTION3D_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=1
            ),
            2: dcdescr.PropertyDesc(
                uid=40001,
                name='direction',
                kbetype=deftype.DIRECTION3D_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=2
            ),
            3: dcdescr.PropertyDesc(
                uid=40002,
                name='spaceID',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.CELL_PRIVATE,
                alias_id=3
            ),
            4: dcdescr.PropertyDesc(
                uid=51007,
                name='entityNO',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=4
            ),
            5: dcdescr.PropertyDesc(
                uid=41006,
                name='modelID',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=5
            ),
            6: dcdescr.PropertyDesc(
                uid=41007,
                name='modelScale',
                kbetype=deftype.ENTITY_SUBSTATE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=6
            ),
            7: dcdescr.PropertyDesc(
                uid=41003,
                name='name',
                kbetype=deftype.UNICODE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=7
            ),
            8: dcdescr.PropertyDesc(
                uid=41004,
                name='uid',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=8
            ),
            9: dcdescr.PropertyDesc(
                uid=41005,
                name='utype',
                kbetype=deftype.ENTITY_UTYPE_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS,
                alias_id=9
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
