"""Classes to describe generated code."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from enki.kbeenum import DistributionFlag

    from .kbetype import IKBETypeDecoder


logger = logging.getLogger(__name__)


@dataclass
class DataTypeDescr:
    """Specification of type from the file 'types.xml'.

    Тип может быть каким угодно, поэтому при парсинге в описании сохраняются
    все возможные данные.
    """

    id: int
    base_type_name: str
    name: str
    # decoder / encoder of kbe type_spec
    kbetype: IKBETypeDecoder

    # FIXED_DICT data
    module_name: str | None = None
    pairs: dict[str, IKBETypeDecoder] | None = None

    # ARRAY data
    of: IKBETypeDecoder | None = None

    @property
    def is_alias(self) -> bool:
        return self.name != self.base_type_name

    @property
    def is_fixed_dict(self) -> bool:
        return self.pairs is not None

    @property
    def is_array(self) -> bool:
        return self.of is not None

    @property
    def type_name(self) -> str:
        if not self.name or self.name.startswith("_"):
            # It's an inner defined type
            return f"{self.base_type_name}_{self.id}"
        return self.name


@dataclass
class PropertyDesc:
    uid: int  # unique identifier of the property
    name: str  # name of the property
    kbetype: IKBETypeDecoder  # decoder / encoder
    distribution_flag: DistributionFlag
    alias_id: int  # see aliasEntityID in kbengine.xml

    component_type_name: str  # When code generating this value calculates


@dataclass
class MethodDesc:
    uid: int  # the unique identifier of the method
    alias_id: int
    name: str
    kbetypes: list[IKBETypeDecoder]


@dataclass
class EntityDesc:
    name: str
    uid: int
    property_desc_by_id: dict[int, PropertyDesc]
    client_methods: dict[int, MethodDesc]
    base_methods: dict[int, MethodDesc]
    cell_methods: dict[int, MethodDesc]

    @cached_property
    def is_optimized_cl_method_uid(self) -> bool:
        return any(m.alias_id != -1 for m in self.client_methods.values())

    @cached_property
    def property_desc_by_name(self) -> dict[str, PropertyDesc]:
        return {pd.name: pd for pd in self.property_desc_by_id.values()}

    @cached_property
    def component_names(self) -> set[str]:
        return {
            prop_desc.name
            for prop_desc in self.property_desc_by_id.values()
            if isinstance(prop_desc.kbetype, _EntityComponent)
        }

    @cached_property
    def property_desc_by_uid(self) -> dict[int, PropertyDesc]:
        return {pd.uid: pd for pd in self.property_desc_by_id.values()}


NO_ENTITY_DESCR = EntityDesc("no entity", 0, {}, {}, {}, {})
