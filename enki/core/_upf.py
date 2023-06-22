"""
KBEngine добавляет этот модуль, чтобы описать сущностей сериализованных через
pickle при передаче данных между компонентами.

Я не сильно вдавался в логику сериализации EntityCall и просто повторил
интерфейс, чтобы работали обработчики / парсеры для BaseappMgr::reqCreateEntityAnywhere
и Baseapp::onCreateEntityAnywhere. Они заработали.
"""

class EntityCall:

    ENTITYCALL_TYPE_CELL = 0
    ENTITYCALL_TYPE_BASE = 1

    def __init__(self, *args, **kwargs) -> None:
        self._args = args
        self._kwargs = kwargs
        self.id = 0
        self.className = ''
        self.type = self.ENTITYCALL_TYPE_BASE
        self.pBundle = None

    def isBase(self) -> bool:
        return self.type == self.ENTITYCALL_TYPE_BASE

    def isCell(self) -> bool:
        return self.type == self.ENTITYCALL_TYPE_CELL

    def newCall(self, *args, **kwargs):
        pass

    def sendCall(self, inBundle):
        pass

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(*{self._args})'

    __repr__ = __str__
