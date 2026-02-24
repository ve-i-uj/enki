"""This generated module contains some settings from the "kbengine.xml" file."""

from typing import ClassVar

from enki import default_kbenginexml


class root(default_kbenginexml.root):
    class publish:  # type: ignore
        script_version: ClassVar[str] = "0.1.0"
    class channelCommon:  # type: ignore
        class timeout:
            external: ClassVar[float] = 60.0
    class cellapp:  # type: ignore
        aliasEntityID: ClassVar[bool] = True
        entitydefAliasID: ClassVar[bool] = True
