import pathlib

import environs

from enki.settings import *


_env = environs.Env()

ASSETS_PATH: pathlib.Path = _env.path('ASSETS_PATH')
KBENGINE_XML_PATH = ASSETS_PATH / 'res' / 'server' / 'kbengine.xml'
