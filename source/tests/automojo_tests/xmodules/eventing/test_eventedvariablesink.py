import threading
import unittest
from datetime import datetime

from automojo.xmodules.eventing.eventedvariablesink import EventedVariableSink


class SimpleSink(EventedVariableSink):
    def invalidate_subscription(self, scope=None):
        pass

    def renew_subscription(self, scope=None):
        pass

    def trigger_auto_subscribe_from_variable(self, varkey):
        pass


class TestEventedVariableSink(unittest.TestCase):

    def test_sink_initializes_variables(self):
        desc_table = {
            "alpha": {},
            "beta": {},
        }
        sink = SimpleSink(desc_table)
        alpha_var = sink.lookup_event_variable("alpha")
        beta_var = sink.lookup_event_variable("beta")
        self.assertIsNotNone(alpha_var)
        self.assertIsNotNone(beta_var)
        self.assertEqual(alpha_var.name, "alpha")
        self.assertEqual(beta_var.name, "beta")
        self.assertEqual(alpha_var.key, "alpha")
        self.assertEqual(beta_var.key, "beta")

    def test_lookup_event_variable_prefix(self):
        sink = SimpleSink({"evt": {}}, sink_prefix="pre")
        var = sink.lookup_event_variable("evt")
        self.assertIsNotNone(var)
        self.assertEqual(var.key, "pre/evt")
        # lookup with prefix should return same variable
        var2 = sink.lookup_event_variable("evt")
        self.assertIs(var, var2)

    def test_lookup_event_variable_missing(self):
        sink = SimpleSink({"exists": {}})
        self.assertIsNone(sink.lookup_event_variable("missing"))

    def test_initiator_moment_register_and_lookup(self):
        sink = SimpleSink({})
        moment = datetime.now()
        ctx = {"info": 1}
        sink.initiator_moment_register("evt", moment, ctx)
        looked = sink.initiator_moment_lookup("evt")
        self.assertEqual(looked, (moment, ctx))

    def test_update_event_variable_updates_value(self):
        sink = SimpleSink({"v": {}})
        sink.update_event_variable("v", 10)
        var = sink.lookup_event_variable("v")
        self.assertEqual(var.value, 10)

    def test_update_event_variable_with_lock(self):
        sink = SimpleSink({"v": {}})
        for _ in sink.yield_state_lock():
            sink.update_event_variable("v", 5, sink_locked=True)
        var = sink.lookup_event_variable("v")
        self.assertEqual(var.value, 5)

    def test_auto_subscribe_property(self):
        sink = SimpleSink({}, auto_subscribe=True)
        self.assertTrue(sink.auto_subscribe)


if __name__ == "__main__":
    unittest.main()
