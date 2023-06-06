"""For developing purposes.

It should be disabled in production usage."""

import inspect


def func_args_values() -> str:
    """
    Returns arguments of a callee function and its values in
    the format "name = value".

    For debug logging.
    """
    upper_frame_info = inspect.stack()[1]
    upper_function_frame = upper_frame_info[0]
    var_names = upper_function_frame.f_code.co_varnames
    args_values = []
    for arg_name in var_names:
        if arg_name not in upper_function_frame.f_locals:
            continue
        if arg_name in ('self', 'cls'):
            continue
        value = upper_function_frame.f_locals[arg_name]
        args_values.append((arg_name, value))
    return ', '.join('%s = %s' % (arg_name, value) for arg_name, value in args_values)


class LogicError(Exception):
    """Error of a programmer."""
    pass
