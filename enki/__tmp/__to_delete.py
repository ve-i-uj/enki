# # TODO: [burov_alexey@mail.ru 05.07.2025 14:50]
# # Алиасы выдаются уже в entity-rpc. Это не относится к декодированию.
# @classmethod
# def create_alias(cls, alias_name: str) -> type[UINT8]:
#     """Create alias of the "self" type."""

# TODO: [2022-11-18 15:54 burov_alexey@mail.ru]:
# Сервер может прислать потенциально число, которое больше,
# чем Python может поменять по формату "f". Пока так.
# if value > 2147483647 or value < -2147483647:
#     value = 0


# @dataclass
# class EntityComponentData:
#     component_type: int
#     owner_id: int
#     component_ent_id: int
#     count: int
#     entity_component_property_id: Optional[int] = None
#     name: Optional[str] = None
#     properties: dict[Any, Any] = dataclasses.field(default_factory=dict)


# class _EntityComponent(_BaseKBEType):
#     @property
#     def default(self) -> EntityComponentData:
#         return EntityComponentData(0, 0, 0, 0)

#     def decode(self, data: memoryview) -> Tuple[EntityComponentData, int]:
#         shift = 0
#         component_type, offset = UINT32.decode(data)
#         shift += offset
#         # TODO: [2022-08-27 10:31 burov_alexey@mail.ru]:
#         # Тут падает. Может быть из-за того, что если прокси создана
#         owner_id, offset = INT32.decode(data[shift:])
#         shift += offset

#         # UInt16 ComponentDescrsType ???
#         component_ent_id, offset = UINT16.decode(data[shift:])
#         shift += offset

#         count, offset = UINT16.decode(data[shift:])
#         shift += offset

#         inst = EntityComponentData(component_type, owner_id, component_ent_id, count)
#         return inst, shift

#     def encode(self, value: Any) -> bytes:
#         raise NotImplementedError
