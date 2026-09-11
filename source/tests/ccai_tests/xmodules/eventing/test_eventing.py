
import unittest
import threading
import time
from datetime import datetime

from ccai.xmodules.eventing.eventedvariablesink import EventedVariableSink


# Upper bound on any wait for a helper thread; a stuck thread fails the test
# instead of hanging the run.
THREAD_JOIN_TIMEOUT = 5

class SimpleSink(EventedVariableSink):
    def invalidate_subscription(self, scope=None):
        pass
    def renew_subscription(self, scope=None):
        pass
    def trigger_auto_subscribe_from_variable(self, varkey):
        pass

class TestEventing(unittest.TestCase):

    def test_evented_variable_waits(self):
        sink = SimpleSink({'value': {}}, auto_subscribe=False)
        var = sink.lookup_event_variable('value')

        def updater():
            time.sleep(0.1)
            sink.update_event_variable('value', 5)

        t = threading.Thread(target=updater)
        t.start()

        moment = datetime.now()
        value = var.wait_for_update(moment, timeout=2, interval=0.05)
        self.assertEqual(value, 5)
        t.join(timeout=THREAD_JOIN_TIMEOUT)
        self.assertFalse(t.is_alive())

        sink2 = SimpleSink({'value': {}}, auto_subscribe=False)
        var2 = sink2.lookup_event_variable('value')
        def updater2():
            time.sleep(0.1)
            sink2.update_event_variable('value', 7)
        t2 = threading.Thread(target=updater2)
        t2.start()
        val2 = var2.wait_for_value(timeout=2, interval=0.05)
        self.assertEqual(val2, 7)
        t2.join(timeout=THREAD_JOIN_TIMEOUT)
        self.assertFalse(t2.is_alive())

if __name__ == '__main__':
    unittest.main()
