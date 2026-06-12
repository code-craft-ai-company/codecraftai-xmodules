"""
.. module:: pipedprocess
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the PipedProcess object.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

from typing import Any, Callable, Iterable, Mapping, Optional

import sys
import threading

from multiprocessing import Process, Queue

from ccai.xmodules.xmuliprocessing.remotestdtee import RemoteStdTee


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

        # Queues are designed for inter-process use and pickle/share correctly,
        # so they may live on the instance and be passed to the child.
        self._stdout_queue = Queue()
        self._stderr_queue = Queue()

        # The parent-side monitor threads are NOT created here: multiprocessing
        # 'spawn' (the default on macOS/Windows) pickles the Process instance to
        # start the child, and live Thread objects are unpicklable ("cannot
        # pickle '_thread.lock' object"). They are started in start(), after the
        # child has been spawned. See start().
        self._stdout_thread = None
        self._stderr_thread = None

        rmtarget = piped_process_main
        rmargs = target, self._stdout_queue, self._stderr_queue, *args
        super().__init__(group=group, target=rmtarget, name=name, args=rmargs, kwargs=kwargs, daemon=daemon)
        return

    def start(self) -> None:
        """
            Spawns the child process and then starts the parent-side monitor
            threads that forward the child's stdout/stderr back to this process.

            The monitor threads are started after ``super().start()`` so the
            (unpicklable) Thread objects are never part of the instance state
            that ``multiprocessing`` pickles to spawn the child.
        """
        super().start()

        self._stdout_thread = threading.Thread(target=self.stdout_monitor, daemon=True)
        self._stdout_thread.start()

        self._stderr_thread = threading.Thread(target=self.stderr_monitor, daemon=True)
        self._stderr_thread.start()

        return

    def stdout_monitor(self) -> None:
        """
            Thread routine that forwards stdout content from the child process
            back to the parent process.
        """
        try:
            while True:
                s = self._stdout_queue.get()
                sys.stdout.write(s)
        except Exception:
            # The queue is closed / the child has exited; stop forwarding.
            pass

        return

    def stderr_monitor(self) -> None:
        """
            Thread routine that forwards stderr content from the child process
            back to the parent process.
        """
        try:
            while True:
                s = self._stderr_queue.get()
                sys.stderr.write(s)
        except Exception:
            # The queue is closed / the child has exited; stop forwarding.
            pass

        return
    
