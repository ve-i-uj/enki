"""The game logic of the "Monster" entity."""

from enki.app.appl import App

from tests.data import descr


class Monster(descr.gameentity.MonsterBase):

    def __init__(self, entity_id, is_player: bool, app: App):
        super().__init__(entity_id, is_player, app)