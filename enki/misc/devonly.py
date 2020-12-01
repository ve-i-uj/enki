"""Функционал на время разработки.

@author: Aleksei Burov (burov_alexey@mail.ru) / ve_i_uj
"""

import inspect


def func_args_values() -> str:
    """
    Возвращает имена аргументов вызывающей функции и их значения
    в формате `имя = значение`.
    
    Чтобы при отладке при логировании функции не прописывать все
    аргументы руками.
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
