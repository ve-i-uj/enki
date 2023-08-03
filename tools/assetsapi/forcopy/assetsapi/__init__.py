# Это константа нужна в сгенерированном коде при старте в движке API.
# Нужно, чтобы в API сущности абстрактные методы и не абстрактные свойства не
# перекрывали методы и свойства сущности из Движка. Пример:
#
# class IBaseAccount(abc.ABC):
#     """This entity will be connected with client after authentication (base component)."""
#
#     if not assetsapi.IN_THE_ENGINE:
#
#         @property
#         def client(self) -> IClientAccount:
#             return IClientAccount() # type: ignore
#
#         @property
#         def cell(self) -> ICellAccount:
#             return ICellAccount() # type: ignore
#
#         @abc.abstractmethod
#         def req_get_avatars(self):
#             """A client requests lists of avatars."""
#
# В примере видно, что если код читается движком, то API сущности будет пустым.
# Если код читается анализатором PyLance, то API сущности будет считано
# анализатором.

IN_THE_ENGINE = True
try:
    import KBEngine
except ImportError:
    IN_THE_ENGINE = False
