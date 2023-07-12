"""???"""

import collections
import tempfile
from pathlib import Path

from unittest import TestCase

from enki.core.kbetype import FixedDict

from tools.parsers import typesxml


class ParseTypesXMLParserTestCase(TestCase):
    """Unit tests of TypesXMLParser.parse"""

    def setUp(self):
        super().setUp()
        self.path_inst = Path(tempfile.NamedTemporaryFile().name)

    def tearDown(self):
        super().tearDown()
        assert isinstance(self.path_inst, Path)
        self.path_inst.unlink()

    def test_parse_UNICODE(self):
        content = """
        <root>
            <!-- avatar name -->
            <AVATAR_NAME> UNICODE </AVATAR_NAME>
        </root>
        """
        with self.path_inst.open('w') as fh:
            fh.write(content)

        inst = typesxml.TypesXMLParser(self.path_inst)
        type_info_by_name = inst.parse()
        type_info = type_info_by_name['AVATAR_NAME']

        assert type_info.name == 'AVATAR_NAME'
        assert type_info.py_type_name == 'AvatarName'
        assert not type_info.is_array
        assert not type_info.is_fixed_dict

    def test_parse_VECTOR3(self):
        content = """
        <root>
            <DIRECTION> VECTOR3 </DIRECTION>
        </root>
        """
        with self.path_inst.open('w') as fh:
            fh.write(content)

        inst = typesxml.TypesXMLParser(self.path_inst)
        type_info_by_name = inst.parse()
        type_info = type_info_by_name['DIRECTION']

        assert type_info.name == 'DIRECTION'
        assert type_info.py_type_name == 'Direction'
        assert not type_info.is_array
        assert not type_info.is_fixed_dict

    def test_parse_UINT64_alias_of_alias(self):
        content = """
        <root>
            <DIRECTION> VECTOR3 </DIRECTION>
            <ENEMY_DIRECTION> DIRECTION </ENEMY_DIRECTION>
        </root>
        """
        with self.path_inst.open('w') as fh:
            fh.write(content)

        inst = typesxml.TypesXMLParser(self.path_inst)
        type_info_by_name = inst.parse()
        type_info = type_info_by_name['ENEMY_DIRECTION']

        assert type_info.name == 'ENEMY_DIRECTION'
        assert type_info.py_type_name == 'EnemyDirection'
        assert not type_info.is_array
        assert not type_info.is_fixed_dict

    def test_parse_ARRAY_of_basic_type(self):
        """Checks parsing of alias of an ARRAY kbe type."""
        content = """
        <root>
            <AVATAR_DBIDS> ARRAY <of> UINT64 </of> </AVATAR_DBIDS>
        </root>
        """
        with self.path_inst.open('w') as fh:
            fh.write(content)

        inst = typesxml.TypesXMLParser(self.path_inst)
        type_info_by_name = inst.parse()
        type_info = type_info_by_name['AVATAR_DBIDS']

        assert type_info.name == 'AVATAR_DBIDS'
        assert type_info.py_type_name == 'AvatarDbids'
        assert type_info.arr_of == 'UINT64'
        assert type_info.arr_of_py_type_name == 'Uint64'
        assert type_info.is_array
        assert not type_info.is_fixed_dict

    def test_parse_ARRAY_of_alias(self):
        """Массив из типа, который определён алиасом."""
        content = """
        <root>
            <DIRECTION> VECTOR3 </DIRECTION>
            <DIRECTIONS> ARRAY <of> DIRECTION </of> </DIRECTIONS>
        </root>
        """
        with self.path_inst.open('w') as fh:
            fh.write(content)

        inst = typesxml.TypesXMLParser(self.path_inst)
        type_info_by_name = inst.parse()
        type_info = type_info_by_name['DIRECTIONS']

        assert type_info.name == 'DIRECTIONS'
        assert type_info.py_type_name == 'Directions'
        assert type_info.arr_of == 'DIRECTION'
        assert type_info.arr_of_py_type_name == 'Direction'
        assert type_info.is_array
        assert not type_info.is_fixed_dict

        # В описании есть тип массива
        assert 'DIRECTION' in type_info_by_name

    def test_parse_ARRAY_of_arrays(self):
        """Массив из типа, который определён алиасом."""
        content = """
        <root>
            <AVATAR_DBIDS> ARRAY <of> UINT64 </of> </AVATAR_DBIDS>
            <ARRAY_OF_ARRAYS> ARRAY <of> AVATAR_DBIDS </of> </ARRAY_OF_ARRAYS>
        </root>
        """
        with self.path_inst.open('w') as fh:
            fh.write(content)

        inst = typesxml.TypesXMLParser(self.path_inst)
        type_info_by_name = inst.parse()
        type_info = type_info_by_name['ARRAY_OF_ARRAYS']

        assert type_info.name == 'ARRAY_OF_ARRAYS'
        assert type_info.py_type_name == 'ArrayOfArrays'
        assert type_info.arr_of == 'AVATAR_DBIDS'
        assert type_info.arr_of_py_type_name == 'AvatarDbids'
        assert type_info.is_array
        assert not type_info.is_fixed_dict

        # В описании есть тип массива
        assert 'AVATAR_DBIDS' in type_info_by_name

    def test_parse_fixed_dict(self):
        content = """
        <root>
            <AVATAR_NAME> UNICODE </AVATAR_NAME>
            <AVATAR_UID> INT32 </AVATAR_UID>
            <DBID> UINT64 </DBID>
            <AVATAR_INFO> FIXED_DICT
                <Properties>
                    <name>
                        <Type> AVATAR_NAME </Type>
                    </name>
                    <uid>
                        <Type> AVATAR_UID </Type>
                    </uid>
                    <dbid>
                        <Type> DBID </Type>
                    </dbid>
                </Properties>
            </AVATAR_INFO>
        </root>
        """
        with self.path_inst.open('w') as fh:
            fh.write(content)

        inst = typesxml.TypesXMLParser(self.path_inst)
        type_info_by_name = inst.parse()
        type_info = type_info_by_name['AVATAR_INFO']

        assert type_info.name == 'AVATAR_INFO'
        assert type_info.py_type_name == 'AvatarInfo'
        assert type_info.fd_pairs is not None
        assert type_info.fd_pairs == {
            'name': 'AvatarName',
            'uid': 'AvatarUid',
            'dbid': 'Dbid',
        }
        assert type_info.converter is None
        assert not type_info.is_array
        assert type_info.is_fixed_dict

        assert 'AVATAR_NAME' in type_info_by_name
        assert 'AVATAR_UID' in type_info_by_name
        assert 'DBID' in type_info_by_name

    def test_parse_fixed_dict_with_array(self):
        """Checks FIXED_DICT with ARRAY in field."""
        content = """
        <root>
            <DBID> UINT64 </DBID>
            <AVATAR_DBIDS> FIXED_DICT
                <Properties>
                    <dbids>
                        <Type> ARRAY <of> DBID </of> </Type>
                    </dbids>
                </Properties>
            </AVATAR_DBIDS>
        </root>
        """
        with self.path_inst.open('w') as fh:
            fh.write(content)

        inst = typesxml.TypesXMLParser(self.path_inst)
        type_info_by_name = inst.parse()
        type_info = type_info_by_name['AVATAR_DBIDS']

        assert type_info.name == 'AVATAR_DBIDS'
        assert type_info.py_type_name == 'AvatarDbids'
        assert type_info.fd_pairs is not None
        assert type_info.fd_pairs == {
            'dbids': 'AvatarDbidsInnerArr1',
        }
        assert type_info.converter is None
        assert 'AvatarDbidsInnerArr1' in type_info.inner_arr_names

        assert not type_info.is_array
        assert type_info.is_fixed_dict

        assert 'AvatarDbidsInnerArr1' in type_info_by_name

    def test_parse_fixed_dict_with_converter(self):
        """Checks parsing of FIXED_DICT with converter."""
        content = """
        <root>
            <AVATAR_NAME> UNICODE </AVATAR_NAME>
            <AVATAR_UID> INT32 </AVATAR_UID>
            <DBID> UINT64 </DBID>
            <AVATAR_INFO> FIXED_DICT
                <implementedBy> module_name.AvatarInfoUserType </implementedBy>
                <Properties>
                    <name>
                        <Type> AVATAR_NAME </Type>
                    </name>
                    <uid>
                        <Type> AVATAR_UID </Type>
                    </uid>
                    <dbid>
                        <Type> DBID </Type>
                    </dbid>
                </Properties>
            </AVATAR_INFO>
        </root>
        """
        with self.path_inst.open('w') as fh:
            fh.write(content)

        # Так будет выглядеть сгенерированные типы

        AvatarName = str
        AvatarUid = int
        Dbid = int

        class AvatarInfo(FixedDict):
            name: AvatarName
            uid: AvatarUid
            dbid: Dbid

            def __init__(self, type_name='AVATAR_INFO',
                         initial_data=collections.OrderedDict({
                            'name': '',
                            'uid': 0,
                            'dbid': 0,
                         })
                        ):
                super().__init__(type_name, initial_data)

        # Это определённый пользователем тип, на который будет заменён
        # AvatarInfo в конвертере. Имя этого типа и модуль, где он находится
        # доступны из types.xml в поле implementedBy

        class AvatarInfoUserType:

            def __init__(self, name: str, uid: int, dbid: int):
                self.name = name
                self.uid = uid
                self.dbid = dbid

        # Это конвертер из FD в UserType и обратно в том же модуле

        class AvatarInfoConverter:

            @classmethod
            def createObjFromDict(cls, fixed_dict: AvatarInfo) -> AvatarInfoUserType:
                return AvatarInfoUserType(
                    fixed_dict.name, fixed_dict.uid, fixed_dict.dbid
                )

            @classmethod
            def getDictFromObj(cls, obj: AvatarInfoUserType) -> AvatarInfo:
                avatar_info = AvatarInfo()
                avatar_info.name = obj.name
                avatar_info.uid = obj.uid
                avatar_info.dbid = obj.dbid
                return avatar_info

            @classmethod
            def isSameType(cls, obj: AvatarInfoUserType) -> bool:
                return isinstance(obj, AvatarInfoUserType)

        inst = typesxml.TypesXMLParser(self.path_inst)
        type_info_by_name = inst.parse()
        type_info = type_info_by_name['AVATAR_INFO']

        assert type_info.name == 'AVATAR_INFO'
        assert type_info.py_type_name == 'AvatarInfo'
        assert type_info.fd_pairs is not None
        assert type_info.fd_pairs == {
            'name': 'AvatarName',
            'uid': 'AvatarUid',
            'dbid': 'Dbid',
        }
        assert type_info.converter is not None
        # При генерации будет добавлен импорт этого типа из модуля module_name
        assert type_info.converter == 'module_name.AvatarInfoUserType'

        assert not type_info.is_array
        assert type_info.is_fixed_dict

        assert 'AVATAR_NAME' in type_info_by_name
        assert 'AVATAR_UID' in type_info_by_name
        assert 'DBID' in type_info_by_name

    def test_parse_array_of_fixed_dict(self):
        content = """
        <root>
            <AVATAR_NAME> UNICODE </AVATAR_NAME>
            <AVATAR_UID> INT32 </AVATAR_UID>
            <DBID> UINT64 </DBID>
            <AVATAR_INFO> FIXED_DICT
                <Properties>
                    <name>
                        <Type> AVATAR_NAME </Type>
                    </name>
                    <uid>
                        <Type> AVATAR_UID </Type>
                    </uid>
                    <dbid>
                        <Type> DBID </Type>
                    </dbid>
                </Properties>
            </AVATAR_INFO>
            <AVATAR_INFOS> ARRAY <of> AVATAR_INFO </of> </AVATAR_INFOS>
        </root>
        """
        with self.path_inst.open('w') as fh:
            fh.write(content)

        inst = typesxml.TypesXMLParser(self.path_inst)
        type_info_by_name = inst.parse()
        type_info = type_info_by_name['AVATAR_INFOS']

        assert type_info.name == 'AVATAR_INFOS'
        assert type_info.py_type_name == 'AvatarInfos'
        assert type_info.arr_of == 'AVATAR_INFO'
        assert type_info.arr_of_py_type_name == 'AvatarInfo'
        assert type_info.is_array
        assert not type_info.is_fixed_dict

        assert 'AVATAR_INFO' in type_info_by_name
