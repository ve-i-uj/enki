import logging
import enum
from typing import Any, Dict

from . import devonly

logger = logging.getLogger(__name__)

# Descendants of enum.Enum cannot have class attributes.
_last_user_data = [15900]
_timer_type_cache: Dict[int, Any] = {}


class TimerID(enum.IntEnum):
    """Parent class for all timer identifiers used in KBEngine.addTimer.

    It guarantees unique id for all timer callbacks in the app process.
    Descendant classes can define its timers just using `enum.auto()` .

    Example:

        class TrapTimerID(TimerID):
            CREATE_TRAP = enum.auto()
            DESTROY_TRAP = enum.auto()

        class OtherTimerID(TimerID):
            START = enum.auto()

        class SomeEntity(KBEngine.Entity):

            def __init__(self):
                KBEngine.Entity.__init__(self)
                self.addTimer(1, 0, TrapTimerID.CREATE_TRAP)

            def onTimer(self, handler_id: int, timer_id: int) -> bool:
                # We can using timer id by name. Timer ids are unique in the whole app
                if timer_id == TrapTimerID.CREATE_TRAP:
                    # create trap ...
                    return True
                elif timer_id == TrapTimerID.DESTROY_TRAP:
                    # destroy trap ...
                    return True
                if timer_id == OtherTimerID.START:
                    # Do something.
                    return True
                return False

    """

    def _generate_next_value_(name, start, count, last_values) -> int:
        _last_user_data[0] += 1
        return _last_user_data[0]

    @classmethod
    def identifier_by_id(cls, timerID: int):
        """Get the field of a particular enum by value.

        This is a debugging method so that the logs show what type
        timer has worked. In production, this method should NOT be called,
        because most likely it will be quite expensive with a large
        number of enums.

        ATTENTION! Empirically, it was found out that if you use cls(timerID) can
        leak memory. Cause this to me could not be determined. This is probably
        due to the fact that Enum.__call__ served via metaclass and something
        happens to python built into the engine. Therefore, I redefine this
        method and made the collection of fields through a function in a module.
        The leak is gone.
        """
        logger.debug('[%s] %s', cls.__name__, devonly.func_args_values())
        identifier = _timer_type_cache.get(timerID, None)
        if identifier is None:
            _fill_timer_type_cache()
        return _timer_type_cache.get(timerID, None)


def _fill_timer_type_cache():
    # ищем во всех дочерних классах TimerType
    for subcls in TimerID.__subclasses__():
        for field in subcls.__members__.values():
            _timer_type_cache[field.value] = field
