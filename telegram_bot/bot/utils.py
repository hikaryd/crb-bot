from typing import override


class Singleton(type):
    _instances: dict["Singleton", object] = {}

    @override
    def __call__(cls: "Singleton", *args: object, **kwargs: object):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
