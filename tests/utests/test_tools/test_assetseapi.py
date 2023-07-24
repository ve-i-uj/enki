"""Тесты генератора api для серверных сущностей."""

import collections
import shutil
import tempfile
from pathlib import Path

from unittest import TestCase

import jinja2
from tools.parsers import EntityDefParser, TypesXMLParser

from tools.assetsapi import utils
from tools.parsers import UsetTypeParser


class AssetsAPITestCase(TestCase):

    def setUp(self):
        super().setUp()
        self._typesxml_path = Path(tempfile.NamedTemporaryFile().name)
        self._entitydef_dir = Path(tempfile.TemporaryDirectory().name)
        self._entitydef_dir.mkdir(exist_ok=True)

    def tearDown(self):
        super().tearDown()
        assert isinstance(self._typesxml_path, Path)
        self._typesxml_path.unlink()
        shutil.rmtree(self._entitydef_dir)

    def test_generate_types(self):
        """
        Проверяем, что генерируется по шаблону без ошибок и под дебагером,
        если нужно, смотрим результат.
        """
        typesxml_content = """
        <root>
            <!-- Простые алиасы -->
            <AVATAR_NAME> UNICODE </AVATAR_NAME>
            <AVATAR_UID> INT32 </AVATAR_UID>
            <DBID> UINT64 </DBID>
            <!-- Вектор -->
            <DIRECTION> VECTOR3 </DIRECTION>
            <ENEMY_DIRECTION> DIRECTION </ENEMY_DIRECTION>
            <!-- Массив -->
            <AVATAR_DBIDS> ARRAY <of> UINT64 </of> </AVATAR_DBIDS>
            <DIRECTIONS> ARRAY <of> DIRECTION </of> </DIRECTIONS>
            <!-- Массив массивов -->
            <ARRAY_OF_ARRAYS> ARRAY <of> AVATAR_DBIDS </of> </ARRAY_OF_ARRAYS>
            <!-- Фиксированный словарь -->
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
            <!-- Фиксированный словарь с массивом, определённым внутри -->
            <INNER_ARRAY_IN_FD> FIXED_DICT
                <Properties>
                    <dbids>
                        <Type> ARRAY <of> DBID </of> </Type>
                    </dbids>
                </Properties>
            </INNER_ARRAY_IN_FD>
            <!-- Фиксированный словарь с конвертерем -->
            <AVATAR_INFO_WITH_CONVERTER> FIXED_DICT
                <implementedBy> module_name.AvatarInfoConverter </implementedBy>
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
            </AVATAR_INFO_WITH_CONVERTER>
            <!-- Массив с FD -->
            <AVATAR_INFOS> ARRAY <of> AVATAR_INFO </of> </AVATAR_INFOS>
        </root>
        """
        with self._typesxml_path.open('w') as fh:
            fh.write(typesxml_content)

        typesxml_parser = TypesXMLParser(self._typesxml_path)
        type_info_by_name = typesxml_parser.parse()

        template_path = Path(__file__).parent.parent.parent.parent / 'tools' / 'assetsapi' / 'templates' / 'typesxml.py.jinja'
        with template_path.open('r') as fh:
            jinja_entity_template = fh.read()
        jinja_env = jinja2.Environment()
        template = jinja_env.from_string(jinja_entity_template)
        res = template.render(
            type_info_by_name=type_info_by_name,
        )

    def test_generated_base_property(self):
        typesxml_content = """
        <root>
            <AVATAR_NAME> UNICODE </AVATAR_NAME>
            <AVATAR_UID> INT32 </AVATAR_UID>
            <DBID> UINT64 </DBID>
            <DIRECTION> VECTOR3 </DIRECTION>
            <AVATAR_DBIDS> ARRAY <of> UINT64 </of> </AVATAR_DBIDS>
            <DIRECTIONS> ARRAY <of> DIRECTION </of> </DIRECTIONS>
            <!-- Массив массивов -->
            <ARRAY_OF_ARRAYS> ARRAY <of> AVATAR_DBIDS </of> </ARRAY_OF_ARRAYS>
            <!-- Фиксированный словарь -->
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
        with self._typesxml_path.open('w') as fh:
            fh.write(typesxml_content)

        entity_def_content = """
        <root>
            <Properties>
                <name>
                    <Type> AVATAR_NAME </Type>
                    <Flags> BASE </Flags>
                    <Persistent> true </Persistent>
                </name>
                <entity_direction>
                    <Type> DIRECTION </Type>
                    <Flags> BASE </Flags>
                    <Persistent> true </Persistent>
                </entity_direction>
                <avatar_dbids>
                    <Type> AVATAR_DBIDS </Type>
                    <Flags> BASE </Flags>
                    <Persistent> true </Persistent>
                </avatar_dbids>
                <directions>
                    <Type> DIRECTIONS </Type>
                    <Flags> BASE_AND_CLIENT </Flags>
                    <Persistent> true </Persistent>
                </directions>
                <array_of_arrays>
                    <Type> ARRAY_OF_ARRAYS </Type>
                    <Flags> BASE_AND_CLIENT </Flags>
                    <Persistent> true </Persistent>
                </array_of_arrays>
                <avatar_info>
                    <Type> AVATAR_INFO </Type>
                    <Flags> BASE_AND_CLIENT </Flags>
                    <Persistent> true </Persistent>
                </avatar_info>
            </Properties>
            <BaseMethods>
            </BaseMethods>
            <CellMethods>
            </CellMethods>
            <ClientMethods>
            </ClientMethods>
        </root>
        """
        with (self._entitydef_dir / 'Avatar.def').open('w') as fh:
            fh.write(entity_def_content)

        typesxml_parser = TypesXMLParser(self._typesxml_path)
        type_info_by_name = typesxml_parser.parse()
        type_info = type_info_by_name['AVATAR_NAME']

        edef_parser = EntityDefParser(self._entitydef_dir)
        entity_info = edef_parser.parse('Avatar')
        entity_info.get_base_properties()

        jinja_entity_template = \
"""
class IBase{{ entity_info.name }}(abc.ABC):
    {%- for prop in entity_info.get_base_properties() %}
    {{ prop.name }}: {{ type_info_by_name[prop.type].py_type_name }}
    {%- endfor %}

"""
        jinja_env = jinja2.Environment()
        template = jinja_env.from_string(jinja_entity_template)
        res = template.render(
            type_info_by_name=type_info_by_name,
            entity_info=entity_info,
        )

        assert res == """
class IBaseAvatar(abc.ABC):
    name: AvatarName
    entity_direction: Direction
    avatar_dbids: AvatarDbids
    directions: Directions
    array_of_arrays: ArrayOfArrays
    avatar_info: AvatarInfo
"""

    def test_generated_cell_property(self):
        typesxml_content = """
        <root>
            <AVATAR_NAME> UNICODE </AVATAR_NAME>
        </root>
        """
        with self._typesxml_path.open('w') as fh:
            fh.write(typesxml_content)

        entity_def_content = """
        <root>
            <Properties>
                <name>
                    <Type> AVATAR_NAME </Type>
                    <Flags> CELL_PUBLIC </Flags>
                    <Persistent> true </Persistent>
                </name>
            </Properties>
            <BaseMethods>
            </BaseMethods>
            <CellMethods>
            </CellMethods>
            <ClientMethods>
            </ClientMethods>
        </root>
        """
        with (self._entitydef_dir / 'Avatar.def').open('w') as fh:
            fh.write(entity_def_content)

        typesxml_parser = TypesXMLParser(self._typesxml_path)
        type_info_by_name = typesxml_parser.parse()
        type_info = type_info_by_name['AVATAR_NAME']

        typesxml_parser = EntityDefParser(self._entitydef_dir)
        entity_info = typesxml_parser.parse('Avatar')
        entity_info.get_base_properties()

        jinja_entity_template = \
"""
class ICell{{ entity_info.name }}(abc.ABC):
    {%- for prop in entity_info.get_cell_properties() %}
    {{ prop.name }}: {{ type_info_by_name[prop.type].py_type_name }}
    {%- endfor %}

"""
        jinja_env = jinja2.Environment()
        template = jinja_env.from_string(jinja_entity_template)
        res = template.render(
            type_info_by_name=type_info_by_name,
            entity_info=entity_info,
        )

        assert res == """
class ICellAvatar(abc.ABC):
    name: AvatarName
"""

    def test_build_method_args(self):
        typesxml_content = """
        <root>
            <AVATAR_NAME> UNICODE </AVATAR_NAME>
        </root>
        """
        with self._typesxml_path.open('w') as fh:
            fh.write(typesxml_content)

        typesxml_parser = TypesXMLParser(self._typesxml_path)
        type_info_by_name = typesxml_parser.parse()

        entity_def_content = """
        <root>
            <Properties>
            </Properties>
            <BaseMethods>
                <method_1>
                    <Exposed />
                    <Arg> INT32 </Arg>
                    <Arg> UINT32 </Arg>
                    <Arg> BOOL </Arg>
                    <Arg> BLOB </Arg>
                    <Arg> UNICODE </Arg>
                </method_1>
            </BaseMethods>
            <CellMethods>
            </CellMethods>
            <ClientMethods>
            </ClientMethods>
        </root>
        """
        with (self._entitydef_dir / 'Avatar.def').open('w') as fh:
            fh.write(entity_def_content)

        typesxml_parser = EntityDefParser(self._entitydef_dir)
        entity_info = typesxml_parser.parse('Avatar')

        res = utils.build_method_args(entity_info.BaseMethods[0], type_info_by_name, {})
        assert res == """self,
                 entity_caller_id: int,
                 arg_0: int,
                 arg_1: int,
                 arg_2: bool,
                 arg_3: bytes,
                 arg_4: str"""

    def test_build_method_args_with_fd_converter(self):
        """У FD с конвертером тип аргумента будет тип из конвертера."""
        typesxml_content = """
        <root>
            <AVATAR_INFO_WITH_CONVERTER> FIXED_DICT
                <implementedBy> module_name.AvatarInfoConverter </implementedBy>
                <Properties>
                    <name>
                        <Type> STRING </Type>
                    </name>
                </Properties>
            </AVATAR_INFO_WITH_CONVERTER>
        </root>
        """
        with self._typesxml_path.open('w') as fh:
            fh.write(typesxml_content)

        user_type_content = """
# Так будет выглядеть сгенерированные типы

AvatarName = str
AvatarUid = int
Dbid = int

class AvatarInfo(dict):
    name: AvatarName
    uid: AvatarUid
    dbid: Dbid

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
"""

        self._user_type_dir = Path(tempfile.TemporaryDirectory().name)
        self._user_type_dir.mkdir(exist_ok=True)
        self._user_type_module_path = self._user_type_dir / 'module_name.py'

        with self._user_type_module_path.open('w') as fh:
            fh.write(user_type_content)

        typesxml_parser = TypesXMLParser(self._typesxml_path)
        type_info_by_name = typesxml_parser.parse()

        user_type_parser = UsetTypeParser(self._user_type_module_path.parent)
        user_type_infos = user_type_parser.parse()

        entity_def_content = """
        <root>
            <Properties>
            </Properties>
            <BaseMethods>
                <method_1>
                    <Arg> AVATAR_INFO_WITH_CONVERTER </Arg> <!-- avatar_info -->
                </method_1>
            </BaseMethods>
            <CellMethods>
            </CellMethods>
            <ClientMethods>
            </ClientMethods>
        </root>
        """
        with (self._entitydef_dir / 'Avatar.def').open('w') as fh:
            fh.write(entity_def_content)

        typesxml_parser = EntityDefParser(self._entitydef_dir)
        entity_info = typesxml_parser.parse('Avatar')

        res = utils.build_method_args(
            entity_info.BaseMethods[0], type_info_by_name, user_type_infos
        )
        assert res == """self,
                 avatar_info: AvatarInfoUserType"""

    def test_generated_base_method(self):
        typesxml_content = """
        <root>
            <AVATAR_NAME> UNICODE </AVATAR_NAME>
            <AVATAR_UID> INT32 </AVATAR_UID>
            <DBID> UINT64 </DBID>
            <DIRECTION> VECTOR3 </DIRECTION>
            <ENEMY_DIRECTION> DIRECTION </ENEMY_DIRECTION>
            <AVATAR_DBIDS> ARRAY <of> UINT64 </of> </AVATAR_DBIDS>
            <DIRECTIONS> ARRAY <of> DIRECTION </of> </DIRECTIONS>
            <ARRAY_OF_ARRAYS> ARRAY <of> AVATAR_DBIDS </of> </ARRAY_OF_ARRAYS>
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
            <INNER_ARRAY_IN_FD> FIXED_DICT
                <Properties>
                    <dbids>
                        <Type> ARRAY <of> DBID </of> </Type>
                    </dbids>
                </Properties>
            </INNER_ARRAY_IN_FD>
            <AVATAR_INFO_WITH_CONVERTER> FIXED_DICT
                <implementedBy> module_name.AvatarInfoConverter </implementedBy>
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
            </AVATAR_INFO_WITH_CONVERTER>
            <AVATAR_INFOS> ARRAY <of> AVATAR_INFO </of> </AVATAR_INFOS>
        </root>
        """
        with self._typesxml_path.open('w') as fh:
            fh.write(typesxml_content)

        entity_def_content = """
        <root>
            <Properties>
            </Properties>
            <BaseMethods>
                <method_01>
                    <Exposed />
                </method_01>
                <method_02>
                </method_02>
                <method_1>
                    <Exposed />
                    <Arg> INT32 </Arg>
                </method_1>
                <method_2>
                    <Exposed />
                    <Arg> AVATAR_NAME </Arg>
                    <Arg> AVATAR_UID </Arg>
                </method_2>
                <method_3>
                    <Arg> DBID </Arg>
                    <Arg> DIRECTION </Arg>
                    <Arg> ENEMY_DIRECTION </Arg>
                </method_3>
                <method_4>
                    <Arg> AVATAR_DBIDS </Arg> <!-- avatar_dbids -->
                    <Arg> DIRECTIONS </Arg> <!-- directions -->
                </method_4>
                <method_5>
                    <Arg> ARRAY_OF_ARRAYS </Arg>
                    <Arg> AVATAR_INFO </Arg>
                </method_5>
                <method_6>
                    <Arg> INNER_ARRAY_IN_FD </Arg>
                    <Arg> AVATAR_INFO_WITH_CONVERTER </Arg>
                    <Arg> AVATAR_INFOS </Arg>
                </method_6>
            </BaseMethods>
            <CellMethods>
                <not_generated_method>
                </not_generated_method>
            </CellMethods>
            <ClientMethods>
            </ClientMethods>
        </root>
        """
        with (self._entitydef_dir / 'Avatar.def').open('w') as fh:
            fh.write(entity_def_content)

        typesxml_parser = TypesXMLParser(self._typesxml_path)
        type_info_by_name = typesxml_parser.parse()

        typesxml_parser = EntityDefParser(self._entitydef_dir)
        entity_info = typesxml_parser.parse('Avatar')

        jinja_entity_template = \
"""class IBase{{ entity_info.name }}(abc.ABC):

    @property
    def cell(self) -> ICell{{ entity_info.name }}:
        pass
{% for info in entity_info.BaseMethods %}
    @abc.abstractmethod
    def {{ info.name }}({{ build_method_args(info, type_info_by_name) }}):
        pass
{% endfor %}

"""
        jinja_env = jinja2.Environment()
        jinja_env.globals.update(
            build_method_args=utils.build_method_args,
        )
        template = jinja_env.from_string(jinja_entity_template)
        res = template.render(
            type_info_by_name=type_info_by_name,
            entity_info=entity_info,
        )

        with open('/tmp/res.py', 'w') as fh:
            fh.write(res)

        assert res == """class IBaseAvatar(abc.ABC):

    @property
    def cell(self) -> ICellAvatar:
        pass

    @abc.abstractmethod
    def method_01(self,
                  entity_caller_id: int):
        pass

    @abc.abstractmethod
    def method_02(self):
        pass

    @abc.abstractmethod
    def method_1(self,
                 entity_caller_id: int,
                 arg_0: int):
        pass

    @abc.abstractmethod
    def method_2(self,
                 entity_caller_id: int,
                 arg_0: AvatarName,
                 arg_1: AvatarUid):
        pass

    @abc.abstractmethod
    def method_3(self,
                 arg_0: Dbid,
                 arg_1: Direction,
                 arg_2: EnemyDirection):
        pass

    @abc.abstractmethod
    def method_4(self,
                 avatar_dbids: AvatarDbids,
                 directions: Directions):
        pass

    @abc.abstractmethod
    def method_5(self,
                 arg_0: ArrayOfArrays,
                 arg_1: AvatarInfo):
        pass

    @abc.abstractmethod
    def method_6(self,
                 arg_0: InnerArrayInFd,
                 arg_1: AvatarInfoUserType,
                 arg_2: AvatarInfos):
        pass

"""
