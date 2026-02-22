"""Code generators.

Generate code by parsed data.
"""

import dataclasses
import functools
import logging
import os
import shutil
from pathlib import Path
from types import ModuleType

import jinja2
from enki.kbetype.decoders.idecoders import IKBETypeDecoder
from enki.kbetype.ikbetype import IKBEType
from enki.msg_parser.client_msg_parser import (
    ParsedEntityInfo,
    ParsedMethodInfo,
    ParsedTypeInfo,
)
from enki.msg_parser.client_msg_parser import (
    ParsedServerErrorInfo,
)

from enki import kbetype
from enki import kbeenum
from enki.command.server_api.importClientEntityDef_cmd import (
    ImportClientEntityDefCommand,
)
from enki.misc import devonly
from enki.msg.msg_descr import MsgArgsType, MsgDescr
from enki.net.addr import Addr
from tools.parsers import (
    DefClassData,
    EntitiesXMLParser,
    EntityDefParser,
    KBEngineXMLParser,
    ParsedKBEngineXMLInfo,
)

logger = logging.getLogger(__name__)


# Директория расположения шаблонов для генерации кода
_JINJA_TEMPLS_DIR: Path = Path(__file__).parent / "templates"

_PROJECT_SITE: str = "https://github.com/ve-i-uj/enki"

_SIMPLE_TYPE_NAMES = [
    "BLOB",
    "BOOL",
    "DOUBLE",
    "ENTITYCALL",
    "FLOAT",
    "INT8",
    "INT16",
    "INT32",
    "INT64",
    "KBE_DATATYPE2ID_MAX",
    "PYTHON",
    "PY_DICT",
    "PY_LIST",
    "PY_TUPLE",
    "STRING",
    "UINT8",
    "UINT8_ARRAY",
    "UINT16",
    "UINT32",
    "UINT64",
    "UNICODE",
    "VECTOR2",
    "VECTOR3",
    "VECTOR4",
    "ENTITY_COMPONENT",
]


jinja_env = jinja2.Environment()

_APP_HEADER_TEMPLATE = '''"""Messages of {name}."""

from enki.kbetype import *
from enki.msg.msg_descr import MsgDescr
'''

_APP_MSG_TEMPLATE = """
{short_name} = MsgDescr(
    id={id},
    name="{name}",
    args_type={args_type},
    args={args},
    desc="{desc}"
)
"""

_SERVERERROR_HEADER_TEMPLATE = '''"""Server errors."""

from enki.msg_parser.client_msg_parser.client_msg_pasrser import (
    ParsedServerErrorInfo,
)
'''

_SERVERERROR_TEMPLATE = """
{name} = ParsedServerErrorInfo(
    id={id},
    name="{name}",
    desc="{desc}"
)
"""

_TYPE_HEADER_TEMPLATE = '''"""Generated types represent types of the file types.xml"""

from typing import TypeAlias

from enki.kbetype import *

'''


def _to_string(msg_spec: MsgDescr):
    """Convert the message description to it string representation."""
    args_type = MsgArgsType(msg_spec.args_type)
    if not msg_spec.args:
        if args_type == MsgArgsType.VARIABLE:
            args = "(UINT8_ARRAY, )"
        else:
            args = "tuple()"
    else:
        args = "\n" + "\n".join(f"        {f.__name__}," for f in msg_spec.args)
        args = f"({args}\n    )"

    return _APP_MSG_TEMPLATE.format(
        short_name=msg_spec.name.split("::")[1],
        id=msg_spec.id,
        name=msg_spec.name,
        args_type=str(MsgArgsType(msg_spec.args_type)),
        args=args,
        desc=msg_spec.desc,
    )


def _chunker(seq, size):
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


class MessagesCodeGen:
    def __init__(self, dst_path: Path) -> None:
        # Root directory of modules contained app messages
        self._dst_path = dst_path
        self._dst_path.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        client_msg_specs: list[MsgDescr],
        loginapp_msg_specs: list[MsgDescr],
        baseapp_msg_specs: list[MsgDescr],
    ) -> None:
        # Filter specs by apps
        app_msg_specs = {
            "client": client_msg_specs,
            "loginapp": loginapp_msg_specs,
            "baseappp": baseapp_msg_specs,
        }
        for app_name, msg_specs in app_msg_specs.items():
            dst_path = self._dst_path / app_name / "_generated.py"
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            with dst_path.open("w") as fh:
                fh.write(
                    _APP_HEADER_TEMPLATE.format(name=app_name.capitalize())
                )
                for msg_spec in sorted(msg_specs, key=lambda s: s.id):
                    fh.write(_to_string(msg_spec))

                if app_name == "client":
                    pairs = []
                    for msg_spec in sorted(msg_specs, key=lambda s: s.id):
                        short_name = msg_spec.short_name
                        pairs.append(f"    {short_name}.id: {short_name}")
                    spec_by_id_str = "\nSPEC_BY_ID = {{\n{}\n}}".format(
                        ",\n".join(sorted(pairs))
                    )
                    fh.write(spec_by_id_str)
                    fh.write("\n")

                all_lines = []
                module_attrs = [f"'{s.short_name}'" for s in msg_specs]
                if app_name == "client":
                    module_attrs.append("'SPEC_BY_ID'")
                for chunk in _chunker(sorted(module_attrs), 1):
                    all_lines.append("    " + ", ".join(chunk))
                fh.write(
                    "\n__all__ = (\n{}\n)\n".format(
                        ",\n".join(sorted(all_lines))
                    )
                )

            logger.info(
                '%s messages have been written (dst file = "%s")',
                app_name.capitalize(),
                dst_path,
            )

        with (self._dst_path / "__init__.py").open("w") as fh:
            fh.write("from . import baseapp, client, loginapp")


class TypesCodeGen:
    def __init__(self, type_dst_path: Path) -> None:
        self._type_dst_path = type_dst_path
        self._type_dst_path.parent.mkdir(parents=True, exist_ok=True)

    def generate(self, parsed_types: list[ParsedTypeInfo]) -> None:
        """Write code for types."""
        parsed_types[:] = self._reorder_types(parsed_types)
        type_by_id = {t.id: t for t in parsed_types}
        # assert type_count == len(parsed_types)

        added_decoders = {}

        with self._type_dst_path.open("w") as fh:
            fh.write(_TYPE_HEADER_TEMPLATE)

            for parsed_type_info in parsed_types:
                pti = parsed_type_info

                new_type_name = "KBE" + "".join(
                    w.capitalize() for w in pti.type_name.split("_")
                )

                if parsed_type_info.base_type_name in _SIMPLE_TYPE_NAMES:
                    # Встроенные декодеры импортируются по умолчанию
                    decoder: IKBETypeDecoder = getattr(
                        kbetype, pti.base_type_name
                    )

                    if parsed_type_info.is_alias:
                        base_type_py_name = decoder.get_kbe_type().__name__
                        type_decoder_str = f"""{pti.type_name}: TypeAlias = {pti.base_type_name}"""

                        py_type_str = (
                            f"{new_type_name}: TypeAlias = {base_type_py_name}"
                        )

                        fh.write(py_type_str + "\n")
                        fh.write(type_decoder_str + "\n")
                        fh.write("\n")
                    else:
                        # У встроенных типов capitalize() может сломать имя
                        new_type_name = decoder.get_kbe_type().__name__

                    added_decoders[pti.name] = new_type_name
                elif parsed_type_info.is_fixed_dict:
                    assert pti.fd_type_id_by_key

                    # Название типа, который будет возвращать декодер
                    fh.write(
                        f"""
@dataclass
class {new_type_name}FixedDict(KBEFixedDict):
"""
                    )
                    # Имена ключей и их типы
                    for k_name, k_type_id in pti.fd_type_id_by_key.items():
                        value_type_name = added_decoders[
                            type_by_id[k_type_id].type_name
                        ]
                        fh.write(f"    {k_name}: {value_type_name}\n")

                    # Декодеры для значений словаря
                    fh.write(
                        f"""

@dataclass
class {new_type_name}FixedDictDecoders(FixedDictDecoders):
"""
                    )
                    for k_name, k_type_id in pti.fd_type_id_by_key.items():
                        decoder_name = type_by_id[k_type_id].type_name
                        fh.write(f"    {k_name} = {decoder_name}\n")

                    # Декодер для всего FIXED_DICT
                    fh.write(
                        f"""

class {pti.type_name}(FIXED_DICT[{new_type_name}FixedDict, {new_type_name}FixedDictDecoders]):
    _decoders = {new_type_name}FixedDictDecoders

    _kbe_type = {new_type_name}FixedDict

    @classmethod
    def get_kbe_type(cls) -> type[{new_type_name}FixedDict]:
        return cls._kbe_type

"""
                    )

                    added_decoders[pti.type_name] = f"{new_type_name}FixedDict"

                elif parsed_type_info.is_array:
                    assert parsed_type_info.arr_of_id is not None
                    elem_decoder_name = type_by_id[
                        parsed_type_info.arr_of_id
                    ].type_name
                    elem_type_name = added_decoders[elem_decoder_name]

                    py_arr_type_name = f"{elem_type_name}Array"
                    if py_arr_type_name not in set(added_decoders.values()):
                        fh.write(
                            f"{py_arr_type_name}: TypeAlias = KBEArray[{elem_type_name}]\n\n"
                        )

                    fh.write(
                        f'''
class {pti.type_name}(ARRAY[{elem_type_name}, {elem_decoder_name}]):
    """Декодер для типа массива {elem_decoder_name}."""

    _element_decoder = {elem_decoder_name}
    _kbe_type = {elem_type_name}Array

    @classmethod
    def get_kbe_type(cls) -> type[{elem_type_name}Array]:
        return cls._kbe_type

    @classmethod
    def _get_element_decoder(cls) -> type[{elem_decoder_name}]:
        return cls._element_decoder

'''
                    )

                    added_decoders[pti.type_name] = f"{elem_type_name}Array"
                else:
                    msg = "Unexpected case"
                    raise devonly.LogicError(msg)

            pairs = []
            for parsed_type_info in sorted(parsed_types, key=lambda s: s.id):
                pairs.append(
                    f"    {parsed_type_info.id}: {parsed_type_info.type_name}"
                )
            spec_by_id_str = "\nDECODER_BY_ID = {{\n{}\n}}".format(
                ",\n".join(pairs)
            )
            fh.write(spec_by_id_str)
            fh.write("\n")

        with (self._type_dst_path.parent / "__init__.py").open("w") as fh:
            fh.write("from ._generated import *")

        logger.info(
            f'Server types have been written (dst file = "{self._type_dst_path}")'
        )

    def _reorder_types(self, type_specs: list[ParsedTypeInfo]):
        """Reorder types that they can be referenced by each other."""
        new_type_specs = []
        # types that need reorder
        broken_type_specs = []
        for type_spec in type_specs:
            if type_spec.base_type_name in _SIMPLE_TYPE_NAMES:
                new_type_specs.append(type_spec)
                continue
            # Alias on FIXED_DICT or ARRAY cannot happen. Alias can refer on
            # a base kbe type.
            if type_spec.arr_of_id and type_spec.arr_of_id > type_spec.id:
                logger.warning("Unexpected behaviour (%s)", type_spec)
                broken_type_specs.append(type_spec)
                # TODO: [2022-08-01 23:07 burov_alexey@mail.ru]:
                # В type_spec.name будет '_BAG_values22_ArrayType'
                continue
                # raise devonly.LogicError('Unexpected behaviour')
            if type_spec.fd_type_id_by_key:
                # Check types of FD keys
                broken = False
                for type_id in type_spec.fd_type_id_by_key.values():
                    if type_id > type_spec.id:
                        broken = True
                        broken_type_specs.append(type_spec)
                        break
                if broken:
                    continue

            new_type_specs.append(type_spec)

        # TODO: [05.01.2021 16:45 burov_alexey@mail.ru]
        # What if broken type has referred to broken type too
        while broken_type_specs:
            type_spec = broken_type_specs[0]
            del broken_type_specs[0]
            if type_spec.is_fixed_dict:
                max_type_id = max(type_spec.fd_type_id_by_key.values())
            elif type_spec.is_array:
                max_type_id = type_spec.arr_of_id
            else:
                msg = "Unexpected behaviour"
                raise devonly.LogicError(msg)
            # Insert this type after all declaration of its key types
            index = None
            for i, new_type_spec in enumerate(new_type_specs):
                if new_type_spec.id == max_type_id:
                    index = i
                    break
            else:
                broken_type_specs.append(type_spec)
                continue
            if index + 1 == len(new_type_specs):
                new_type_specs.append(type_spec)
            else:
                new_type_specs.insert(index + 1, type_spec)

        return new_type_specs


def get_python_type(deftype: ModuleType, typesxml_id: int) -> str:
    """Returns the python type of the property."""
    kbe_type = deftype.DECODER_BY_ID[typesxml_id].kbetype
    return kbe_type.__orig_bases__[0].__args__[0].__name__


def get_type_name(deftype: ModuleType, typesxml_id: int) -> str:
    type_spec = deftype.DECODER_BY_ID[typesxml_id]
    return type_spec.name if type_spec.name else type_spec.type_name


def get_default_value(deftype: ModuleType, typesxml_id: int) -> str:
    spec = deftype.DECODER_BY_ID[typesxml_id]
    return f"deftype.{spec.name}.default"


def build_method_args(
    deftype: ModuleType, meth_dc: ParsedMethodInfo, need_eid: bool = True
) -> str:
    args = (
        ["self"]
        + (["entity_id: int"] if need_eid else [])
        + [
            f"{get_type_name(deftype, t).lower()}_{i}: {get_python_type(deftype, t)}"
            for i, t in enumerate(meth_dc.arg_types)
        ]
    )
    return f",\n{' ' * (9 + len(meth_dc.name))}".join(args)


def build_args(
    deftype: ModuleType, meth_dc: ParsedMethodInfo, need_brackets: bool = True
) -> str:
    if len(meth_dc.arg_types) == 0:
        return "()" if need_brackets else ""
    args = ", ".join(
        f"{get_type_name(deftype, t).lower()}_{i}"
        for i, t in enumerate(meth_dc.arg_types)
    )
    return (f"({args}, )") if need_brackets else args


class EntitySerializersCodeGen:
    """Генерирует сириализаторы для RPC на сервер."""

    def __init__(self, eserializer_dst_path: Path) -> None:
        self._eserializer_dst_path = eserializer_dst_path
        self._eserializer_dst_path.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        entities: list[ParsedEntityInfo],
        assets_ent_data: dict[str, DefClassData],
        assets_ent_c_data: dict[str, DefClassData],
        deftype: ModuleType,
    ) -> None:
        """Write code for entities serializers."""
        jinja_env.globals.update(
            get_python_type=functools.partial(get_python_type, deftype),
            build_method_args=functools.partial(build_method_args, deftype),
            get_default_value=functools.partial(get_default_value, deftype),
            get_type_name=functools.partial(get_type_name, deftype),
            kbeenum=kbeenum,
        )

        for entity_spec in entities:
            is_entity_component: bool = entity_spec.name in assets_ent_c_data
            if is_entity_component:
                ec_type_by_name: dict[str, str] = {}
                dst_path = self._eserializer_dst_path / "components"
                template_path = (
                    _JINJA_TEMPLS_DIR / "eserializer" / "ecserializer.py.jinja"
                )
            else:
                ec_type_by_name: dict[str, str] = {
                    d.name: d.type
                    for d in assets_ent_data[entity_spec.name].Components
                }
                dst_path = self._eserializer_dst_path
                # TODO: [2022-11-12 08:46 burov_alexey@mail.ru]:
                # В настройки
                template_path = (
                    _JINJA_TEMPLS_DIR / "eserializer" / "eserializer.py.jinja"
                )

            dst_path.mkdir(exist_ok=True)
            with (dst_path / f"{entity_spec.name}.py").open("w") as fh:
                with open(template_path) as tmpl_fh:
                    template = jinja_env.from_string(tmpl_fh.read())
                fh.write(
                    template.render(
                        entity_spec=entity_spec,
                        assets_ent_data=assets_ent_data,
                        ec_type_by_name=ec_type_by_name,
                        assets_ent_c_data=assets_ent_c_data,
                    )
                )

        ec_types_by_ename = {}
        for entity_spec in entities:
            if entity_spec.name not in assets_ent_data:
                continue
            ec_types_by_ename[entity_spec.name] = {}
            for d in assets_ent_data[entity_spec.name].Components:
                ec_types_by_ename[entity_spec.name][d.name] = d.type

        with (self._eserializer_dst_path / "__init__.py").open("w") as fh:
            # TODO: [2022-11-12 11:54 burov_alexey@mail.ru]:
            # В настройки
            with open(
                _JINJA_TEMPLS_DIR
                / "eserializer"
                / "eserializer_init_module.py.jinja"
            ) as tmpl_fh:
                template = jinja_env.from_string(tmpl_fh.read())
            fh.write(
                template.render(
                    entities=entities,
                    assets_ent_c_data=assets_ent_c_data,
                )
            )

        (self._eserializer_dst_path / "components").mkdir(exist_ok=True)
        with (self._eserializer_dst_path / "components" / "__init__.py").open(
            "w"
        ) as fh:
            pass

        with (self._eserializer_dst_path.parent / "__init__.py").open(
            "w"
        ) as fh:
            fh.write("from ._generated import *")

        logger.info(
            f'Entities have been written (dst file = "{self._eserializer_dst_path}")'
        )


class EntitiesCodeGen:
    def __init__(self, entity_dst_path: Path) -> None:
        self._entity_dst_path = entity_dst_path
        self._entity_dst_path.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        entities: list[ParsedEntityInfo],
        assets_ent_data: dict[str, DefClassData],
        assets_ent_c_data: dict[str, DefClassData],
        deftype: ModuleType,
    ) -> None:
        """Write code for entities."""
        jinja_env.globals.update(
            get_python_type=functools.partial(get_python_type, deftype),
            build_method_args=functools.partial(build_method_args, deftype),
            build_args=functools.partial(build_args, deftype),
            get_default_value=functools.partial(get_default_value, deftype),
            get_type_name=functools.partial(get_type_name, deftype),
            kbeenum=kbeenum,
        )

        for entity_spec in entities:
            is_entity_component: bool = entity_spec.name in assets_ent_c_data
            if is_entity_component:
                ec_type_by_name: dict[str, str] = {}
                dst_path = self._entity_dst_path / "components"
                template_path = (
                    _JINJA_TEMPLS_DIR
                    / "gameentity"
                    / "entity_component.py.jinja"
                )
            else:
                ec_type_by_name: dict[str, str] = {
                    d.name: d.type
                    for d in assets_ent_data[entity_spec.name].Components
                }
                dst_path = self._entity_dst_path
                # TODO: [2022-11-12 08:46 burov_alexey@mail.ru]:
                # В настройки
                template_path = (
                    _JINJA_TEMPLS_DIR / "gameentity" / "entity.py.jinja"
                )

            dst_path.mkdir(exist_ok=True)
            with (dst_path / f"{entity_spec.name}.py").open("w") as fh:
                with open(template_path) as tmpl_fh:
                    template = jinja_env.from_string(tmpl_fh.read())
                fh.write(
                    template.render(
                        entity_spec=entity_spec,
                        assets_ent_data=assets_ent_data,
                        ec_type_by_name=ec_type_by_name,
                        assets_ent_c_data=assets_ent_c_data,
                    )
                )

        ec_types_by_ename = {}
        for entity_spec in entities:
            if entity_spec.name not in assets_ent_data:
                continue
            ec_types_by_ename[entity_spec.name] = {}
            for d in assets_ent_data[entity_spec.name].Components:
                ec_types_by_ename[entity_spec.name][d.name] = d.type

        with (CodeGenDstPath.ROOT / "description.py").open("w") as fh:
            with open(
                _JINJA_TEMPLS_DIR / "gameentity" / "description.py.jinja"
            ) as tmpl_fh:
                template = jinja_env.from_string(tmpl_fh.read())
            fh.write(
                template.render(
                    entities=entities,
                    ec_types_by_ename=ec_types_by_ename,
                    assets_ent_c_data=assets_ent_c_data,
                )
            )

        with (self._entity_dst_path / "__init__.py").open("w") as fh:
            with open(
                _JINJA_TEMPLS_DIR / "gameentity" / "entity_init_module.py.jinja"
            ) as tmpl_fh:
                template = jinja_env.from_string(tmpl_fh.read())
            fh.write(
                template.render(
                    entities=entities,
                    assets_ent_c_data=assets_ent_c_data,
                )
            )

        (self._entity_dst_path / "components").mkdir(exist_ok=True)
        with (self._entity_dst_path / "components" / "__init__.py").open(
            "w"
        ) as fh:
            pass

        with (self._entity_dst_path.parent / "__init__.py").open("w") as fh:
            fh.write("from ._generated import *")

        logger.info(
            f'Entities have been written (dst file = "{self._entity_dst_path}")'
        )


class ErrorCodeGen:
    def __init__(self, dst_path: Path) -> None:
        self._dst_path = dst_path
        self._dst_path.parent.mkdir(parents=True, exist_ok=True)

    def generate(self, spec: list[ParsedServerErrorInfo]) -> None:
        spec.sort(key=lambda e: e.name)
        with self._dst_path.open("w") as fh:
            fh.write(_SERVERERROR_HEADER_TEMPLATE)

            for error_spec in spec:
                fh.write(
                    _SERVERERROR_TEMPLATE.format(
                        **dataclasses.asdict(error_spec)
                    )
                )

            pairs = []
            for error_spec in sorted(spec, key=lambda s: s.id):
                pairs.append(f"    {error_spec.id}: {error_spec.name}")
            spec_by_id_str = "\nERROR_BY_ID = {{\n{}\n}}".format(
                ",\n".join(pairs)
            )
            fh.write(spec_by_id_str)
            fh.write("\n")

            all_lines = []
            for chunk in _chunker(
                [f"'{s.name}'" for s in spec] + ["'ERROR_BY_ID'"], 1
            ):
                all_lines.append("    " + ", ".join(chunk))
            fh.write(
                "\n__all__ = (\n{}\n)\n".format(",\n".join(sorted(all_lines)))
            )

        logger.info(
            'Server errors have been written (dst file = "%s")', self._dst_path
        )


class KBEngineXMLDataCodeGen:
    def __init__(self, entity_dst_path: Path) -> None:
        self._entity_dst_path = entity_dst_path
        self._entity_dst_path.parent.mkdir(parents=True, exist_ok=True)

    def generate(self, config_dc: ParsedKBEngineXMLInfo) -> None:
        with (self._entity_dst_path).open("w") as fh:
            with open(_JINJA_TEMPLS_DIR / "kbenginexml.py.jinja") as tmpl_fh:
                template = jinja_env.from_string(tmpl_fh.read())
            fh.write(template.render(root=config_dc.root))


class CodeGenDstPath:

    def __init__(self, game_generated_client_api_dir: Path) -> None:
        self._game_generated_client_api_dir = game_generated_client_api_dir

    @property
    def ROOT(self) -> Path:
        return self._game_generated_client_api_dir

    @property
    def APP(self) -> Path:
        return self.ROOT / "app"

    @property
    def SERIALIZER_ENTITY(self) -> Path:
        return self.ROOT / "eserializer" / "_generated"

    @property
    def ENTITY(self) -> Path:
        return self.ROOT / "gameentity" / "_generated"

    @property
    def TYPE(self) -> Path:
        return self.ROOT / "deftype/_generated.py"

    @property
    def SERVERERROR(self) -> Path:
        return self.ROOT / "servererror/_generated.py"

    @property
    def KBENGINE_XML(self) -> Path:
        return self.ROOT / "kbenginexml.py"


class CodeGenSrcPath:

    def __init__(self, game_assets_dir: Path) -> None:
        self._game_assets_dir = game_assets_dir

    @property
    def ASSETS_ROOT(self) -> Path:
        return self._game_assets_dir

    @property
    def KBENGINE_XML_PATH(self) -> Path:
        return self.ASSETS_ROOT / "res" / "server" / "kbengine.xml"

    @property
    def ENTITIES_XML_PATH(self) -> Path:
        return self.ASSETS_ROOT / "scripts" / "entities.xml"

    @property
    def ENTITY_DEFS_DIR(self) -> Path:
        return self.ASSETS_ROOT / "scripts" / "entity_defs"

    @property
    def ENTITY_DEFS_COMPONENT_DIR(self) -> Path:
        return self.ASSETS_ROOT / "scripts" / "entity_defs" / "components"


async def generate_code(
    game_assets_dir: Path,
    login_name: str,
    password: str,
    game_generated_client_api_dir: Path,
    loginapp_addr: Addr,
) -> None:
    code_gen_src_path = CodeGenSrcPath(game_assets_dir)
    code_gen_dst_path = CodeGenDstPath(game_generated_client_api_dir)

    # Parse assets info
    assets_ent_data: dict[str, DefClassData] = {}
    entities_xml_parser = EntitiesXMLParser(code_gen_src_path.ENTITIES_XML_PATH)
    entity_def_parser = EntityDefParser(code_gen_src_path.ENTITY_DEFS_DIR)
    for ent_data in entities_xml_parser.parse().get_all():
        assets_ent_data[ent_data.name] = entity_def_parser.parse(ent_data.name)

    # Read component entities
    assets_ent_c_data: dict[str, DefClassData] = {}
    entity_def_parser_for_components = EntityDefParser(
        code_gen_src_path.ENTITY_DEFS_COMPONENT_DIR
    )
    for filename in os.listdir(code_gen_src_path.ENTITY_DEFS_COMPONENT_DIR):
        if filename.endswith(".def") and filename[0].isupper():
            comp_name: str = filename.rsplit(".", 1)[0]
            assets_ent_c_data[comp_name] = (
                entity_def_parser_for_components.parse(comp_name)
            )

    # Generate entity descriptions
    if code_gen_dst_path.ROOT.exists():
        shutil.rmtree(code_gen_dst_path.ROOT)
    code_gen_dst_path.ROOT.mkdir(parents=True)
    with (code_gen_dst_path.ROOT / "__init__.py").open("w") as fh:
        fh.write(
            f'"""The package contains generated python code for '
            f'the KBEngine client.\n\nGenerated by the "enki" '
            f'project <{_PROJECT_SITE}>\n"""\n\n'
        )
        fh.write(
            "from . import deftype, eserializer, kbenginexml, gameentity, description\n"
        )

    # Generate entity descriptions
    type_dst_path = code_gen_dst_path.TYPE
    entity_dst_path = code_gen_dst_path.ENTITY
    eserialier_dst_path = code_gen_dst_path.SERIALIZER_ENTITY

    importClientEntityDef_cmd = ImportClientEntityDefCommand(  # noqa: N806
        login_name, password, loginapp_addr
    )
    importClientEntityDef_res = await importClientEntityDef_cmd.execute()
    if not importClientEntityDef_res.success:
        logger.error(
            "The messages from Loginapp cannot be requested (err = '%s')",
            importClientEntityDef_res.text,
        )
        return

    assert importClientEntityDef_res.result is not None

    type_code_gen = TypesCodeGen(type_dst_path)
    type_code_gen.generate(importClientEntityDef_res.result.types)

    # Это нужно в процедуру (загрузка deftype)
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "deftype", CodeGenDstPath.TYPE
    )
    assert spec is not None
    assert spec.loader is not None
    module: ModuleType = importlib.util.module_from_spec(spec)
    sys.modules["deftype"] = module
    spec.loader.exec_module(module)

    entity_code_gen = EntitiesCodeGen(entity_dst_path)
    entity_code_gen.generate(
        importClientEntityDef_res.result.entities,
        assets_ent_data,
        assets_ent_c_data,
        module,
    )

    eserializer_code_gen = EntitySerializersCodeGen(eserialier_dst_path)
    eserializer_code_gen.generate(
        importClientEntityDef_res.result.entities,
        assets_ent_data,
        assets_ent_c_data,
        module,
    )

    # Generate data of kbengine.xml
    logger.info(
        f"Generate settings from kbengine.xml ... (to "
        f'"{CodeGenDstPath.KBENGINE_XML}")'
    )
    data = KBEngineXMLParser(KBENGINE_XML_PATH).parse()
    code_gen = KBEngineXMLDataCodeGen(CodeGenDstPath.KBENGINE_XML)
    code_gen.generate(data)
