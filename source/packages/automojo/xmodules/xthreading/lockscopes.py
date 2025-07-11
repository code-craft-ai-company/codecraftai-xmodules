"""
.. module:: lockscopes
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module that contains the :class:`LockedScope` and :class:`UnLockedScope`
               objects which provide exception safe locking and unlocking patterns.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []



from typing import Union, Type

from types import TracebackType

from threading import Lock, RLock

class LockedScope:
    """
        Context manager that acquires a lock for the scope of a ``with`` block.
    """

    def __init__(self, lock: Union[Lock, RLock]) -> None:
        """
            Initialize the scope manager with the lock to acquire.

            :param lock: Lock instance to manage.
        """
        self._lock = lock
        return
    
    def __enter__(self) -> "LockedScope":
        """
            Acquire the managed lock.
        """
        self._lock.acquire()
        return self

    def __exit__(self, ex_type: Type[BaseException], ex_inst: BaseException, ex_tb: TracebackType) -> bool:
        """
            Release the managed lock.

            :param ex_type: Exception type.
            :param ex_inst: Exception instance.
            :param ex_tb: Traceback information.

            :returns: ``False`` to propagate exceptions.
        """
        self._lock.release()
        return False

class UnLockedScope:
    """
        Context manager that temporarily releases a lock.
    """

    def __init__(self, lock: Union[Lock, RLock]) -> None:
        """
            Initialize with the lock to manage.

            :param lock: Lock instance to release and reacquire.
        """
        self._lock = lock
        return
    
    def __enter__(self) -> "UnLockedScope":
        """
            Release the managed lock.
        """
        self._lock.release()
        return self

    def __exit__(self, ex_type: Type[BaseException], ex_inst: BaseException, ex_tb: TracebackType) -> bool:
        """
            Reacquire the managed lock.

            :param ex_type: Exception type.
            :param ex_inst: Exception instance.
            :param ex_tb: Traceback information.

            :returns: ``False`` to propagate exceptions.
        """
        self._lock.acquire()
        return False

def create_locked_scope(lock: Union[Lock, RLock]) -> LockedScope:
    """
        Convenience function returning a :class:`LockedScope`.

        :param lock: Lock instance to manage.

        :returns: A new :class:`LockedScope`.
    """

    lkscope = LockedScope(lock)

    return lkscope

def create_unlocked_scope(lock: Union[Lock, RLock]) -> UnLockedScope:
    """
        Convenience function returning an :class:`UnLockedScope`.

        :param lock: Lock instance to manage.

        :returns: A new :class:`UnLockedScope`.
    """

    unlkscope = UnLockedScope(lock)

    return unlkscope