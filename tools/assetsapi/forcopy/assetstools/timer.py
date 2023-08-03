import enum


# Descendants of enum.Enum cannot have class attributes.
_last_user_data = [15900]


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


        class TrapperMixin:

            def __init__(self):
                self.addTimer(1, 0, TrapTimerID.CREATE_TRAP)

            def onTimer(self, handler_id: int, timer_id: int) -> bool:
                if timer_id == TrapTimerID.CREATE_TRAP:
                    # create trap ...
                    return True
                elif timer_id == TrapTimerID.DESTROY_TRAP:
                    # destroy trap ...
                    return True
                return False

        class SomeEntity(KBEngine.Entity, TrapperMixin):

            def __init__(self):
                KBEngine.Entity.__init__(self)
                TrapperMixin.__init__(self)
                self.addTimer(1, 0, TrapTimerID.CREATE_TRAP)

            def onTimer(self, handler_id: int, timer_id: int) -> bool:
                if TrapperMixin.onTimer(self, handler_id, timer_id):
                    return True
                # We can using timer id by name. Timer ids are unique in
                # the whole app
                if timer_id == OtherTimerID.START:
                    # Do something.
                    return True
                return False

    """

    def _generate_next_value_(name, start, count, last_values):
        _last_user_data[0] += 1
        return _last_user_data[0]
