"""Classes to describe generated code."""

from __future__ import annotations

import abc
import logging
from dataclasses import dataclass
from functools import cached_property
from typing import Optional

from enki.kbeenum import DistributionFlag
from enki.net.kbeclient import IKBEType, kbetype

logger = logging.getLogger(__name__)


@dataclass
class DataTypeDescr:
    """Specification of type from the file 'types.xml'."""

    @property
    def id(self) -> int:
        return None

    @property
    def base_type_name(self) -> str:
        return None

    @property
    def name(self) -> str:
        return None

    # decoder / encoder of kbe type_spec
    @property
    def kbetype(self) -> IKBEType:
        return None


    # FIXED_DICT data
    @property
    def module_name(self) -> Optional[str]:
        return None

    @property
    def pairs(self) -> Optional[dict[str, IKBEType]]:
        return None

    # ARRAY data
    @property
    def of(self) -> Optional[IKBEType]:
        return None

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
        if not self.name or self.name.startswith('_'):
            # It's an inner defined type
            return f'{self.base_type_name}_{self.id}'
        return self.name


@dataclass
class PropertyDesc:
    @property
    def uid(self) -> int:
        return None
  # unique identifier of the property
    @property
    def name(self) -> str:
        return None
  # name of the property
    @property
    def kbetype(self) -> IKBEType:
        return None
  # decoder / encoder
    @property
    def distribution_flag(self) -> DistributionFlag:
        return None

    @property
    def alias_id(self) -> int:
        return None
  # see aliasEntityID in kbengine.xml

    @property
    def component_type_name(self) -> str:
        return None
 # When code generating this value calculates


@dataclass
class MethodDesc:
    @property
    def uid(self) -> int:
        return None
  # the unique identifier of the method
    @property
    def alias_id(self) -> int:
        return None

    @property
    def name(self) -> str:
        return None

    @property
    def kbetypes(self) -> list[IKBEType]:
        return None


@dataclass
class EntityDesc:
    @property
    def name(self) -> str:
        return None

    @property
    def uid(self) -> int:
        return None

    @property
    def property_desc_by_id(self) -> dict[int, PropertyDesc]:
        return None

    @property
    def client_methods(self) -> dict[int, MethodDesc]:
        return None

    @property
    def base_methods(self) -> dict[int, MethodDesc]:
        return None

    @property
    def cell_methods(self) -> dict[int, MethodDesc]:
        return None

    @cached_property
    def is_optimized_cl_method_uid(self) -> bool:
        return any(m.alias_id != -1 for m in self.client_methods.values())

    @cached_property
    def property_desc_by_name(self) -> dict[str, PropertyDesc]:
        return {pd.name: pd for pd in self.property_desc_by_id.values()}

    @cached_property
    def component_names(self) -> set[str]:
        return set((
            prop_desc.name for prop_desc in self.property_desc_by_id.values()
            if isinstance(prop_desc.kbetype, kbetype._EntityComponent)
        ))

    @cached_property
    def property_desc_by_uid(self) -> dict[int, PropertyDesc]:
        return {pd.uid: pd for pd in self.property_desc_by_id.values()}


NO_ENTITY_DESCR = EntityDesc(
    'no entity', 0, {}, {}, {}, {}
)
