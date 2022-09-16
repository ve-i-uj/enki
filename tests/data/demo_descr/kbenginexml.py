"""This generated module contains some settings from the "kbengine.xml" file."""

from typing import ClassVar

from tools.data import default_kbenginexml


class root(default_kbenginexml.root):
    class publish:
        script_version: ClassVar[str] = "0.1.0"
    class channelCommon:
        class timeout:
            external: ClassVar[float] = 60.0
    class cellapp:
        aliasEntityID: ClassVar[bool] = True
        entitydefAliasID: ClassVar[bool] = True