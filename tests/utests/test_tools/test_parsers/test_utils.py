"""Тесты парсера файла entities.xml."""

from pathlib import Path
import tempfile
import unittest

from tools.parsers import utils, EntitiesXMLParser, EntityDefParser, EntitiesXMLData


class NormalizeEntitiesxmlTest(unittest.TestCase):
    """Тесты для процедуры normalize_entitiesxml."""

    def setUp(self) -> None:
        super().setUp()
        data_dir = Path(__file__).parent.parent.parent.parent / 'data'
        self._entities_xml_path = (
            data_dir / 'demo_assets_confs' / 'demo_entities.xml').resolve()
        self._entitydef_dir = (
            data_dir / 'demo_assets_confs' / 'demo_entity_defs').resolve()

    def _check(self, updated_exml_data: EntitiesXMLData):
        data_by_ename = {d.name: d for d in updated_exml_data.get_all()}

        # Account единсвенный в demo не наследует GameObject
        assert data_by_ename['Account'].hasBase is True
        # Поэтому у Account не прописан hasCell и значит он False, но
        # всё равно он будет выставлен в ручную в False
        assert data_by_ename['Account'].hasCell is False
        # hasClient всем выставляется в ручную в entities.xml
        assert data_by_ename['Account'].hasClient is True

        assert data_by_ename['Avatar'].hasBase is True
        assert data_by_ename['Avatar'].hasCell is True
        assert data_by_ename['Avatar'].hasClient is True

        assert data_by_ename['Monster'].hasBase is True
        assert data_by_ename['Monster'].hasCell is True
        assert data_by_ename['Monster'].hasClient is True

        assert data_by_ename['NPC'].hasBase is True
        assert data_by_ename['NPC'].hasCell is True
        assert data_by_ename['NPC'].hasClient is True

        assert data_by_ename['Gate'].hasBase is True
        assert data_by_ename['Gate'].hasCell is True
        assert data_by_ename['Gate'].hasClient is True

        assert data_by_ename['Spaces'].hasBase is True
        assert data_by_ename['Spaces'].hasCell is True
        assert data_by_ename['Spaces'].hasClient is False

        assert data_by_ename['Space'].hasBase is True
        assert data_by_ename['Space'].hasCell is True
        assert data_by_ename['Space'].hasClient is False

        assert data_by_ename['SpaceDuplicate'].hasBase is True
        assert data_by_ename['SpaceDuplicate'].hasCell is True
        assert data_by_ename['SpaceDuplicate'].hasClient is False

        assert data_by_ename['SpawnPoint'].hasBase is True
        assert data_by_ename['SpawnPoint'].hasCell is True
        assert data_by_ename['SpawnPoint'].hasClient is False

    def test_normalize_entitiesxml(self):
        exml_parser = EntitiesXMLParser(self._entities_xml_path)
        exml_data = exml_parser.parse()
        edef_parser = EntityDefParser(self._entitydef_dir)
        edef_data = {
            ed.name: edef_parser.parse(ed.name) for ed in exml_data.get_all()
        }
        updated_exml_data = utils.normalize_entitiesxml(
            exml_data, edef_data
        )
        self._check(updated_exml_data)

    def test_to_file(self):
        """Проверка записи в файл конфига."""
        exml_parser = EntitiesXMLParser(self._entities_xml_path)
        exml_data = exml_parser.parse()
        edef_parser = EntityDefParser(self._entitydef_dir)
        edef_data = {
            ed.name: edef_parser.parse(ed.name) for ed in exml_data.get_all()
        }
        updated_exml_data = utils.normalize_entitiesxml(exml_data, edef_data)
        tmp_path = Path(tempfile.NamedTemporaryFile().name)
        updated_exml_data.to_file(tmp_path)

        exml_parser = EntitiesXMLParser(tmp_path)
        exml_data = exml_parser.parse()
        self._check(exml_data)
