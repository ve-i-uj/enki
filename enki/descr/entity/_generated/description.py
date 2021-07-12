"""This generated module contains entity descriptions."""

from .Account import AccountBase
from .. import _entity
from ... import _deftype

DESC_BY_UID = {
    1: _entity.EntityDesc(
        name='Account',
        uid=1,
        cls=AccountBase,
        property_desc_by_id={
            1: _entity.PropertyDesc(
                uid=1,
                name='test_type_ARRAY_of_FIXED_DICT',
                kbetype=_deftype.AVATAR_INFO_LIST_SPEC.kbetype
            ),
            2: _entity.PropertyDesc(
                uid=2,
                name='test_type_FIXED_DICT',
                kbetype=_deftype.AVATAR_INFO_SPEC.kbetype
            ),
            3: _entity.PropertyDesc(
                uid=3,
                name='test_alias_DBID',
                kbetype=_deftype.DBID_SPEC.kbetype
            ),
            4: _entity.PropertyDesc(
                uid=4,
                name='test_type_PYTHON',
                kbetype=_deftype.PYTHON_SPEC.kbetype
            ),
            5: _entity.PropertyDesc(
                uid=5,
                name='test_type_VECTOR2',
                kbetype=_deftype.VECTOR2_SPEC.kbetype
            ),
            6: _entity.PropertyDesc(
                uid=6,
                name='test_type_VECTOR3',
                kbetype=_deftype.VECTOR3_SPEC.kbetype
            ),
            7: _entity.PropertyDesc(
                uid=7,
                name='test_type_VECTOR4',
                kbetype=_deftype.VECTOR4_SPEC.kbetype
            ),
            40000: _entity.PropertyDesc(
                uid=40000,
                name='position',
                kbetype=_deftype.VECTOR3_SPEC.kbetype
            ),
            40001: _entity.PropertyDesc(
                uid=40001,
                name='direction',
                kbetype=_deftype.VECTOR3_SPEC.kbetype
            ),
            40002: _entity.PropertyDesc(
                uid=40002,
                name='spaceID',
                kbetype=_deftype.UINT32_SPEC.kbetype
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
