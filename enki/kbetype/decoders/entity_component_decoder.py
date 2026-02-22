from enki.kbetype.decoders.basic_data_type_decoders import INT32, UINT16, UINT32
from enki.kbetype.decoders.idecoders import IKBETypeDecoder
from enki.kbetype.pytypes.entity_component import EntityComponentData


class ENTITY_COMPONENT(IKBETypeDecoder[EntityComponentData]):
    """Декодер/кодер для типа данных ENTITY_COMPONENT.

    Структура данных в бинарном представлении:
    - component_type (UINT32): тип компонента
    - owner_id (INT32): ID владельца
    - component_ent_id (UINT16): ID компонента (ComponentDescrsType)
    - count (UINT16): счетчик/количество
    """

    _kbe_type = EntityComponentData

    @classmethod
    def get_kbe_type(cls) -> type[EntityComponentData]:
        """Возвращает тип данных, с которым работает этот декодер.

        Returns:
            type[EntityComponentData]: класс EntityComponentData

        """
        return cls._kbe_type

    @classmethod
    def decode(cls, data: memoryview) -> tuple[EntityComponentData, int]:
        """Декодирует бинарные данные в объект EntityComponentData.

        Args:
            data: memoryview с бинарными данными для декодирования

        Returns:
            tuple[EntityComponentData, int]: кортеж из декодированного объекта
                и количества прочитанных байт

        """
        total_offset = 0

        # Декодируем тип компонента (UINT32)
        component_type, offset = UINT32.decode(data)
        total_offset += offset

        # Декодируем ID владельца (INT32)
        owner_id, offset = INT32.decode(data[total_offset:])
        total_offset += offset

        # Декодируем ID компонента (UINT16) - ComponentDescrsType
        component_ent_id, offset = UINT16.decode(data[total_offset:])
        total_offset += offset

        # Декодируем счетчик (UINT16)
        count, offset = UINT16.decode(data[total_offset:])
        total_offset += offset

        # Создаем объект EntityComponentData
        inst = EntityComponentData(
            component_type, owner_id, component_ent_id, count
        )

        return inst, total_offset

    @classmethod
    def encode(cls, value: EntityComponentData) -> bytes:
        """Кодирует объект EntityComponentData в бинарное представление.

        Структура закодированных данных:
        - component_type (4 байта, UINT32)
        - owner_id (4 байта, INT32)
        - component_ent_id (2 байта, UINT16)
        - count (2 байта, UINT16)

        Args:
            value: объект EntityComponentData для кодирования

        Returns:
            bytes: закодированные бинарные данные

        Raises:
            TypeError: если value не является экземпляром EntityComponentData

        """
        if not isinstance(value, EntityComponentData):
            msg = f"Expected EntityComponentData, got {type(value).__name__}"
            raise TypeError(
                msg
            )

        # Кодируем каждое поле в правильном порядке
        component_type_bytes = UINT32.encode(value.component_type)
        owner_id_bytes = INT32.encode(value.owner_id)
        component_ent_id_bytes = UINT16.encode(value.component_ent_id)
        count_bytes = UINT16.encode(value.count)

        # Объединяем все закодированные данные
        return (
            component_type_bytes
            + owner_id_bytes
            + component_ent_id_bytes
            + count_bytes
        )
