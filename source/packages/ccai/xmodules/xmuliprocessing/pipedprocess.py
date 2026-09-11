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

import queue
import sys
import threading

from multiprocessing import Process, Queue
from multiprocessing.connection import wait as wait_for_sentinels

from ccai.xmodules.xmuliprocessing.remotestdtee import RemoteStdTee


# How long a parent-side monitor thread blocks on its queue before it checks
# whether the child process has finished.  The monitors self-terminate once
# the child has exited and the queue has been drained, so this is only the
# granularity of that check, not a limit on how long a child may run.
MONITOR_POLL_INTERVAL = 0.1


def write_to_current_stdout(content: str) -> None:
    """
        Writes ``content`` to whatever ``sys.stdout`` is at the moment of the
        call, so output follows any redirection the parent has in place.

        :param content: Text to write.
    """
    sys.stdout.write(content)
    return


def write_to_current_stderr(content: str) -> None:
    """
        Writes ``content`` to whatever ``sys.stderr`` is at the moment of the
        call, so output follows any redirection the parent has in place.

        :param content: Text to write.
    """
    sys.stderr.write(content)
    return


def piped_process_main(entry_point: Callable, stdout_queue: Queue, stderr_queue: Queue, *args, **kwargs):
    """
        Entry point that runs in the child process.  It tees the child's standard
        streams into the queues, runs ``entry_point`` and then hands every byte of
        buffered output to the parent before returning.

        All of the queue traffic, including the close and the join of the queue
        feeder threads, is deliberately completed here inside ``Process.run`` while
        the interpreter is fully alive.  Deferring it to the interpreter's exit-time
        stream flush would start feeder threads after ``multiprocessing`` has already
        run its exit finalizers, which can deadlock the child at shutdown (observed
        on Windows) and leave the parent waiting on ``join`` forever.

        :param entry_point: The callable to run in the child process.
        :param stdout_queue: Queue that carries the child's stdout lines to the parent.
        :param stderr_queue: Queue that carries the child's stderr lines to the parent.
        :param args: Positional arguments for ``entry_point``.
        :param kwargs: Keyword arguments for ``entry_point``.
    """
    orig_stdout = sys.stdout
    orig_stderr = sys.stderr

    stdout_tee = RemoteStdTee(stdout_queue, sys.__stdout__)
    stderr_tee = RemoteStdTee(stderr_queue, sys.__stderr__)

    sys.stdout = stdout_tee
    sys.stderr = stderr_tee
    try:
        entry_point(*args, **kwargs)
    finally:
        # Forward any partial last line, then put the real streams back so the
        # interpreter's exit-time flush never touches the queues again.
        stdout_tee.flush()
        stderr_tee.flush()
        sys.stdout = orig_stdout
        sys.stderr = orig_stderr

        # Deterministically push everything into the pipe and retire the
        # feeder threads while we still can.
        stdout_queue.close()
        stderr_queue.close()
        stdout_queue.join_thread()
        stderr_queue.join_thread()

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

    def join(self, timeout: Optional[float] = None) -> None:
        """
            Waits for the child process to exit and then for the monitor threads
            to finish forwarding its output, so that when this method returns
            with ``exitcode`` set, every line the child wrote has already been
            written to this process's ``sys.stdout`` / ``sys.stderr``.

            :param timeout: Maximum number of seconds to wait.  As with
                            :meth:`multiprocessing.Process.join`, ``None`` waits
                            indefinitely and a timeout is reported through
                            ``exitcode`` remaining ``None`` rather than raised.
        """
        super().join(timeout)

        if self.exitcode is None:
            # The child is still running; the caller asked for a bounded wait.
            return

        # The child has exited and closed its end of the queues, so the monitors
        # are draining what is left and will stop on their own.  Bound the wait
        # so a misbehaving monitor cannot turn a join into a hang.
        if self._stdout_thread is not None:
            self._stdout_thread.join(timeout)
        if self._stderr_thread is not None:
            self._stderr_thread.join(timeout)

        return

    def stdout_monitor(self) -> None:
        """
            Thread routine that forwards stdout content from the child process
            back to the parent process.
        """
        self._forward_until_child_exits(self._stdout_queue, write_to_current_stdout)
        return

    def stderr_monitor(self) -> None:
        """
            Thread routine that forwards stderr content from the child process
            back to the parent process.
        """
        self._forward_until_child_exits(self._stderr_queue, write_to_current_stderr)
        return

    def _child_has_exited(self) -> bool:
        """
            Reports whether the child process has terminated.

            The process ``sentinel`` is used instead of :meth:`is_alive` because
            the sentinel is safe to poll from a thread other than the one that
            joins the process; ``is_alive`` reaps the child on POSIX and racing
            it against ``join`` from another thread is not safe.
        """
        ready = wait_for_sentinels([self.sentinel], timeout=0)
        exited = len(ready) > 0
        return exited

    def _forward_until_child_exits(self, source_queue: Queue, write: Callable[[str], None]) -> None:
        """
            Forwards strings from ``source_queue`` through ``write`` until the
            child has exited and the queue has been drained.

            The child closes and joins its queues before it exits, so once the
            sentinel reports the child gone, the very next empty poll means
            there is nothing more in flight.

            :param source_queue: Queue being fed by the child process.
            :param write: Callable that writes one forwarded string.
        """
        while True:
            try:
                content = source_queue.get(timeout=MONITOR_POLL_INTERVAL)
            except queue.Empty:
                if self._child_has_exited():
                    break
                continue

            write(content)

        return
