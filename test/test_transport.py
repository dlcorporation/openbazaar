import json
import unittest

import mock

from node import protocol, transport


class TestTransportLayerCallbacks(unittest.TestCase):
    """Test the callback features of the TransportLayer class."""

    def setUp(self):
        self.callback1 = mock.Mock()
        self.callback2 = mock.Mock()
        self.callback3 = mock.Mock()

        self.tl = transport.TransportLayer(1, 'localhost', None, 1)
        self.tl.add_callback('section_one', self.callback1)
        self.tl.add_callback('section_one', self.callback2)
        self.tl.add_callback('all', self.callback3)

    def _assert_called(self, one, two, three):
        self.assertEqual(self.callback1.call_count, one)
        self.assertEqual(self.callback2.call_count, two)
        self.assertEqual(self.callback3.call_count, three)

    def test_fixture(self):
        self._assert_called(0, 0, 0)

    def test_callbacks(self):
        self.tl.trigger_callbacks('section_one', None)
        self._assert_called(1, 1, 1)

    def test_all_callback(self):
        self.tl.trigger_callbacks('section_with_no_register', None)
        self._assert_called(0, 0, 1)

    def test_explicit_all_section(self):
        self.tl.trigger_callbacks('all', None)
        self._assert_called(0, 0, 1)


class TestTransportLayerMessageHandling(unittest.TestCase):

    def setUp(self):
        self.tl = transport.TransportLayer(1, 'localhost', None, 1)

    def test_on_message_ok(self):
        """OK message should trigger no callbacks."""
        self.tl.trigger_callbacks = mock.MagicMock(
            side_effect=AssertionError()
        )
        self.tl._on_message(protocol.ok())

    def test_on_message_not_ok(self):
        """
        Any non-OK message should cause trigger_callbacks to be called with
        the type of message and the message object (dict).
        """
        data = protocol.shout({})
        self.tl.trigger_callbacks = mock.MagicMock()
        self.tl._on_message(data)
        self.tl.trigger_callbacks.assert_called_with(data['type'], data)

    def test_on_raw_message_invalid(self):
        """Invalid serialized messages should be dropped."""
        self.tl._init_peer = mock.MagicMock()
        self.tl._on_message = mock.MagicMock()
        self.tl._on_raw_message('invalid serialization')
        self.assertFalse(self.tl._init_peer.called)
        self.assertFalse(self.tl._on_message.called)

    def test_on_raw_message_hello_no_uri(self):
        """A hello message with no uri should not add a peer."""
        self.tl._on_raw_message([json.dumps(protocol.hello_request({}))])
        self.assertEqual(0, len(self.tl.peers))

    def test_on_raw_message_hello_with_uri(self):
        """A hello message with a uri should result in a new peer."""
        request = protocol.hello_request({
            'uri': 'tcp://localhost:12345'
        })
        self.tl._on_raw_message([json.dumps(request)])
        self.assertEqual(1, len(self.tl.peers))


class TestTransportLayerProfile(unittest.TestCase):

    def test_get_profile(self):
        tl = transport.TransportLayer(1, '1.1.1.1', 12345, 1)
        self.assertEqual(
            tl.get_profile(),
            protocol.hello_request({
                'uri': 'tcp://1.1.1.1:12345'
            })
        )

if __name__ == "__main__":
    unittest.main()
