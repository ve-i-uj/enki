"""Тесты для парсера директории assets/scripts/user_type."""

import collections
import shutil
import tempfile
from pathlib import Path

from unittest import TestCase

from enki.core.kbetype import FixedDict

from tools.parsers import typesxml
from tools.parsers.usertype import UsetTypeParser


class ParseTypesXMLParserTestCase(TestCase):
    """Unit tests of TypesXMLParser.parse"""

    def setUp(self):
        super().setUp()
        self._user_type_dir = Path(tempfile.TemporaryDirectory().name)
        self._user_type_dir.mkdir(exist_ok=True)
        self._module_path = self._user_type_dir / 'module_name.py'

    def tearDown(self):
        super().tearDown()
        assert isinstance(self._module_path, Path)
        self._module_path.unlink()
        shutil.rmtree(self._user_type_dir)

    def test_parse_user_type_class_methods(self):
        """Тест, когда адекватно оформлен модуль конвертера."""
        content = """
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
        with self._module_path.open('w') as fh:
            fh.write(content)

        inst = UsetTypeParser(self._user_type_dir)
        user_type_infos = inst.parse()
        info = user_type_infos[self._module_path.stem]

        assert info.module_name == self._module_path.stem
        assert info.converter_info.name == 'AvatarInfoConverter'
        assert info.converter_info.fd_type == 'AvatarInfo'
        assert info.converter_info.obj_type == 'AvatarInfoUserType'

    def test_parse_user_type_by_createObjFromDict(self):
        """Тест, когда аннотации есть только у createObjFromDict."""
        content = """
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
    def getDictFromObj(cls, obj):
        avatar_info = AvatarInfo()
        avatar_info.name = obj.name
        avatar_info.uid = obj.uid
        avatar_info.dbid = obj.dbid
        return avatar_info

    @classmethod
    def isSameType(cls, obj):
        return isinstance(obj, AvatarInfoUserType)
"""
        with self._module_path.open('w') as fh:
            fh.write(content)

        inst = UsetTypeParser(self._user_type_dir)
        user_type_infos = inst.parse()
        info = user_type_infos[self._module_path.stem]

        assert info.module_name == self._module_path.stem
        assert info.converter_info.name == 'AvatarInfoConverter'
        assert info.converter_info.fd_type == 'AvatarInfo'
        assert info.converter_info.obj_type == 'AvatarInfoUserType'

    def test_parse_user_type_by_getDictFromObj(self):
        """Тест, когда аннотации есть только у getDictFromObj."""
        content = """
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
    def createObjFromDict(cls, fixed_dict):
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
    def isSameType(cls, obj):
        return isinstance(obj, AvatarInfoUserType)
"""
        with self._module_path.open('w') as fh:
            fh.write(content)

        inst = UsetTypeParser(self._user_type_dir)
        user_type_infos = inst.parse()
        info = user_type_infos[self._module_path.stem]

        assert info.module_name == self._module_path.stem
        assert info.converter_info.name == 'AvatarInfoConverter'
        assert info.converter_info.fd_type == 'AvatarInfo'
        assert info.converter_info.obj_type == 'AvatarInfoUserType'

    def test_parse_user_type_no_annotations(self):
        """Тест, когда аннотаций и конвертера нет."""
        content = """
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
    def createObjFromDict(cls, fixed_dict):
        return AvatarInfoUserType(
            fixed_dict.name, fixed_dict.uid, fixed_dict.dbid
        )

    @classmethod
    def getDictFromObj(cls, obj):
        avatar_info = AvatarInfo()
        avatar_info.name = obj.name
        avatar_info.uid = obj.uid
        avatar_info.dbid = obj.dbid
        return avatar_info

    @classmethod
    def isSameType(cls, obj):
        return isinstance(obj, AvatarInfoUserType)
"""
        with self._module_path.open('w') as fh:
            fh.write(content)

        inst = UsetTypeParser(self._user_type_dir)
        user_type_infos = inst.parse()
        info = user_type_infos[self._module_path.stem]

        assert info.module_name == self._module_path.stem
        assert info.converter_info.name == 'AvatarInfoConverter'
        assert info.converter_info.fd_type == 'Any'
        assert info.converter_info.obj_type == 'Any'

    def test_parse_user_type_invalid_signature(self):
        """Конвертер имеет неправильную сигнатуру метода и не попадает в результат."""
        content = """
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
    def createObjFromDict(cls, fixed_dict):
        return AvatarInfoUserType(
            fixed_dict.name, fixed_dict.uid, fixed_dict.dbid
        )

    @classmethod
    def getDictFromObj(cls, obj, param1, param2):
        avatar_info = AvatarInfo()
        avatar_info.name = obj.name
        avatar_info.uid = obj.uid
        avatar_info.dbid = obj.dbid
        return avatar_info

    @classmethod
    def isSameType(cls, obj):
        return isinstance(obj, AvatarInfoUserType)
"""
        with self._module_path.open('w') as fh:
            fh.write(content)

        inst = UsetTypeParser(self._user_type_dir)
        user_type_infos = inst.parse()
        info = user_type_infos.get(self._module_path.stem)

        assert info is None

    def test_parse_user_type_static_methods(self):
        """Тест, когда конвертер имеет статические методы."""
        content = """
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

    @staticmethod
    def createObjFromDict(fixed_dict: AvatarInfo) -> AvatarInfoUserType:
        return AvatarInfoUserType(
            fixed_dict.name, fixed_dict.uid, fixed_dict.dbid
        )

    @staticmethod
    def getDictFromObj(obj: AvatarInfoUserType) -> AvatarInfo:
        avatar_info = AvatarInfo()
        avatar_info.name = obj.name
        avatar_info.uid = obj.uid
        avatar_info.dbid = obj.dbid
        return avatar_info

    @staticmethod
    def isSameType(obj: AvatarInfoUserType) -> bool:
        return isinstance(obj, AvatarInfoUserType)
"""
        with self._module_path.open('w') as fh:
            fh.write(content)

        inst = UsetTypeParser(self._user_type_dir)
        user_type_infos = inst.parse()
        info = user_type_infos[self._module_path.stem]

        assert info.module_name == self._module_path.stem
        assert info.converter_info.name == 'AvatarInfoConverter'
        assert info.converter_info.fd_type == 'AvatarInfo'
        assert info.converter_info.obj_type == 'AvatarInfoUserType'

    def test_parse_user_type_instance(self):
        """Тест, когда конвертер - это экземпляр класса конвертера."""
        content = """
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

    def createObjFromDict(self, fixed_dict: AvatarInfo) -> AvatarInfoUserType:
        return AvatarInfoUserType(
            fixed_dict.name, fixed_dict.uid, fixed_dict.dbid
        )

    def getDictFromObj(self, obj: AvatarInfoUserType) -> AvatarInfo:
        avatar_info = AvatarInfo()
        avatar_info.name = obj.name
        avatar_info.uid = obj.uid
        avatar_info.dbid = obj.dbid
        return avatar_info

    def isSameType(self, obj: AvatarInfoUserType) -> bool:
        return isinstance(obj, AvatarInfoUserType)

inst = AvatarInfoConverter()
"""
        with self._module_path.open('w') as fh:
            fh.write(content)

        inst = UsetTypeParser(self._user_type_dir)
        user_type_infos = inst.parse()
        info = user_type_infos[self._module_path.stem]

        assert info.module_name == self._module_path.stem
        assert info.converter_info.name == 'inst'
        assert info.converter_info.fd_type == 'AvatarInfo'
        assert info.converter_info.obj_type == 'AvatarInfoUserType'
