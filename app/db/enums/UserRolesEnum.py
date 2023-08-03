from enum import Enum


class UserRolesEnum(Enum):
    USER = 0, "user"
    MODERATOR = 1, "moderator"
    ADMIN = 2, "admin"

    def __init__(self, value, status):
        self._value = value
        self._status = status

    @classmethod
    def get(cls, value, default=None):
        for item in cls:
            if item.value[1] == value:
                return item
        return default

    def __gt__(self, other):
        return self._value > other

    def __lt__(self, other):
        return self._value < other

    def __le__(self, other):
        return self._value <= other

    def __ge__(self, other):
        return self._value >= other

    def __eq__(self, other):
        return self._value == other

    def __ne__(self, other):
        return self._value != other
