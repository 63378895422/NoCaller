#!/usr/bin/env python3
"""
Test suite for SIP Client call initiation functionality
Tests making calls with custom caller ID and SIP INVITE message handling
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import socket

# Import the SIPClient class
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from SIPClient import SIPClient


class TestSIPClientCall(unittest.TestCase):
    
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
    
    def test_build_invite_basic(self):
        """Test building basic INVITE message without SMS data."""
        # Setup
        self.client.to_uri = "sip:+1987654321@test.sip.example.com"
        
        # Execute
        invite_msg = self.client._build_invite("+1234567890", "+1987654321")
        
        # Verify
        self.assertIn('INVITE sip:+1987654321@test.sip.example.com SIP/2.0', invite_msg)
        self.assertIn('Via: SIP/2.0/UDP example.com;branch=', invite_msg)
        # Note: _build_invite always applies caller ID spoofing, so we get display name
        self.assertIn('From: "+1234567890" <sip:+1234567890@example.com>;tag=', invite_msg)
        self.assertIn('To: <sip:+1987654321@test.sip.example.com>', invite_msg)
        self.assertIn('Call-ID: ', invite_msg)
        self.assertIn('CSeq: ', invite_msg)
        self.assertIn('INVITE', invite_msg)
        self.assertIn('Contact: <sip:testuser@example.com>', invite_msg)
        self.assertIn('Content-Type: application/sdp', invite_msg)
        self.assertIn('Content-Length: 200', invite_msg)
        self.assertIn('Max-Forwards: 70', invite_msg)
        self.assertIn('User-Agent: GhostCaller/NoCaller-SIP/1.0', invite_msg)
        # Should have SDP
        self.assertIn('v=0', invite_msg)
        self.assertIn('m=audio 5004 RTP/AVP 0', invite_msg)
    
    def test_build_invite_with_caller_id_spoofing(self):
        """Test that caller ID spoofing works in From header."""
        # Setup
        self.client.to_uri = "sip:+1987654321@test.sip.example.com"
        
        # Execute
        invite_msg = self.client._build_invite("John Doe", "+1987654321")
        
        # Verify - From should contain the display name
        self.assertIn('From: "John Doe" <sip:+1234567890@example.com>;tag=', invite_msg)
    
    def test_build_invite_with_pdu_data(self):
        """Test building INVITE with custom headers for SMS data."""
        # Setup
        self.client.to_uri = "sip:+1987654321@test.sip.example.com"
        pdu_message = {
            'X-SMS-Sender': '+1234567890',
            'X-SMS-Message': 'Hello World',
            'X-Custom-Header': 'test-value'
        }
        
        # Execute
        invite_msg = self.client._build_invite("+1234567890", "+1987654321", pdu_message)
        
        # Verify - should contain custom headers
        self.assertIn('X-SMS-Sender: +1234567890', invite_msg)
        self.assertIn('X-SMS-Message: Hello World', invite_msg)
        self.assertIn('X-Custom-Header: test-value', invite_msg)
    
    def test_format_for_sip_various_inputs(self):
        """Test phone number formatting for SIP."""
        test_cases = [
            # (input, expected_output)
            ("+15551234567", "+15551234567"),  # Already international
            ("15551234567", "+115551234567"),   # Missing + (treated as US)
            ("5551234567", "+15551234567"),     # 10-digit US number
            ("12345", "+12345"),                 # Short number
            ("+442079460000", "+442079460000"), # UK number
        ]
        
        for input_num, expected in test_cases:
            with self.subTest(input_num=input_num):
                result = self.client._format_for_sip(input_num)
                self.assertEqual(result, expected)
    
    @patch('socket.socket')
    def test_make_call_success(self, mock_socket_class):
        """Test successful call initiation."""
        # Setup mocks
        mock_sock = Mock()
        mock_socket_class.return_value = mock_sock
        mock_sock.connect.return_value = None
        
        # Mock responses: 100 Trying, 180 Ringing, 200 OK
        mock_sock.recvfrom.side_effect = [
            (b'SIP/2.0 100 Trying\r\n\r\n', ('test.sip.example.com', 5060)),
            (b'SIP/2.0 180 Ringing\r\n\r\n', ('test.sip.example.com', 5060)),
            (b'SIP/2.0 200 OK\r\n\r\n', ('test.sip.example.com', 5060))
        ]
        
        # Create fresh client and connect
        client = SIPClient(self.config)
        client.connect()
        
        # Execute
        result = client.make_call("+1234567890", "+1987654321")
        
        # Verify
        self.assertTrue(result)
        # Should have sent INVITE once
        mock_sock.sendto.assert_called_once()
        # Check that the message sent was an INVITE
        call_args = mock_sock.sendto.call_args[0][0]
        self.assertIn(b'INVITE', call_args)
        self.assertIn(b'+1987654321', call_args)
        # Should have received 3 responses
        self.assertEqual(mock_sock.recvfrom.call_count, 3)
    
    @patch('socket.socket')
    def test_make_call_failure(self, mock_socket_class):
        """Test call initiation failure."""
        # Setup mocks
        mock_sock = Mock()
        mock_socket_class.return_value = mock_sock
        mock_sock.connect.return_value = None
        mock_sock.recvfrom.return_value = (
            b'SIP/2.0 486 Busy Here\r\n\r\n', ('test.sip.example.com', 5060)
        )
        
        # Create fresh client and connect
        client = SIPClient(self.config)
        client.connect()
        
        # Execute
        result = client.make_call("+1234567890", "+1987654321")
        
        # Verify
        self.assertFalse(result)
        mock_sock.sendto.assert_called_once()  # Still sent the INVITE
        self.assertEqual(mock_sock.recvfrom.call_count, 1)  # Got one response
    
    @patch('socket.socket')
    def test_make_call_network_error(self, mock_socket_class):
        """Test call initiation with network error."""
        # Setup mocks
        mock_sock = Mock()
        mock_socket_class.return_value = mock_sock
        mock_sock.connect.return_value = None
        mock_sock.sendto.side_effect = socket.error("Network error")
        
        # Create fresh client and connect
        client = SIPClient(self.config)
        client.connect()
        
        # Execute
        result = client.make_call("+1234567890", "+1987654321")
        
        # Verify
        self.assertFalse(result)
    
    def test_make_call_when_not_connected(self):
        """Test make_call when not connected."""
        # Setup disconnected state
        self.client.sock = None
        self.client.connected = False
        
        # Execute
        result = self.client.make_call("+1234567890", "+1987654321")
        
        # Verify
        self.assertFalse(result)
    
    def test_make_call_invalid_inputs(self):
        """Test make_call with invalid inputs."""
        # Setup connected state
        self.client.sock = Mock()
        self.client.connected = True
        
        # Test with None inputs
        result = self.client.make_call(None, "+1987654321")
        self.assertFalse(result)
        
        result = self.client.make_call("+1234567890", None)
        self.assertFalse(result)
        
        # Test with empty strings
        result = self.client.make_call("", "+1987654321")
        self.assertFalse(result)
        
        result = self.client.make_call("+1234567890", "")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()