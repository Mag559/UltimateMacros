from threading import Lock


class SingletonMeta(type):
    """
    Metaclass for singletons,
    features a lock, which is a little extra considering most of the thread safety hinges on the interpreter lock
    """
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
