"""This generated module contains entity descriptions."""

from .Account import AccountBase

from enki import dcdescr
from enki.descr import deftype

DESC_BY_UID = {
    1: dcdescr.EntityDesc(
        name='Account',
        uid=1,
        cls=AccountBase,
        property_desc_by_id={
            1: dcdescr.PropertyDesc(
                uid=1,
                name='test_type_ARRAY_of_FIXED_DICT',
                kbetype=deftype.AVATAR_INFO_LIST_SPEC.kbetype
            ),
            2: dcdescr.PropertyDesc(
                uid=2,
                name='test_default',
                kbetype=deftype.DBID_SPEC.kbetype
            ),
            40000: dcdescr.PropertyDesc(
                uid=40000,
                name='position',
                kbetype=deftype.VECTOR3_SPEC.kbetype
            ),
            40001: dcdescr.PropertyDesc(
                uid=40001,
                name='direction',
                kbetype=deftype.VECTOR3_SPEC.kbetype
            ),
            40002: dcdescr.PropertyDesc(
                uid=40002,
                name='spaceID',
                kbetype=deftype.UINT32_SPEC.kbetype
            ),
        },
        client_methods=[
        ],
        base_methods=[
        ],
        cell_methods=[
        ],
    ),
}

__all__ = ['DESC_BY_UID']
