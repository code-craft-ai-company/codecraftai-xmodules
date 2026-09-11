"""
    Tests for :class:`ccai.xmodules.xmuliprocessing.pipedprocess.PipedProcess`.

    The child targets are module-level functions so that they are importable by
    name in a child started with the 'spawn' start method (the default on
    Windows and macOS).  Every wait on the child is bounded so that a defect
    surfaces as a failing test rather than a hung test run.
"""

import io
import sys
import unittest

from typing import Any, Callable, Dict, Optional, Tuple

from ccai.xmodules.xmuliprocessing.pipedprocess import PipedProcess


# Generous upper bound for a child that does almost nothing; a spawned child
# has to start a fresh interpreter and import the test package first.
CHILD_JOIN_TIMEOUT = 30


def child_prints_lines() -> None:
    print("child_out")
    print("child_err", file=sys.stderr)
    return


def child_writes_partial_lines() -> None:
    # No newline at all: the content must still reach the parent at exit.
    sys.stdout.write("partial_out")
    sys.stderr.write("partial_err")
    return


def child_echoes_arguments(first: str, second: str, suffix: str = "") -> None:
    print(f"{first}-{second}{suffix}")
    return


def child_exits_with_status() -> None:
    sys.exit(3)


class TestPipedProcess(unittest.TestCase):

    def setUp(self) -> None:
        self._orig_stdout = sys.stdout
        self._orig_stderr = sys.stderr
        self.out_capture = io.StringIO()
        self.err_capture = io.StringIO()
        sys.stdout = self.out_capture
        sys.stderr = self.err_capture
        return

    def tearDown(self) -> None:
        sys.stdout = self._orig_stdout
        sys.stderr = self._orig_stderr
        return

    def _run_child(self, target: Callable, args: Tuple[Any, ...] = (),
                   kwargs: Optional[Dict[str, Any]] = None) -> Optional[int]:
        """
            Runs ``target`` in a :class:`PipedProcess`, waits a bounded time for it
            and returns its exit code.  A child that outlives the timeout is killed
            and reported as a failure instead of hanging the test run.
        """
        proc = PipedProcess(target=target, args=args, kwargs=kwargs)
        proc.start()
        proc.join(timeout=CHILD_JOIN_TIMEOUT)

        exitcode = proc.exitcode
        if exitcode is None:
            proc.kill()
            proc.join(timeout=CHILD_JOIN_TIMEOUT)
            self.fail(f"PipedProcess did not exit within {CHILD_JOIN_TIMEOUT} seconds.")

        return exitcode

    def test_child_stdout_is_forwarded(self) -> None:
        self._run_child(child_prints_lines)
        self.assertIn("child_out", self.out_capture.getvalue())
        return

    def test_child_stderr_is_forwarded(self) -> None:
        self._run_child(child_prints_lines)
        self.assertIn("child_err", self.err_capture.getvalue())
        return

    def test_forwarded_lines_are_tagged_with_child_pid(self) -> None:
        self._run_child(child_prints_lines)
        captured = self.out_capture.getvalue()
        self.assertRegex(captured, r"\[\d+\] child_out")
        return

    def test_partial_stdout_line_is_forwarded_at_exit(self) -> None:
        self._run_child(child_writes_partial_lines)
        self.assertIn("partial_out", self.out_capture.getvalue())
        return

    def test_partial_stderr_line_is_forwarded_at_exit(self) -> None:
        self._run_child(child_writes_partial_lines)
        self.assertIn("partial_err", self.err_capture.getvalue())
        return

    def test_output_is_complete_when_join_returns(self) -> None:
        # No sleep after join: the contract is that join() only returns once
        # the monitors have written everything the child produced.
        self._run_child(child_prints_lines)
        self.assertIn("child_out", self.out_capture.getvalue())
        self.assertIn("child_err", self.err_capture.getvalue())
        return

    def test_exit_code_is_zero_on_success(self) -> None:
        exitcode = self._run_child(child_prints_lines)
        self.assertEqual(exitcode, 0)
        return

    def test_exit_code_reports_child_exit_status(self) -> None:
        exitcode = self._run_child(child_exits_with_status)
        self.assertEqual(exitcode, 3)
        return

    def test_positional_and_keyword_arguments_reach_target(self) -> None:
        self._run_child(child_echoes_arguments, args=("alpha", "beta"), kwargs={"suffix": "!"})
        self.assertIn("alpha-beta!", self.out_capture.getvalue())
        return


if __name__ == '__main__':
    unittest.main()
