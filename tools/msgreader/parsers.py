"""Парсеры данных сообщения."""

# # TODO: [2025-09-11 10:59 burov_alexey@mail.ru]:
# # Здесь у Client могут плохо отображаться сообщения сущностей. Или нужно в
# # пакете все сообщения иметь


# TODO: [2025-09-11 11:26 burov_alexey@mail.ru]:
# Это нужно делать только если потребуется
    # parser = getattr(
    #     importlib.import_module(
    #         f"enki.msg_parser.{comp_type.name.lower()}_msg_parser"
    #     ),
    #     f"{(msg.name.split('::')[1][0].upper() + msg.name.split('::')[1][1:])}MsgParser",
    #     None,
    # )
    # if parser is None:
    #     logger.error('There is no parser for the "%s" message', msg.name)
    #     _print_end()
    #     return None

    # err_text = (
    #     f'The message "{msg.name}" cannot be parsed (parser={parser.__name__})'
    # )
    # try:
    #     res = parser().parse(msg)
    # except Exception as err:
    #     logger.error(err)
    #     logger.error(err_text)
    #     _print_end()
    #     return None

    # if not res.success:
    #     logger.error(err_text)
    #     _print_end()
    #     return None

    # assert res.result is not None

    # txt_header = f"*** {msg.name} (id = {msg.id}) ***"
    # logger.info(txt_header)
    # logger.info(pprint.pformat(res.result.asdict(), indent=4))
    # _print_end()
    # return None
