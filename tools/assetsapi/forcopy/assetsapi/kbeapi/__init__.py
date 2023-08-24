"""
Пакет содержит модули движка (KBEngine и Math), которые будут или API
в случае локальной разработки, или модулями непосредственно движка в случае
рантайма.
"""

from . import Math

from ._entityapi import *
from ._kbengineapi import *
