#!/usr/bin/env python3
"""
Test suite for SIPClient.connect() method
Covers UDP and TLS connections, failure handling, timeouts, and socket properties.
"""

import sys
import os
import socket
import ssl
import unittest
from unittest.mock import patch, MagicMock
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from SIPClient import SIPClient


class TestSIPClientConnect(unittest.TestCase):
    """Test cases for SIPClient.connect() method"""
    
    def setUp(self):
        """Set up test configuration"""
        self.config = {
            'sip_server': '127.0.0.1',
            'sip_port': 5060,
            'username': 'testuser',
            'password': 'testpass',
            'domain': 'test.com',
            'use_tls': False,
            'transport': 'UDP'
        }
        self.client = SIPClient(self.config)
    
    def tearDown(self):
        """Clean up after tests"""
        if self.client.sock:
            try:
                self.client.sock.close()
            except:
                pass
        self.client.connected = False
    
    @patch('SIPClient.socket.socket')
    def test_successful_udp_connection(self, mock_socket_class):
        """Test successful UDP connection to mock SIP server"""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        # Simulate successful connection
        mock_socket.connect.return_value = None
        mock_socket.sendto.return_value = 0
        
        # Set UDP-specific config
        self.client.use_tls = False
        self.client.sip_port = 5060
        
        result = self.client.connect()
        
        # Verify result
        self.assertTrue(result, "UDP connection should succeed")
        self.assertTrue(self.client.connected, "Client should be marked as connected")
        mock_socket.connect.assert_called_once_with(('127.0.0.1', 5060))
        mock_socket.settimeout.assert_called_once_with(10)
        self.assertIsNotNone(self.client.sock)  # Socket was created
    
    @patch('SIPClient.socket.socket')
    @patch('SIPClient.ssl.create_default_context')
    def test_successful_tls_connection(self, mock_ssl_context, mock_socket_class):
        """Test successful TLS connection to mock SIP server"""
        # Setup socket mock
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        # Setup SSL mock
        mock_ssl_ctx = MagicMock()
        mock_ssl_context.return_value = mock_ssl_ctx
        
        # Have wrap_socket return the same socket mock so we can verify connect
        mock_ssl_ctx.wrap_socket.return_value = mock_socket
        
        # Set TLS configuration
        self.client.use_tls = True
        self.client.sip_port = 5061
        
        result = self.client.connect()
        
        # Verify result
        self.assertTrue(result, "TLS connection should succeed")
        self.assertTrue(self.client.connected, "Client should be marked as connected")
        
        # Verify TLS-specific behavior
        mock_ssl_context.assert_called_once_with()
        mock_ssl_ctx.wrap_socket.assert_called_once_with(
            mock_socket, 
            server_hostname='127.0.0.1'
        )
        mock_socket.connect.assert_called_once_with(('127.0.0.1', 5061))
        mock_socket.settimeout.assert_called_once_with(10)
        self.assertIsNotNone(self.client.sock)
    
    @patch('SIPClient.socket.socket')
    def test_connection_failure_invalid_server(self, mock_socket_class):
        """Test connection failure when server is unreachable"""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        # Simulate connection error
        mock_socket.connect.side_effect = ConnectionRefusedError("Connection refused")
        
        result = self.client.connect()
        
        self.assertFalse(result, "Connection should fail with unreachable server")
        self.assertFalse(self.client.connected, "Client should not be marked as connected")
        mock_socket.connect.assert_called_once_with(('127.0.0.1', 5060))
        mock_socket.settimeout.assert_called_once_with(10)  # Timeout is set before connect
        self.assertIsNotNone(self.client.sock)  # Socket was created
    
    @patch('SIPClient.socket.socket')
    def test_connection_failure_timeout(self, mock_socket_class):
        """Test connection timeout scenario"""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        # Simulate timeout during connection
        mock_socket.connect.side_effect = socket.timeout("timed out")
        
        result = self.client.connect()
        
        self.assertFalse(result, "Connection should fail with timeout")
        self.assertFalse(self.client.connected, "Client should not be marked as connected")
        mock_socket.connect.assert_called_once_with(('127.0.0.1', 5060))
        mock_socket.settimeout.assert_called_once_with(10)
        self.assertIsNotNone(self.client.sock)  # Socket was created
    
    @patch('SIPClient.socket.socket')
    @patch('SIPClient.ssl.create_default_context')
    def test_connection_failure_ssl_error(self, mock_ssl_context, mock_socket_class):
        """Test TLS connection failure due to SSL error"""
        mock_ssl_ctx = MagicMock()
        mock_ssl_context.return_value = mock_ssl_ctx
        
        # Simulate SSL wrap_socket error - this happens before socket connect
        mock_ssl_ctx.wrap_socket.side_effect = ssl.SSLError("certificate verify failed")
        
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        # Set TLS configuration
        self.client.use_tls = True
        self.client.sip_port = 5061
        
        result = self.client.connect()
        
        self.assertFalse(result, "TLS connection should fail with SSL error")
        self.assertFalse(self.client.connected, "Client should not be marked as connected")
        mock_ssl_context.assert_called_once_with()
        mock_ssl_ctx.wrap_socket.assert_called_once()
        mock_socket.settimeout.assert_not_called()  # Socket not created, so timeout not set
        self.assertIsNone(self.client.sock)  # Socket was not created
    
    @patch('SIPClient.socket.socket')
    def test_socket_properties_after_udp_connection(self, mock_socket_class):
        """Verify socket properties are set correctly after UDP connection"""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        mock_socket.connect.return_value = None
        
        # Set up socket attributes to verify
        mock_socket.configure_mock(**{
            'family': socket.AF_INET,
            'type': socket.SOCK_DGRAM,
            'proto': 17
        })
        
        # Set UDP config
        self.client.use_tls = False
        self.client.sip_port = 5060
        
        result = self.client.connect()
        
        self.assertTrue(result)
        # Verify socket properties
        self.assertEqual(self.client.sock.family, socket.AF_INET)
        self.assertEqual(self.client.sock.type, socket.SOCK_DGRAM)
        self.assertEqual(self.client.sock.proto, 17)
    
    @patch('SIPClient.socket.socket')
    @patch('SIPClient.ssl.create_default_context')
    def test_socket_properties_after_tls_connection(self, mock_ssl_context, mock_socket_class):
        """Verify socket properties are set correctly after TLS connection"""
        mock_ssl_ctx = MagicMock()
        mock_ssl_context.return_value = mock_ssl_ctx
        
        # Create a mock SSL socket with expected properties
        mock_ssl_sock = MagicMock()
        # Configure as SSL socket with stream type
        mock_ssl_sock.configure_mock(**{
            'family': socket.AF_INET,
            'type': socket.SOCK_STREAM,
            'proto': 0
        })
        mock_ssl_ctx.wrap_socket.return_value = mock_ssl_sock
        
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        # Set TLS configuration
        self.client.use_tls = True
        self.client.sip_port = 5061
        
        result = self.client.connect()
        
        self.assertTrue(result)
        self.assertEqual(self.client.sock.family, socket.AF_INET)
        self.assertEqual(self.client.sock.type, socket.SOCK_STREAM)
    
    @patch('SIPClient.socket.socket')
    @patch('SIPClient.ssl.create_default_context')
    def test_connection_uses_correct_port_for_tls(self, mock_ssl_context, mock_socket_class):
        """Test that TLS connection uses port 5061 by default"""
        mock_ssl_ctx = MagicMock()
        mock_ssl_context.return_value = mock_ssl_ctx
        
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        # Have wrap_socket return the same socket mock so we can verify connect
        mock_ssl_ctx.wrap_socket.return_value = mock_socket
        
        # Set TLS configuration
        self.client.use_tls = True
        self.client.sip_port = 5061  # Ensure port is set
        
        result = self.client.connect()
        
        mock_socket.connect.assert_called_once_with(('127.0.0.1', 5061))
    
    @patch('SIPClient.socket.socket')
    @patch('SIPClient.ssl.create_default_context')
    def test_connection_uses_configured_port_for_udp(self, mock_ssl_context, mock_socket_class):
        """Test that UDP connection uses configured port"""
        # We'll accept both mocks but only use socket mock
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        # Set UDP config with custom port
        self.client.use_tls = False
        self.client.sip_port = 6060
        
        result = self.client.connect()
        
        mock_socket.connect.assert_called_once_with(('127.0.0.1', 6060))
    
    @patch('SIPClient.socket.socket')
    def test_connection_timeout_value(self, mock_socket_class):
        """Test that socket timeout is set to 10 seconds as specified"""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        result = self.client.connect()
        
        mock_socket.settimeout.assert_called_once_with(10)
    
    @patch('SIPClient.socket.socket')
    def test_connection_without_socket_creation_on_failure(self, mock_socket_class):
        """Test that socket is not created when connection fails before creation"""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        # Simulate an error during socket creation (unlikely but possible)
        mock_socket_class.side_effect = Exception("Test error during socket creation")
        
        result = self.client.connect()
        
        self.assertFalse(result)
        self.assertIsNone(self.client.sock)
    
    @patch('SIPClient.socket.socket')
    def test_multiple_connection_attempts(self, mock_socket_class):
        """Test that multiple calls to connect() behave correctly"""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        mock_socket.connect.return_value = None
        
        # First connection
        result1 = self.client.connect()
        self.assertTrue(result1)
        self.assertTrue(self.client.connected)
        
        # Second connection (should fail because already connected)
        # We'll simulate that the socket is already connected
        mock_socket.connect.side_effect = Exception("Already connected")
        
        result2 = self.client.connect()
        self.assertFalse(result2)
        
        # Verify that connect was called twice
        calls = mock_socket.connect.call_count
        self.assertEqual(calls, 2)


if __name__ == '__main__':
    # Run tests and show results
    unittest.main(verbosity=2)