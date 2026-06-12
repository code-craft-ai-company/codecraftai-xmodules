"""
.. module:: debugging
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module which contains functions for supporting various debug scenarios and for
               supporting wellknow breakpoints.

.. note:: The modules that are named `xsomething` like this module are prefixed with an `x` character to
          indicate they extend the functionality of a base python module and the `x` is pre-pended to
          prevent module name collisions with python modules.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import List

import inspect
import logging
import threading
import time

from enum import Enum


logger = logging.getLogger(__name__)


DEFAULT_DEBUG_PORT = 5678
PORT_DEBUGPY_ASSISTANT = 5679

class DEBUGGER(str, Enum):
    PDB = 'pdb'
    DEBUGPY = 'debugpy'


def in_vscode_debugger() -> bool:
    """
        Determines whether the current process is running under VSCode's
        debugger.

        :returns: ``True`` if VSCode debugging is active.
    """
    invscode = False
    for frame in inspect.stack():
        if frame[1].endswith("pydevd.py"):
            invscode = True
            break
    return invscode


def debugger_wellknown_breakpoint_entry(debugger: str, breakpoint_name: str, configured_breakpoints: List[str]) -> None:
    """
        Triggers a breakpoint if the named well known breakpoint is enabled
        in the current context.

        :param debugger: The name of the debugger to use when a breakpoint is hit.
        :param breakpoint_name: Key identifying the breakpoint.
        :param configured_breakpoints: A list of breakpoints that have been configured by the user.
    """

    if breakpoint_name in configured_breakpoints:
        if debugger == DEBUGGER.PDB:
            # The debug flag was passed on the commandline so we break here.
            import pdb
            pdb.set_trace()
        elif debugger == DEBUGGER.DEBUGPY:
            logger.info("Waiting for debugger on port={}".format(DEFAULT_DEBUG_PORT))

            invscode = in_vscode_debugger()

            # The remote debug flag was passed on the commandline so we break here.
            import debugpy
            if invscode:
                debugpy.listen(("127.0.0.1", DEFAULT_DEBUG_PORT))
                debugpy.wait_for_client()
            debugpy.breakpoint()

    return


def debugger_wellknown_breakpoint_code_append(debugger: str, breakpoint_name: str, code_lines: list, current_indent: str,
                                              configured_breakpoints: List[str]) -> None:
    """
        Appends source lines that trigger a well known breakpoint when
        enabled in the debug context.

        :param debugger: The name of the debugger to use when a breakpoint is hit.
        :param breakpoint_name: Identifier for the breakpoint.
        :param code_lines: List of lines being emitted.
        :param current_indent: Current indentation prefix for the new lines.
        :param configured_breakpoints: A list of breakpoints that have been configured by the user.
    """

    if breakpoint_name in configured_breakpoints:
        if debugger == DEBUGGER.PDB:
            code_lines.append('')
            code_lines.append('{}# The debug flag was passed on the commandline so we break here.'.format(current_indent))
            code_lines.append('{}import pdb'.format(current_indent))
            code_lines.append('{}pdb.set_trace()'.format(current_indent))
        elif debugger == DEBUGGER.DEBUGPY:
            invscode = in_vscode_debugger()

            code_lines.append('')
            code_lines.append('{}# The remote debug flag was passed on the commandline so we break here.'.format(current_indent))
            code_lines.append('{}import debugpy'.format(current_indent))
            if invscode:
                code_lines.append('{}debugpy.listen(("127.0.0.1", {}))'.format(current_indent, DEFAULT_DEBUG_PORT))
                code_lines.append('{}debugpy.wait_for_client()'.format(current_indent))
            code_lines.append('{}debugpy.breakpoint()'.format(current_indent))

            logger.info("Waiting for debugger on port={}".format(DEFAULT_DEBUG_PORT))

    return


class DebugPyAssistant():
    """
        The DebugPyAssistant is used to setup a daemon thread that creates a remote debug
        endpoint that can optionally connected to in order to remote debug a process running
        in the automation environment.
    """

    def __init__(self, name: str = "DebugPyAssistant",
                 *, endpoint=("127.0.0.1", PORT_DEBUGPY_ASSISTANT)) -> None:
        """
            Starts a daemon thread exposing a ``debugpy`` endpoint.

            :param name: Name for the background thread.
            :param endpoint: ``(host, port)`` tuple to listen on.
        """

        self._endpoint = endpoint
        self._running = True

        self._debug_thread = threading.Thread(
            name=name, target=self._entry_debug_server, daemon=True
        )
        self._debug_thread.start()
        return

    @property
    def endpoint(self):
        """
            Network endpoint for debug connections.
        """
        return self._endpoint

    @property
    def thread(self):
        """
            Background thread serving the debug endpoint.
        """
        return self._debug_thread

    def _entry_debug_server(self):
        """
            Thread routine that waits for debugger clients and breaks on
            each connection.
        """

        import debugpy
        debugpy.listen(self._endpoint)

        while self._running:

            debugpy.wait_for_client()

            # While we are connected to the debugger, have the debug assistant
            # thread loop
            while debugpy.is_client_connected():
                time.sleep(2)

        return