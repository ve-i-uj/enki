"""This generated module contains entity descriptions."""

from .Account import AccountBase

from enki import dcdescr, kbeenum
from enki.descr import deftype

DESC_BY_UID = {
    1: dcdescr.EntityDesc(
        name='Account',
        uid=1,
        cls=AccountBase,
        property_desc_by_id={
            1: dcdescr.PropertyDesc(
                uid=1,
                name='name',
                kbetype=deftype.AVATAR_NAME_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS
            ),
            40000: dcdescr.PropertyDesc(
                uid=40000,
                name='position',
                kbetype=deftype.VECTOR3_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS
            ),
            40001: dcdescr.PropertyDesc(
                uid=40001,
                name='direction',
                kbetype=deftype.VECTOR3_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.ALL_CLIENTS
            ),
            40002: dcdescr.PropertyDesc(
                uid=40002,
                name='spaceID',
                kbetype=deftype.UINT32_SPEC.kbetype,
                distribution_flag=kbeenum.DistributionFlag.CELL_PRIVATE
            ),
        },
        client_methods={
            3: dcdescr.MethodDesc(
                uid=3,
                name='resp_get_avatars',
                kbetypes=[
                    deftype.AVATAR_DBIDS_SPEC.kbetype,deftype.ARRAY_27_SPEC.kbetype,
                ]
            ),
        },
        base_methods={
            2: dcdescr.MethodDesc(
                uid=2,
                name='req_get_avatars',
                kbetypes=[
                    deftype.AVATAR_UID_SPEC.kbetype,deftype.AVATAR_NAME_SPEC.kbetype,
                ]
            ),
        },
        cell_methods={
            1: dcdescr.MethodDesc(
                uid=1,
                name='cellapp_method',
                kbetypes=[
                    deftype.STRING_SPEC.kbetype,deftype.AVATAR_INFO_LIST_SPEC.kbetype,
                ]
            ),
        },
    ),
}

__all__ = ['DESC_BY_UID']
