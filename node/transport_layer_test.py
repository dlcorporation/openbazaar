import json
import unittest

import mock

from p2p import TransportLayer
import protocol

# Test the callback features of the TransportLayer class
class TestTransportLayerCallbacks(unittest.TestCase):
    one_called = False
    two_called = False
    three_called = False

    def _callback_one(self, arg):
        self.assertFalse(self.one_called)
        self.one_called = True

    def _callback_two(self, arg):
        self.assertFalse(self.two_called)
        self.two_called = True

    def _callback_three(self, arg):
        self.assertFalse(self.three_called)
        self.three_called = True

    def setUp(self):
        self.tl = TransportLayer(1, 'localhost', None, 1)
        self.tl.add_callback('section_one', self._callback_one)
        self.tl.add_callback('section_one', self._callback_two)
        self.tl.add_callback('all', self._callback_three)

    def _assert_called(self, one, two, three):
        self.assertEqual(self.one_called, one)
        self.assertEqual(self.two_called, two)
        self.assertEqual(self.three_called, three)

    def test_fixture(self):
        self._assert_called(False, False, False)

    def test_callbacks(self):
        self.tl.trigger_callbacks('section_one', None)
        self._assert_called(True, True, True)

    def test_all_callback(self):
        self.tl.trigger_callbacks('section_with_no_register', None)
        self._assert_called(False, False, True)

    def test_explicit_all_section(self):
        self.tl.trigger_callbacks('all', None)
        self._assert_called(False, False, True)

class TestTransportLayerMessageHandling(unittest.TestCase):
    def setUp(self):
        self.tl = TransportLayer(1, 'localhost', None, 1)

    # The ok message should not trigger any callbacks
    def test_on_message_ok(self):
        self.tl.trigger_callbacks = mock.MagicMock(side_effect=AssertionError())
        self.tl._on_message(protocol.ok())

    # Any non-ok message should cause trigger_callbacks to be called with
    # the type of message and the message object (dict)
    def test_on_message_not_ok(self):
        data = protocol.shout({})
        self.tl.trigger_callbacks = mock.MagicMock()
        self.tl._on_message(data)
        self.tl.trigger_callbacks.assert_called_with(data['type'], data)

    # Invalid serialized messages should be dropped
    def test_on_raw_message_invalid(self):
        self.tl._init_peer = mock.MagicMock()
        self.tl._on_message = mock.MagicMock()
        self.tl._on_raw_message('invalid serialization')
        self.assertFalse(self.tl._init_peer.called)
        self.assertFalse(self.tl._on_message.called)

    # A hello message with no uri should not add a peer
    def test_on_raw_message_hello_no_uri(self):
        self.tl._on_raw_message([json.dumps(protocol.hello_request({}))])
        self.assertEqual(0, len(self.tl._peers))

    # A hello message with a uri should result in a new peer
    def test_on_raw_message_hello_with_uri(self):
        request = protocol.hello_request({ 'uri': 'tcp://localhost:12345' })
        self.tl._on_raw_message([json.dumps(request)])
        self.assertEqual(1, len(self.tl._peers))

class TestTransportLayerProfile(unittest.TestCase):
    def test_get_profile(self):
        tl = TransportLayer(1, '1.1.1.1', 12345, 1)
        self.assertEqual(tl.get_profile(),
                protocol.hello_request({ 'uri': 'tcp://1.1.1.1:12345' }))
