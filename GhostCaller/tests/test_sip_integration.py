#!/usr/bin/env python3
"""
Integration test for SIP Client with configuration file
Tests that SIPClient can be properly configured and instantiated
"""

import unittest
import os
import sys
import configparser

# Add the GhostCaller directory to the path
ghostcaller_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ghostcaller_dir)

from SIPClient import SIPClient
from GhostCaller import load_sip_config, construct_pdu, send_sms_via_sip, make_sip_call


class TestSIPIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_path = os.path.join(ghostcaller_dir, 'sip_config.ini')
    
    def test_config_file_exists(self):
        """Test that sip_config.ini exists."""
        self.assertTrue(os.path.exists(self.config_path), 
                       "sip_config.ini file should exist")
    
    def test_load_sip_config_from_file(self):
        """Test loading SIP configuration from file."""
        config = load_sip_config(self.config_path)
        
        # Should return a dictionary with expected keys
        self.assertIsInstance(config, dict)
        self.assertIn('sip_server', config)
        self.assertIn('sip_port', config)
        self.assertIn('username', config)
        self.assertIn('password', config)
        self.assertIn('domain', config)
        self.assertIn('use_tls', config)
        self.assertIn('transport', config)
        
        # Check values match the file
        self.assertEqual(config['sip_server'], 'sip.example.com')
        self.assertEqual(config['sip_port'], 5060)
        self.assertEqual(config['username'], 'your_username')
        self.assertEqual(config['password'], 'your_password')
        self.assertEqual(config['domain'], 'example.com')
        self.assertEqual(config['use_tls'], False)
        self.assertEqual(config['transport'], 'UDP')
    
    def test_sip_client_creation_with_config(self):
        """Test creating SIPClient with configuration from file."""
        config = load_sip_config(self.config_path)
        client = SIPClient(config)
        
        self.assertIsInstance(client, SIPClient)
        self.assertEqual(client.sip_server, 'sip.example.com')
        self.assertEqual(client.sip_port, 5060)
        self.assertEqual(client.username, 'your_username')
        self.assertEqual(client.password, 'your_password')
        self.assertEqual(client.domain, 'example.com')
        self.assertEqual(client.use_tls, False)
        self.assertEqual(client.transport, 'UDP')
    
    def test_sip_client_defaults_when_config_missing(self):
        """Test SIPClient uses defaults when config values missing."""
        # Create minimal config
        minimal_config = {}
        client = SIPClient(minimal_config)
        
        # Should use defaults from __init__
        self.assertEqual(client.sip_server, 'sip.example.com')  # default
        self.assertEqual(client.sip_port, 5060)  # default
        self.assertEqual(client.username, 'user')  # default
        self.assertEqual(client.password, 'pass')  # default
        self.assertEqual(client.domain, 'example.com')  # default
        self.assertEqual(client.use_tls, False)  # default
        self.assertEqual(client.transport, 'UDP')  # default
    
    def test_construct_pdu_still_works(self):
        """Test that the original PDU construction functionality still works."""
        pdu = construct_pdu('TestSender', '+1234567890', 'Test message')
        
        self.assertIsNotNone(pdu)
        self.assertIsInstance(pdu, str)
        self.assertTrue(len(pdu) > 0)
        # Should start with SMS-SUBMIT header
        self.assertTrue(pdu.startswith('0011'))  # 00 = SMSC, 11 = SMS-SUBMIT
    
    def test_make_sip_call_function_exists(self):
        """Test that make_sip_call function exists and is callable."""
        self.assertTrue(callable(make_sip_call))
    
    def test_send_sms_via_sip_function_exists(self):
        """Test that send_sms_via_sip function exists and is callable."""
        self.assertTrue(callable(send_sms_via_sip))
    
    def test_sip_client_has_expected_methods(self):
        """Test that SIPClient has all expected methods."""
        expected_methods = [
            '__init__',
            'connect',
            'register',
            'make_call',
            'send_sms_via_sip',
            '_build_register',
            '_build_invite',
            '_build_auth_header',
            '_handle_401',
            '_receive_response',
            '_format_for_sip',
            'disconnect'
        ]
        
        for method in expected_methods:
            self.assertTrue(hasattr(SIPClient, method), 
                           f"SIPClient should have method {method}")
            attr = getattr(SIPClient, method)
            self.assertTrue(callable(attr) or method.startswith('__'), 
                           f"SIPClient.{method} should be callable")
    
    def test_sip_client_initial_state(self):
        """Test that SIPClient starts in correct initial state."""
        config = load_sip_config(self.config_path)
        client = SIPClient(config)
        
        # Initial state checks
        self.assertIsNone(client.sock)
        self.assertFalse(client.connected)
        self.assertIsInstance(client.call_id, str)
        self.assertTrue(len(client.call_id) > 0)
        self.assertTrue(client.branch.startswith('z9hG4bK'))
        self.assertIsInstance(client.from_uri, str)
        self.assertIsNone(client.to_uri)
        self.assertIsInstance(client.contact_uri, str)
        self.assertIsNone(client.nonce)
        self.assertIsNone(client.realm)
        self.assertEqual(client.qop, "auth")


if __name__ == '__main__':
    unittest.main()