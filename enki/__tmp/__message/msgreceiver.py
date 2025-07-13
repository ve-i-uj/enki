class _DefaultMsgReceiver(IClientMsgReceiver):
    """Message receiver using by default after initialization of the client."""

    def on_receive_msg(self, msg: Message):
        logger.debug(f"[{self}] ({devonly.func_args_values()})")  # noqa: G004

    def on_end_receive_msg(self):
        logger.debug(f"[{self}] ({devonly.func_args_values()})")  # noqa: G004
