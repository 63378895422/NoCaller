#!/usr/bin/env python3
"""
Test suite for SIP Client registration functionality
Tests SIP registration with and without authentication
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import socket

# Import the SIPClient class
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from SIPClient import SIPClient


class TestSIPClientRegistration(unittest.TestCase):
    
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
    
    def test_build_register_without_auth(self):
        """Test building REGISTER message without authentication."""
        # Execute
        register_msg = self.client._build_register(auth=False)
        
        # Verify
        self.assertIn('REGISTER sip:test.sip.example.com SIP/2.0', register_msg)
        self.assertIn('Via: SIP/2.0/UDP example.com;branch=', register_msg)
        self.assertIn('From: <sip:testuser@example.com>;tag=', register_msg)
        self.assertIn('To: <sip:testuser@example.com>', register_msg)
        self.assertIn('Call-ID: ', register_msg)
        self.assertIn('CSeq: ', register_msg)
        self.assertIn('REGISTER', register_msg)
        self.assertIn('Contact: <sip:testuser@example.com>', register_msg)
        self.assertIn('Expires: 3600', register_msg)
        self.assertIn('Max-Forwards: 70', register_msg)
        self.assertIn('User-Agent: GhostCaller/NoCaller-SIP/1.0', register_msg)
        # Should not have Authorization header
        self.assertNotIn('Authorization:', register_msg)
    
    def test_build_register_with_auth(self):
        """Test building REGISTER message with authentication."""
        # Setup auth data
        self.client.realm = 'testrealm'
        self.client.nonce = 'testnonce'
        
        # Execute
        register_msg = self.client._build_register(auth=True)
        
        # Verify
        self.assertIn('Authorization:', register_msg)
        self.assertIn('Digest username="testuser"', register_msg)
        self.assertIn('realm="testrealm"', register_msg)
        self.assertIn('nonce="testnonce"', register_msg)
    
    @patch('socket.socket')
    def test_register_success_no_auth(self, mock_socket_class):
        """Test successful registration when no auth is needed."""
        # Setup mocks
        mock_sock = Mock()
        mock_socket_class.return_value = mock_sock
        mock_sock.connect.return_value = None
        mock_sock.recvfrom.return_value = (
            b'SIP/2.0 200 OK\r\n'
            b'Via: SIP/2.0/UDP example.com;branch=z9hG4bK12345\r\n'
            b'From: <sip:testuser@example.com>;tag=1234\r\n'
            b'To: <sip:testuser@example.com>;tag=5678\r\n'
            b'Call-ID: 12345@example.com\r\n'
            b'CSeq: 1 REGISTER\r\n'
            b'Content-Length: 0\r\n'
            b'\r\n',
            ('test.sip.example.com', 5060)
        )
        
        # Create fresh client and connect
        client = SIPClient(self.config)
        client.connect()
        
        # Execute
        result = client.register()
        
        # Verify
        self.assertTrue(result)
        # Should have sent register message twice (initial + retry if needed, but in this case just once since 200 OK)
        self.assertEqual(mock_sock.sendto.call_count, 1)
        # Check that the message sent was a REGISTER
        call_args = mock_sock.sendto.call_args[0][0]
        self.assertIn(b'REGISTER', call_args)
    
    @patch('socket.socket')
    def test_register_success_with_auth(self, mock_socket_class):
        """Test successful registration requiring authentication."""
        # Setup mocks
        mock_sock = Mock()
        mock_socket_class.return_value = mock_sock
        mock_sock.connect.return_value = None
        
        # First response: 401 Unauthorized
        # Second response: 200 OK after auth
        mock_sock.recvfrom.side_effect = [
            (
                b'SIP/2.0 401 Unauthorized\r\n'
                b'Via: SIP/2.0/UDP example.com;branch=z9hG4bK12345\r\n'
                b'From: <sip:testuser@example.com>;tag=1234\r\n'
                b'To: <sip:testuser@example.com>;tag=5678\r\n'
                b'Call-ID: 12345@example.com\r\n'
                b'CSeq: 1 REGISTER\r\n'
                b'WWW-Authenticate: Digest realm="testrealm", nonce="testnonce"\r\n'
                b'Content-Length: 0\r\n'
                b'\r\n',
                ('test.sip.example.com', 5060)
            ),
            (
                b'SIP/2.0 200 OK\r\n'
                b'Via: SIP/2.0/UDP example.com;branch=z9hG4bK67890\r\n'
                b'From: <sip:testuser@example.com>;tag=1234\r\n'
                b'To: <sip:testuser@example.com>;tag=5678\r\n'
                b'Call-ID: 12345@example.com\r\n'
                b'CSeq: 2 REGISTER\r\n'
                b'Content-Length: 0\r\n'
                b'\r\n',
                ('test.sip.example.com', 5060)
            )
        ]
        
        # Create fresh client and connect
        client = SIPClient(self.config)
        client.connect()
        
        # Execute
        result = client.register()
        
        # Verify
        self.assertTrue(result)
        # Should have sent register message twice (first without auth, second with auth)
        self.assertEqual(mock_sock.sendto.call_count, 2)
        
        # Check first message (no auth)
        first_call_args = mock_sock.sendto.call_args_list[0][0][0]
        self.assertIn(b'REGISTER', first_call_args)
        self.assertNotIn(b'Authorization:', first_call_args)
        
        # Check second message (with auth)
        second_call_args = mock_sock.sendto.call_args_list[1][0][0]
        self.assertIn(b'REGISTER', second_call_args)
        self.assertIn(b'Authorization:', second_call_args)
        self.assertIn(b'Digest username="testuser"', second_call_args)
        self.assertIn(b'realm="testrealm"', second_call_args)
        self.assertIn(b'nonce="testnonce"', second_call_args)
    
    @patch('socket.socket')
    def register_failure(self, mock_socket_class):
        """Test registration failure."""
        # Setup mocks
        mock_sock = Mock()
        mock_socket_class.return_value = mock_sock
        mock_sock.connect.return_value = None
        mock_sock.recvfrom.return_value = (
            b'SIP/2.0 400 Bad Request\r\n'
            b'Content-Length: 0\r\n'
            b'\r\n',
            ('test.sip.example.com', 5060)
        )
        
        # Create fresh client and connect
        client = SIPClient(self.config)
        client.connect()
        
        # Execute
        result = client.register()
        
        # Verify
        self.assertFalse(result)
        self.assertEqual(mock_sock.sendto.call_count, 1)
    
    @patch('socket.socket')
    def test_register_network_error(self, mock_socket_class):
        """Test registration with network error."""
        # Setup mocks
        mock_sock = Mock()
        mock_socket_class.return_value = mock_sock
        mock_sock.connect.return_value = None
        mock_sock.sendto.side_effect = socket.error("Network error")
        
        # Create fresh client and connect
        client = SIPClient(self.config)
        client.connect()
        
        # Execute
        result = client.register()
        
        # Verify
        self.assertFalse(result)
    
    def test_register_when_not_connected(self):
        """Test registration when not connected."""
        # Setup disconnected state
        self.client.sock = None
        self.client.connected = False
        
        # Execute
        result = self.client.register()
        
        # Verify
        self.assertFalse(result)
        self.assertFalse(self.client.connected)
    
    def test_handle_401_extracts_auth_info(self):
        """Test that _handle_401 correctly extracts realm and nonce."""
        # Setup
        response = (
            'SIP/2.0 401 Unauthorized\r\n'
            'Via: SIP/2.0/UDP example.com;branch=z9hG4bK12345\r\n'
            'From: <sip:testuser@example.com>;tag=1234\r\n'
            'To: <sip:testuser@example.com>;tag=5678\r\n'
            'Call-ID: 12345@example.com\r\n'
            'CSeq: 1 REGISTER\r\n'
            'WWW-Authenticate: Digest realm="testrealm", nonce="testnonce"\r\n'
            'Content-Length: 0\r\n'
            '\r\n'
        )
        
        # Execute
        self.client._handle_401(response)
        
        # Verify
        self.assertEqual(self.client.realm, 'testrealm')
        self.assertEqual(self.client.nonce, 'testnonce')
    
    def test_handle_401_missing_auth_header(self):
        """Test _handle_401 when WWW-Authenticate header is missing."""
        # Setup
        response = (
            'SIP/2.0 401 Unauthorized\r\n'
            'Content-Length: 0\r\n'
            '\r\n'
        )
        
        # Execute
        self.client._handle_401(response)
        
        # Verify - should not crash and auth info should remain None
        self.assertIsNone(self.client.realm)
        self.assertIsNone(self.client.nonce)
    
    def test_handle_401_malformed_auth_header(self):
        """Test _handle_401 with malformed WWW-Authenticate header."""
        # Setup
        response = (
            'SIP/2.0 401 Unauthorized\r\n'
            'WWW-Authenticate: Invalid format\r\n'
            'Content-Length: 0\r\n'
            '\r\n'
        )
        
        # Execute
        self.client._handle_401(response)
        
        # Verify - should not crash and auth info should remain None
        self.assertIsNone(self.client.realm)
        self.assertIsNone(self.client.nonce)


if __name__ == '__main__':
    unittest.main()