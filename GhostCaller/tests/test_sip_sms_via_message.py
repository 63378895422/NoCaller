#!/usr/bin/env python3
"""
Test suite for SIP Client SMS sending via SIP MESSAGE method
Tests sending SMS using SIP MESSAGE method
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add the parent directory to sys.path so we can import SIPClient
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SIPClient import SIPClient


class TestSIPClientSMSViaMessage(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = {
            'sip_server': 'test.sip.example.com',
            'sip_port': 5060,
            'username': 'testuser',
            'password': 'testpass',
            'domain': 'example.com',
            'use_tls': False,
            'transport': 'UDP'
        }
        self.client = SIPClient(self.config)
        # Mock the socket connection
        self.client.sock = Mock()
        self.client.connected = True
    
    def test_format_phone_number_for_sip(self):
        """Test _format_for_sip method with various inputs."""
        test_cases = [
            ("+15551234567", "+15551234567"),
            ("15551234567", "+115551234567"),
            ("5551234567", "+15551234567"),
            ("12345", "+12345"),
        ]
        
        for input_num, expected in test_cases:
            with self.subTest(input_num=input_num):
                result = self.client._format_for_sip(input_num)
                self.assertEqual(result, expected)
    
    @patch('socket.socket')
    def test_send_sip_message_success(self, mock_socket_class):
        """Test successful SMS sending via SIP MESSAGE."""
        # Setup mocks
        mock_sock = Mock()
        mock_socket_class.return_value = mock_sock
        mock_sock.connect.return_value = None
        mock_sock.recvfrom.return_value = (
            b'SIP/2.0 200 OK\r\n\r\n',
            ('test.sip.example.com', 5060)
        )
        
        # Create fresh client and connect
        client = SIPClient(self.config)
        client.connect()
        
        # Execute
        result = client._send_sip_message("+1234567890", "+1987654321", "Test message")
        
        # Verify
        self.assertTrue(result)
        mock_sock.sendto.assert_called_once()
        # Check that the message sent was a MESSAGE
        call_args = mock_sock.sendto.call_args[0][0]
        self.assertIn(b'MESSAGE', call_args)
        self.assertIn(b'+1987654321', call_args)
        mock_sock.recvfrom.assert_called_once()
    
    @patch('socket.socket')
    def test_send_sip_message_failure(self, mock_socket_class):
        """Test SIP MESSAGE sending failure."""
        # Setup mocks
        mock_sock = Mock()
        mock_socket_class.return_value = mock_sock
        mock_sock.connect.return_value = None
        mock_sock.recvfrom.return_value = (
            b'SIP/2.0 403 Forbidden\r\n\r\n',
            ('test.sip.example.com', 5060)
        )
        
        # Create fresh client and connect
        client = SIPClient(self.config)
        client.connect()
        
        # Execute
        result = client._send_sip_message("+1234567890", "+1987654321", "Test message")
        
        # Verify
        self.assertFalse(result)
        mock_sock.sendto.assert_called_once()
        mock_sock.recvfrom.assert_called_once()
    
    @patch('socket.socket')
    def test_send_sip_message_network_error(self, mock_socket_class):
        """Test SIP MESSAGE sending with network error."""
        # Setup mocks
        mock_sock = Mock()
        mock_socket_class.return_value = mock_sock
        mock_sock.connect.return_value = None
        mock_sock.sendto.side_effect = ConnectionError("Network error")
        
        # Create fresh client and connect
        client = SIPClient(self.config)
        client.connect()
        
        # Execute
        result = client._send_sip_message("+1234567890", "+1987654321", "Test message")
        
        # Verify
        self.assertFalse(result)
    
    def test_send_sip_message_when_not_connected(self):
        """Test _send_sip_message when not connected."""
        # Setup disconnected state
        self.client.sock = None
        self.client.connected = False
        
        # Execute
        result = self.client._send_sip_message("+1234567890", "+1987654321", "Test message")
        
        # Verify
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()