"""
.. module:: pipedprocess
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the PipedProcess object.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automaiton Mojo LLC"
__credits__ = []

from typing import Any, Callable, Iterable, Mapping, Optional

import sys
import threading

from multiprocessing import Process, Queue

from automojo.xmodules.xmuliprocessing.remotestdtee import RemoteStdTee


def piped_process_main(entry_point: Callable, stdout_queue: Queue, stderr_queue: Queue, *args):
    sys.stdout = RemoteStdTee(stdout_queue, sys.__stdout__)
    sys.stderr = RemoteStdTee(stderr_queue, sys.__stderr__)
    entry_point(*args)
    return


class PipedProcess(Process):

    def __init__(self, group: None = None, target: Optional[Callable]=None, name: Optional[str]=None, args: Iterable[Any] = (),
                 kwargs: Optional[Mapping[str, Any]] = None, *, daemon: Optional[bool]=None) -> None:
        """
            Creates a :class:`multiprocessing.Process` derivative that captures
            standard out and error streams.

            :param group: Process group.
            :param target: Entry point callable.
            :param name: Name for the process.
            :param args: Positional arguments for ``target``.
            :param kwargs: Keyword arguments for ``target``.
            :param daemon: ``True`` if the process is a daemon.
        """
        
        if kwargs is None:
            kwargs = {}

        self._stdout_queue = Queue()
        self._stderr_queue = Queue()

        self._stdout_thread = threading.Thread(target=self.stdout_monitor, daemon=True)
        self._stdout_thread.start()

        self._stderr_thread = threading.Thread(target=self.stderr_monitor, daemon=True)
        self._stderr_thread.start()

        rmtarget = piped_process_main
        rmargs = target, self._stdout_queue, self._stderr_queue, *args
        super().__init__(group=group, target=rmtarget, name=name, args=rmargs, kwargs=kwargs, daemon=daemon)
        return
    
    def stdout_monitor(self):
        """
            Thread routine that forwards stdout content from the child process
            back to the parent process.
        """
        try:
            while True:
                s = self._stdout_queue.get()
                sys.stdout.write(s)
        except:
            pass

        return
    
    def stderr_monitor(self):
        """
            Thread routine that forwards stderr content from the child process
            back to the parent process.
        """
        try:
            while True:
                s = self._stderr_queue.get()
                sys.stderr.write(s)
        except:
            pass
        
        return
    
