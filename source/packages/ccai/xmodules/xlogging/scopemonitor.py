"""
.. module:: scopemonitor
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module which contains the :class:`ScopeMonitor` object which monitors watches :class:`MonitoredScope`
               objects to make sure they have not expired.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

from typing import List

import logging
import threading

from datetime import timedelta

from ccai.xmodules.xcollections.helpers import insert_into_ordered_list_ascending

from ccai.xmodules.xlogging.monitoredscope import MonitoredScope


DEFAULT_MONITORED_SCOPE_NOTIFY_DELAY = timedelta(seconds=60)


logger = logging.getLogger(__name__)


class ScopeMonitor:
    """
        The :class:`ScopeMonitor` object is utilized to provide monitoring of threads that are entering
        sections of code that might have a tendency to block and cause disruptions in automation processes.

        The :class:`MonitoredScope` takes pre-dictive work packets for logging from threads entering critical
        sections of code monitored by :class:`MonitoredScope` instances used in a 'with' statement.

        ..code-block:: python

            with MonitoredScope("RunCommand", "Running command on cluster node (%s)" % nodeip) as mscope:
                cluster.run_cmd(1, "echo blah")

        The use of a :class:`MonitoredScope` remove the necessity to log prior to entering a critical
        section of code but allows log entrys to be pre-emptively handed off to the :class:`ScopeMonitor`
        thread for contingent processing should a the thread fail to return from the critical section of
        code in a timely manner.
    """

    SCOPE_MONITOR_INTERVAL = 5

    instance = None
    initialized = False

    def __new__(cls, *_args, **_kwargs):
        """
            Constructs new instances of the :class:`MonitoredScope` object. The
            :class:`MonitoredScope` object is a singleton so following instantiations
            of the object will reference the existing singleton
        """

        if cls.instance is None:
            cls.instance = super(ScopeMonitor, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        """
            Initializes the singleton scope monitor.
        """
        thisType = type(self)
        if not thisType.initialized:
            thisType.initialized = True

            self._monitors: List[MonitoredScope] = []
            self._monitors_lock = threading.RLock()

            self._timer = None
            self._active = False
        return

    def register_monitor(self, monitor: MonitoredScope):
        """
            Register a monitor context with the :class:`MonitoredScope` singleton.

            :param monitor: The monitor context to add to the the list of monitored scopes.
        """

        self._monitors_lock.acquire()
        try:
            insert_into_ordered_list_ascending(self._monitors, monitor)

            if not self._active:
                self._timer = threading.Timer(self.SCOPE_MONITOR_INTERVAL, self._monitor_tick)
                self._timer.start()
                self._active = True
        finally:
            self._monitors_lock.release()

        return

    def _monitor_tick(self):
        """
            Timer callback used to check for expired scopes.
        """
        self._monitors_lock.acquire()
        try:
            if len(self._monitors) > 0:
                while True:
                    firstMonitor = self._monitors[0]
                    if firstMonitor.expired:
                        firstMonitor.trigger_notification()
                        del self._monitors[0]

                        if len(self._monitors) == 0:
                            self._timer.cancel()
                            del self._timer

                            self._active = False

                    else:
                        break
        finally:
            self._monitors_lock.release()

        return


global_scope_monitor = None
