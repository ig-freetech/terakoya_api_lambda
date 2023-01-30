from typing import cast, Any


class classproperty (property):
    """Subclass property to make classmethod properties possible"""

    def __get__(self, _, owner):
        return cast(Any, self.fget).__get__(None, owner)()
