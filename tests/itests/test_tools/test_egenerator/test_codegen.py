import os
from pathlib import Path

import pytest

from tests.itests.app_mocks.loginapp_mock import LoginappMock
from tools.egenerator.codegen import generate_code

GAME_ASSETS_DIR = os.environ.get("GAME_ASSETS_DIR")
GAME_GENERATED_CLIENT_API_DIR = os.environ.get("GAME_GENERATED_CLIENT_API_DIR")
GAME_ACCOUNT_NAME = os.environ.get("GAME_ACCOUNT_NAME")
GAME_PASSWORD = os.environ.get("GAME_PASSWORD")


class TestCodeGen:

    _CURR_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

    @pytest.mark.timeout(5)
    async def test_generate_code(
        self,
        loginapp_fixture: LoginappMock,
        temp_dir_name: str,
        # self,
        # started_kbe_loginapp,
        # temp_dir_name: str,
    ):
        """Генерация кода сущностей и типов для клиентского плагина."""
        assert GAME_ASSETS_DIR is not None
        assert GAME_ASSETS_DIR
        assert Path(GAME_ASSETS_DIR).exists()

        assert GAME_ACCOUNT_NAME
        assert GAME_PASSWORD

        if (
            GAME_GENERATED_CLIENT_API_DIR is None
            or not GAME_GENERATED_CLIENT_API_DIR
        ):
            game_generated_client_api_dir = Path(temp_dir_name)
        else:
            game_generated_client_api_dir = Path(GAME_GENERATED_CLIENT_API_DIR)

        await generate_code(
            game_assets_dir=Path(GAME_ASSETS_DIR),
            login_name=GAME_ACCOUNT_NAME,
            password=GAME_PASSWORD,
            game_generated_client_api_dir=game_generated_client_api_dir,
            # loginapp_addr=started_kbe_loginapp,
            loginapp_addr=loginapp_fixture.tcp_addr,
        )
