class ThreadedGameLayer(IGameLayer):
    """Игровой слой вызывает колбэки в другом треде."""

    def __init__(self, app: App) -> None:
        self._entities: dict[int, GameEntity] = {}
        self._app = app

    def get_entities(self) -> dict[int, IKBEClientGameEntity]:
        return {i: e for i, e in self._entities.items()}

    def call_entity_created(self, entity_id: int, entity_cls_name: str, is_player: bool):
        self.on_call_entity_created(entity_id, entity_cls_name, is_player)

    def on_call_entity_created(self, entity_id: int, entity_cls_name: str, is_player: bool):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        e_cls = self._app.get_entity_game_cls_by_cls_name(entity_cls_name)
        entity = e_cls(entity_id, is_player: bool, app: App)
