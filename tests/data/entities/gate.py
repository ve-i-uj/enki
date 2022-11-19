"""The game logic of the "Gate" entity."""

from enki.app.appl import App

from tests.data import demo_descr


class Gate(demo_descr.gameentity.GateBase):

    def __init__(self, entity_id, is_player: bool, app: App):
        super().__init__(entity_id, is_player, app)
