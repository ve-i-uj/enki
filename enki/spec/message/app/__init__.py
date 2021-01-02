"""Predefined messages of kbe Apps (LoginApp, BaseApp etc.)."""


from . import client, loginapp, baseapp
from . import _client, _loginapp, _baseapp


def _add_initial_msges():
    """Add initial messages to request all them from server and generate them."""
    for src, dst in ((_client, client),
                     (_loginapp, loginapp),
                     (_baseapp, baseapp)):
        for attr_name in dir(src):
            attr = getattr(src, attr_name)
            setattr(dst, attr_name, attr)

    if not hasattr(client, 'SPEC_BY_ID'):
        # Blank start. There is no server messages yet.
        client.SPEC_BY_ID = _client.SPEC_BY_ID
    else:
        client.SPEC_BY_ID.update()


_add_initial_msges()
