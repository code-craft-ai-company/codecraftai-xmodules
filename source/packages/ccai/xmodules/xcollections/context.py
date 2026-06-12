"""
.. module:: context
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module that contains the :class:`Context` object — a thread-safe,
               path-addressable global context and configuration map.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, Iterable, Optional, Union

from threading import RLock

from ccai.xmodules.xcollections.dictmap import DictMap


class Context:
    """
        A path-addressable context and configuration map.

        :class:`Context` wraps a :class:`DictMap` so values can be stored and
        retrieved using ``/`` separated paths (for example ``/database/host``),
        and serializes access through an :class:`RLock` so it is safe to share a
        single instance (see :func:`ContextSingleton`) across threads.
    """

    def __init__(self, store: Optional[Dict[str, Any]] = None) -> None:
        """
            Initializes a :class:`Context` instance.

            :param store: Optional backing dictionary; a new empty dict is used
                when not provided.
        """
        if store is None:
            store = {}

        self._store = store
        self._map = DictMap(self._store)
        self._lock = RLock()
        return

    @property
    def store(self) -> Dict[str, Any]:
        """
            The underlying backing dictionary for this context.

            :returns: The backing dictionary.
        """
        return self._store

    def exists(self, path: str) -> bool:
        """
            Indicates whether a value exists at the specified path.

            :param path: The ``/`` separated path to check.

            :returns: ``True`` if a value exists at the path.
        """
        self._lock.acquire()
        try:
            rtnval = self._map.exists(path)
        finally:
            self._lock.release()

        return rtnval

    def lookup(self, path: Union[str, Iterable[str]], default: Optional[Any] = None, raise_error: bool = True) -> Any:
        """
            Looks up the value stored at the specified path.

            :param path: The ``/`` separated path to look up.
            :param default: Value returned when the path is absent and
                ``raise_error`` is ``False``.
            :param raise_error: When ``True``, raise :class:`LookupError` for a
                missing path; otherwise return ``default``.

            :returns: The value stored at the path (or ``default``).
            :raises: LookupError
        """
        self._lock.acquire()
        try:
            rtnval = self._map.lookup(path, default=default, raise_error=raise_error)
        finally:
            self._lock.release()

        return rtnval

    def insert(self, path: str, obj: Any) -> None:
        """
            Inserts a value at the specified path.

            :param path: The ``/`` separated path to insert at.
            :param obj: The value to store.
        """
        self._lock.acquire()
        try:
            self._map.insert(path, obj)
        finally:
            self._lock.release()

        return

    def remove(self, path: str) -> Any:
        """
            Removes and returns the value at the specified path.

            :param path: The ``/`` separated path to remove.

            :returns: The removed value.
            :raises: LookupError
        """
        self._lock.acquire()
        try:
            rtnval = self._map.remove(path)
        finally:
            self._lock.release()

        return rtnval
