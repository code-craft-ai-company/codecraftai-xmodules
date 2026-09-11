"""
.. module:: remotestdtee
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the RemoteStdTee object.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import TextIO

import os

from multiprocessing import Queue

from io import StringIO


# Python text streams always carry '\n' as the line terminator; the platform
# 'os.linesep' ('\r\n' on Windows) is only ever produced by the underlying
# binary layer of a real file.  A tee that sits in front of the text layer
# must therefore split on '\n', otherwise on Windows no line is ever
# recognised and every write is held back until the exit-time flush.
LINE_TERMINATOR = "\n"


class RemoteStdTee(StringIO):
    def __init__(self, queue: Queue, orig_file: TextIO):
        """
            Creates an instance of :class:`RemoteStdTee` used to capture output
            for forwarding to the owning process.

            :param queue: Queue used to forward output strings.
            :param orig_file: Original file object being replaced.
        """
        super().__init__()
        self._pid = os.getpid()
        self._queue = queue
        self._orig_file = orig_file
        return

    def flush(self):
        """
            Flushes the internal buffer and forwards any buffered content to the
            remote queue before flushing the underlying file handle.
        """
        buffer = self.getvalue()
        if len(buffer) > 0:
            self._queue.put(f"[{self._pid}] {buffer}{os.linesep}")
        self.seek(0)
        self.truncate()
        return self._orig_file.flush()

    def write(self, s: str):
        """
            Writes string content to the tee buffer and forwards complete lines
            to the remote queue.

            :param s: Text to write.
        """
        nlidx = s.find(LINE_TERMINATOR)
        if nlidx < 0:
            StringIO.write(self, s)
        else:
            nlidx = s.rindex(LINE_TERMINATOR)
            rems = s[nlidx + 1:]
            qmsg = self.getvalue() + s[:nlidx]
            self.seek(0)
            self.truncate()
            if len(rems) > 0:
                StringIO.write(self, rems)
            self._queue.put(f"[{self._pid}] {qmsg}{os.linesep}")
        return self._orig_file.write(s)
