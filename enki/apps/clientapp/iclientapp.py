"""Интерфейсы клиента KBEngine."""

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class IBaseappClient(ABC):

    @abstractmethod
    async def logout(self):
        pass

    @abstractmethod
    def _on_kicked(self, entity_id: int, oldpassword: str, newpassword: str):
        """Следит за принудительным отключением."""

    @abstractmethod
    def _on_relogin(self, entity_id: int, oldpassword: str, newpassword: str):
        """Следит за переподлючениями."""
