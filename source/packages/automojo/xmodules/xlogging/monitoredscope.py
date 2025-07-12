"""
.. module:: scopemonitoring
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module which contains the :class:`MonitoredScope` object which monitors thread entrapment
               withing a specified scope.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Type

from types import TracebackType

import logging
import os
import uuid

from datetime import datetime, timedelta

from automojo.waiting.waitmodel import TimeoutContext

from automojo.xmodules.xformatting import split_and_indent_lines

DEFAULT_MONITORED_SCOPE_NOTIFY_DELAY = timedelta(seconds=60)

logger = logging.getLogger()

class MonitoredScope:
    """
        The :class:`MonitoredScope` object is utilized in order to provide monitoring on threads
        that are entering sections of code that might have a tendency to block and cause disruptions
        in automation processes.  The monitored scope allows for the creation of scopes of code execution
        that can capture contextual information and hand it to a monitor thread that can then log an error
        message if the thread entering the monitored context does not return from the context with a
        specified period of time.

        This solves the problem of reducing log clutter by not having to log at the entry of problematic
        sections of code, but delay the logging until the thread has failed to exit in a timely manner and
        ensure the logging can happen by passing the work off to another thread that is running in a safer
        context.
    """

    ERROR_COMPARISON_TYPE_MESSAGE = "Comparison is only support between two 'MonitoredScope' objects."

    def __init__(self, label, message, timeout_ctx: TimeoutContext, notify_delay: timedelta=DEFAULT_MONITORED_SCOPE_NOTIFY_DELAY):
        """
            Creates a :class:`MonitoredScope` instance.

            :param label: Human readable label for the scope.
            :param message: Message logged if the scope expires.
            :param timeout_ctx: Timeout context controlling expiration.
            :param notify_delay: Delay before notification is triggered.
        """
        self._id = str(uuid.uuid4())
        self._label = label
        self._message = message
        self._timeout_ctx = timeout_ctx
        self._notify_delay = notify_delay

        self._diag_func = None
        self._diag_args = None
        self._diag_kwargs = None

        self._exited = False
        self._triggered = False
        return

    def __enter__(self) -> "MonitoredScope":
        """
            Enters the monitored scope and registers with the monitor.
        """
        global global_scope_monitor

        if global_scope_monitor is None:
            global_scope_monitor = ScopeMonitor()

        self._timeout_ctx.mark_begin()

        global_scope_monitor.register_monitor(self)

        return self

    def __exit__(self, ex_type: Type[BaseException], ex_inst: BaseException, ex_tb: TracebackType) -> bool:
        """
            Exits the monitored scope and marks it as completed.
        """
        self._exited = True

        return False

    def __eq__(self, other: "MonitoredScope"):
        """
            Perform comparison between MonitoredScope(left) == MonitoredScope(right)
        """
        if not isinstance(other, MonitoredScope):
            raise ValueError(self.ERROR_COMPARISON_TYPE_MESSAGE)

        return self._timeout_ctx.end_time == other._timeout_ctx.end_time

    def __ge__(self, other: "MonitoredScope"):
        """
            Perform comparison between MonitoredScope(left) >= MonitoredScope(right)
        """
        if not isinstance(other, MonitoredScope):
            raise ValueError(self.ERROR_COMPARISON_TYPE_MESSAGE)

        return self._timeout_ctx.end_time >= other._timeout_ctx.end_time

    def __gt__(self, other: "MonitoredScope"):
        """
            Perform comparison between MonitoredScope(left) > MonitoredScope(right)
        """
        if not isinstance(other, MonitoredScope):
            raise ValueError(self.ERROR_COMPARISON_TYPE_MESSAGE)

        return self._timeout_ctx.end_time > other._timeout_ctx.end_time

    def __le__(self, other: "MonitoredScope"):
        """
            Perform comparison between MonitoredScope(left) <= MonitoredScope(right)
        """
        if not isinstance(other, MonitoredScope):
            raise ValueError(self.ERROR_COMPARISON_TYPE_MESSAGE)

        return self._timeout_ctx.end_time <= other._timeout_ctx.end_time

    def __lt__(self, other: "MonitoredScope"):
        """
            Perform comparison between MonitoredScope(left) < MonitoredScope(right)
        """
        if not isinstance(other, MonitoredScope):
            raise ValueError(self.ERROR_COMPARISON_TYPE_MESSAGE)

        return self._timeout_ctx.end_time < other._timeout_ctx.end_time

    def __ne__(self, other: "MonitoredScope"):
        """
            Perform comparison between MonitoredScope(left) != MonitoredScope(right)
        """
        if not isinstance(other, MonitoredScope):
            raise ValueError(self.ERROR_COMPARISON_TYPE_MESSAGE)

        return self._timeout_ctx.end_time != other._timeout_ctx.end_time

    @property
    def exited(self):
        """
            Return true if the thread that entered the MonitoredScope has exited.
        """
        return self._exited

    @property
    def expired(self):
        """
            Returns true if the MonitoredScope instance has not been exited by the calling
            thread before it has expired.
        """
        is_expired = False
        now = datetime.now()
        if now > (self._timeout_ctx.end_time + self._notify_delay):
            is_expired = True
        return is_expired

    @property
    def id(self):
        """
            The unique identifier for this MonitoredScope instance.
        """
        return self._id

    @property
    def label(self):
        """
            The human readable label has been assigned to identify this scope.
        """
        return self._label

    @property
    def message(self):
        """
            The message that will be logged if this MonitoredScope is not exited before
            the timemout has expired.
        """
        return self._message

    def set_diagnostic(self, diagnostic_function, *args, **kwargs):
        """
            Sets the diagnostic function and its associated args which will be run if
            the :class:`MonitoredScope` is not exited before it has expired.
        """
        self._diag_func = diagnostic_function
        self._diag_args = args
        self._diag_kwargs = kwargs
        return

    def trigger_notification(self):
        """
            On the first trigger of a notification.  Runs the diagnostic function, logs the label and
            message along with the information collected by the diagnostic function.
        """
        if not self._triggered:
            self._triggered = True
            if self.expired:

                errlines = [
                    "MonitoredScope({}): Timeout waiting for thread to exit monitored scope.".format(self._label),
                    "MESSAGE: {}".format(self._message),

                ]

                if  self._diag_func:
                    errlines.append("DIAGNOSTIC:")

                    diagmsg = self._diag_func(*self._diag_args, **self._diag_kwargs)
                    errlines.extend(split_and_indent_lines(diagmsg, 1))

                errmsg = os.linesep.join(errlines)
                logger.error(errmsg)

        return
