# TODO: [16.07.2021 burov_alexey@mail.ru]:
# Нужно общее остановочное исключение для всего клиента KBEngine

class StopClientException(Exception):
    """Signal to stop the client."""
    pass
