#!/usr/bin/env python3
"""
Test suite for SIP Client connection functionality
Tests both TLS and non-TLS connection scenarios
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import socket
import ssl

# Import the SIPClient class
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from SIPClient import SIPClient


class TestSIPClientConnection(unittest.TestCase):
    
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
    
    def test_init_sets_correct_attributes(self):
        """Test that initialization sets all attributes correctly."""
        self.assertEqual(self.client.sip_server, 'test.sip.example.com')
        self.assertEqual(self.client.sip_port, 5060)
        self.assertEqual(self.client.username, 'testuser')
        self.assertEqual(self.client.password, 'testpass')
        self.assertEqual(self.client.domain, 'example.com')
        self.assertEqual(self.client.use_tls, False)
        self.assertEqual(self.client.transport, 'UDP')
        self.assertIsNone(self.client.sock)
        self.assertFalse(self.client.connected)
    
    @patch('socket.socket')
    @patch('ssl.create_default_context')
    def test_connect_udp_success(self, mock_ssl_context, mock_socket_class):
        """Test successful UDP connection."""
        # Setup mocks
        mock_sock = Mock()
        mock_socket_class.return_value = mock_sock
        mock_sock.connect.return_value = None
        
        # Execute
        result = self.client.connect()
        
        # Verify
        self.assertTrue(result)
        self.assertTrue(self.client.connected)
        self.assertEqual(self.client.sock, mock_sock)
        mock_socket_class.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)
        mock_sock.settimeout.assert_called_once_with(10)
        mock_sock.connect.assert_called_once_with(('test.sip.example.com', 5060))
        # TLS should not be used
        mock_ssl_context.assert_not_called()
    
    @patch('socket.socket')
    @patch('ssl.create_default_context')
    def test_connect_tls_success(self, mock_ssl_context, mock_socket_class):
        """Test successful TLS connection."""
        # Setup config for TLS
        tls_config = self.config.copy()
        tls_config['use_tls'] = True
        client = SIPClient(tls_config)
        
        # Setup mocks
        mock_sock = Mock()
        mock_ssl_sock = Mock()
        mock_socket_class.return_value = mock_sock
        mock_ssl_context.return_value.wrap_socket.return_value = mock_ssl_sock
        mock_ssl_sock.connect.return_value = None
        
        # Execute
        result = client.connect()
        
        # Verify
        self.assertTrue(result)
        self.assertTrue(client.connected)
        self.assertEqual(client.sock, mock_ssl_sock)
        self.assertEqual(client.sip_port, 5061)  # TLS port
        mock_socket_class.assert_called_once_with(socket.AF_INET)
        mock_ssl_context.assert_called_once()
        mock_ssl_context.return_value.wrap_socket.assert_called_once_with(
            mock_sock, server_hostname='test.sip.example.com'
        )
        mock_ssl_sock.settimeout.assert_called_once_with(10)
        mock_ssl_sock.connect.assert_called_once_with(('test.sip.example.com', 5061))
    
    @patch('socket.socket')
    def test_connect_failure_handling(self, mock_socket_class):
        """Test connection failure handling."""
        # Setup mock to raise exception
        mock_socket_class.side_effect = socket.error("Connection refused")
        
        # Execute
        result = self.client.connect()
        
        # Verify
        self.assertFalse(result)
        self.assertFalse(self.client.connected)
        self.assertIsNone(self.client.sock)
    
    @patch('socket.socket')
    def test_connect_timeout(self, mock_socket_class):
        """Test connection timeout handling."""
        # Setup mock to raise timeout
        mock_socket_class.side_effect = socket.timeout("Connection timeout")
        
        # Execute
        result = self.client.connect()
        
        # Verify
        self.assertFalse(result)
        self.assertFalse(self.client.connected)
        self.assertIsNone(self.client.sock)
    
    def test_disconnect_cleans_up_resources(self):
        """Test that disconnect properly cleans up resources."""
        # Setup connected state
        mock_sock = Mock()
        self.client.sock = mock_sock
        self.client.connected = True
        
        # Execute
        self.client.disconnect()
        
        # Verify
        mock_sock.close.assert_called_once()
        # Note: disconnect() closes the socket but doesn't set it to None in the current implementation
        self.assertEqual(self.client.sock, mock_sock)
        self.assertFalse(self.client.connected)
    
    def test_disconnect_when_not_connected(self):
        """Test disconnect when not connected doesn't error."""
        # Setup disconnected state
        self.client.sock = None
        self.client.connected = False
        
        # Execute - should not raise exception
        try:
            self.client.disconnect()
        except Exception:
            self.fail("disconnect() raised Exception when not connected!")
        
        # Verify state unchanged (sock remains None, connected remains False)
        self.assertIsNone(self.client.sock)
        self.assertFalse(self.client.connected)


if __name__ == '__main__':
    unittest.main()