from pathlib import Path

# Директория расположения шаблонов для генерации кода
JINJA_TEMPLS_DIR: Path = Path(__file__).parent / 'templates'
TYPESXML_JINJA_TEMPLATE_PATH = JINJA_TEMPLS_DIR / 'typesxml.py.jinja'
