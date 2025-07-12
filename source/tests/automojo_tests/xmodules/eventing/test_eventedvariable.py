import unittest
import weakref
import time
from datetime import datetime, timedelta

from automojo.xmodules.eventing.eventedvariable import EventedVariable
from automojo.xmodules.eventing.eventedvariablesink import EventedVariableSink
from automojo.xmodules.eventing.enumerations import EventedVariableState


class SimpleSink(EventedVariableSink):
    def invalidate_subscription(self, scope=None):
        pass

    def renew_subscription(self, scope=None):
        pass

    def trigger_auto_subscribe_from_variable(self, varkey):
        pass


class TestEventedVariable(unittest.TestCase):

    def _create_sink_and_var(self, desc=None):
        if desc is None:
            desc = {}
        sink = SimpleSink({'value': desc}, auto_subscribe=False)
        var = sink.lookup_event_variable('value')
        return sink, var

    def test_constructor_sets_default_value(self):
        _, var = self._create_sink_and_var({'default': 7})
        self.assertEqual(var.value, 7)
        self.assertIsNone(var.created)
        self.assertIsNone(var.updated)
        self.assertIsNone(var.changed)

    def test_constructor_raises_for_non_evented(self):
        sink, _ = self._create_sink_and_var()
        with self.assertRaises(ValueError):
            EventedVariable('value', 'value', weakref.ref(sink), evented=False)

    def test_expired_property_behavior(self):
        _, var = self._create_sink_and_var()
        self.assertTrue(var.expired)
        future = datetime.now() + timedelta(seconds=5)
        var.sync_update(1, expires=future)
        self.assertFalse(var.expired)
        var._expires = datetime.now() - timedelta(seconds=1)
        self.assertTrue(var.expired)

    def test_sync_update_updates_timestamps(self):
        _, var = self._create_sink_and_var()
        var.sync_update(1)
        first_updated = var.updated
        first_changed = var.changed
        self.assertIsNotNone(first_updated)
        self.assertEqual(first_updated, first_changed)
        time.sleep(0.01)
        var.sync_update(1)
        self.assertGreater(var.updated, first_updated)
        self.assertEqual(var.changed, first_changed)

    def test_sync_read_returns_current_state(self):
        _, var = self._create_sink_and_var()
        var.sync_update('val')
        value, updated, changed, state = var.sync_read()
        self.assertEqual(value, 'val')
        self.assertEqual(updated, changed)
        self.assertEqual(state, EventedVariableState.Valid)

    def test_last_initiator_moment_lookup(self):
        sink, var = self._create_sink_and_var()
        moment = datetime.now()
        sink.initiator_moment_register('value', moment, context='ctx')
        self.assertEqual(var.last_initiator_moment, (moment, 'ctx'))

    def test_wait_for_update_timeout(self):
        _, var = self._create_sink_and_var()
        moment = datetime.now()
        with self.assertRaises(TimeoutError):
            var.wait_for_update(moment, timeout=0.1, interval=0.05)

    def test_wait_for_value_timeout(self):
        _, var = self._create_sink_and_var()
        with self.assertRaises(TimeoutError):
            var.wait_for_value(timeout=0.1, interval=0.05)

    def test_str_representation_includes_state(self):
        _, var = self._create_sink_and_var()
        var.sync_update(42)
        text = str(var)
        self.assertIn('name=value', text)
        self.assertIn('value=42', text)
        self.assertIn('state=Valid', text)


if __name__ == '__main__':
    unittest.main()
