"""???"""

import collections


class SpaceDataMgr:

    def __init__(self) -> None:
        self._data: dict[int, dict[str, str]] = collections.defaultdict(dict)

    def get_data(self, space_id: int, key: str) -> str:
        return self._data[space_id][key]

    def set_data(self, space_id: int, key: str, value: str):
        self._data[space_id][key] = value

    def del_data(self, space_id: int, key: str):
        del self._data[space_id][key]
