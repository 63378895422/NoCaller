#!/usr/bin/env python3
"""
SIP Client integration for GhostCaller/NoCaller
Provides PBX and SIP server connectivity for advanced calling capabilities
"""

import socket
import ssl
import hashlib
import base64
import time
import random
import uuid
import re
from urllib.parse import quote


class SIPClient:
    """SIP client for connecting to PBX systems and SIP servers"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.sock = None
        self.connected = False
        self.call_id = str(uuid.uuid4())
        self.branch = "z9hG4bK" + str(random.randint(100000, 999999))
        
        # SIP server configuration
        self.sip_server = self.config.get('sip_server', 'sip.example.com')
        self.sip_port = self.config.get('sip_port', 5060)
        self.username = self.config.get('username', 'user')
        self.password = self.config.get('password', 'pass')
        self.domain = self.config.get('domain', 'example.com')
        self.use_tls = self.config.get('use_tls', False)
        self.transport = self.config.get('transport', 'UDP')
        
        # Call configuration
        self.from_uri = self.config.get('from_uri', f'sip:{self.username}@{self.domain}')
        self.to_uri = None
        self.contact_uri = self.config.get('contact_uri', f'sip:{self.username}@{self.domain}')
        
        # Authentication
        self.nonce = None
        self.realm = None
        self.qop = "auth"
        
    def connect(self):
        """Establish connection to SIP server"""
        try:
            if self.use_tls:
                context = ssl.create_default_context()
                self.sock = context.wrap_socket(socket.socket(socket.AF_INET), 
                                              server_hostname=self.sip_server)
                self.sip_port = 5061  # Default TLS port
            else:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            self.sock.settimeout(10)
            self.sock.connect((self.sip_server, self.sip_port))
            self.connected = True
            print(f"✓ Connected to SIP server: {self.sip_server}:{self.sip_port}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to connect to SIP server: {e}")
            self.connected = False
            return False
    
    def register(self):
        """Register with SIP server"""
        if not self.connected:
            print("✗ Not connected to SIP server")
            return False
            
        try:
            register_msg = self._build_register()
            self.sock.sendto(register_msg.encode(), (self.sip_server, self.sip_port))
            response = self._receive_response()
            
            if response and '401' in response:
                self._handle_401(response)
                # Retry with authentication
                register_msg = self._build_register(auth=True)
                self.sock.sendto(register_msg.encode(), (self.sip_server, self.sip_port))
                response = self._receive_response()
            
            if response and '200' in response:
                print("✓ SIP registration successful")
                return True
            else:
                print("✗ SIP registration failed")
                return False
                
        except Exception as e:
            print(f"✗ SIP registration error: {e}")
            return False
    
    def make_call(self, caller_id, target_number, pdu_message=None):
        """Initiate a call with custom caller ID"""
        try:
            # Format phone number for SIP
            sip_target = self._format_for_sip(target_number)
            self.to_uri = f"sip:{sip_target}@{self.sip_server}"
            
            invite_msg = self._build_invite(caller_id, target_number, pdu_message)
            self.sock.sendto(invite_msg.encode(), (self.sip_server, self.sip_port))
            
            response = self._receive_response()
            
            if response and '100' in response and '180' in response and '200' in response:
                print(f"✓ Call initiated: {caller_id} -> {target_number}")
                return True
            else:
                print("✗ Call initiation failed")
                return False
                
        except Exception as e:
            print(f"✗ Error making call: {e}")
            return False
    
    def send_sms_via_sip(self, sender, recipient, message, pdu_data=None):
        """Send SMS via SIP MESSAGE method or convert to call with SMS content"""
        try:
            # Method 1: Use SIP MESSAGE (if supported)
            if self._send_sip_message(sender, recipient, message):
                return True
            
            # Method 2: Create call with SMS PDU in custom headers
            return self._send_call_with_sms(sender, recipient, message, pdu_data)
            
        except Exception as e:
            print(f"✗ Error sending SMS via SIP: {e}")
            return False
    
    def _send_sip_message(self, sender, recipient, message):
        """Send SMS using SIP MESSAGE method"""
        try:
            sip_target = self._format_for_sip(recipient)
            to_uri = f"sip:{sip_target}@{self.sip_server}"
            
            message_body = f"From: {sender}\n\n{message}"
            
            msg = f"MESSAGE {to_uri} SIP/2.0\r\n"
            msg += f"Via: SIP/2.0/UDP {self.domain};branch={self.branch}\r\n"
            msg += f"From: {self.from_uri};tag={random.randint(1000, 9999)}\r\n"
            msg += f"To: {to_uri}\r\n"
            msg += f"Call-ID: {self.call_id}@{self.domain}\r\n"
            msg += f"CSeq: {random.randint(100, 999)} MESSAGE\r\n"
            msg += f"Contact: {self.contact_uri}\r\n"
            msg += f"Content-Type: text/plain\r\n"
            msg += f"Content-Length: {len(message_body)}\r\n"
            msg += f"Max-Forwards: 70\r\n"
            msg += f"User-Agent: GhostCaller/NoCaller-SIP/1.0\r\n"
            msg += f"\r\n{message_body}"
            
            self.sock.sendto(msg.encode(), (self.sip_server, self.sip_port))
            response = self._receive_response()
            
            if response and '200' in response:
                print("✓ SMS sent via SIP MESSAGE")
                return True
            return False
            
        except Exception as e:
            print(f"SIP MESSAGE failed: {e}")
            return False
    
    def _send_call_with_sms(self, sender, recipient, message, pdu_data):
        """Send SMS by creating call with SMS content in custom headers"""
        try:
            # Use custom headers to carry SMS data
            custom_headers = {
                'X-SMS-Sender': sender,
                'X-SMS-Recipient': recipient,
                'X-SMS-Message': message[:160],  # SMS limit
                'X-SMS-PDU': pdu_data[:200] if pdu_data else ''
            }
            
            return self.make_call(sender, recipient, message, custom_headers)
            
        except Exception as e:
            print(f"Call-with-SMS failed: {e}")
            return False
    
    def _build_register(self, auth=False):
        """Build SIP REGISTER message"""
        msg = f"REGISTER sip:{self.sip_server} SIP/2.0\r\n"
        msg += f"Via: SIP/2.0/UDP {self.domain};branch={self.branch}\r\n"
        msg += f"From: <{self.from_uri}>;tag={random.randint(1000, 9999)}\r\n"
        msg += f"To: <{self.from_uri}>\r\n"
        msg += f"Call-ID: {self.call_id}@{self.domain}\r\n"
        msg += f"CSeq: {random.randint(100, 999)} REGISTER\r\n"
        msg += f"Contact: <{self.contact_uri}>\r\n"
        msg += f"Expires: 3600\r\n"
        msg += f"Max-Forwards: 70\r\n"
        msg += f"User-Agent: GhostCaller/NoCaller-SIP/1.0\r\n"
        
        if auth:
            auth_header = self._build_auth_header('REGISTER', f"sip:{self.sip_server}")
            msg += f"Authorization: {auth_header}\r\n"
        
        msg += f"\r\n"
        return msg
    
    def _build_invite(self, caller_id, target_number, pdu_message=None):
        """Build SIP INVITE message with caller ID spoofing"""
        msg = f"INVITE {self.to_uri} SIP/2.0\r\n"
        msg += f"Via: SIP/2.0/UDP {self.domain};branch={self.branch}\r\n"
        msg += f"From: <sip:{caller_id}@{self.domain}>;tag={random.randint(1000, 9999)}\r\n"
        msg += f"To: <{self.to_uri}>\r\n"
        msg += f"Call-ID: {self.call_id}@{self.domain}\r\n"
        msg += f"CSeq: {random.randint(100, 999)} INVITE\r\n"
        msg += f"Contact: <{self.contact_uri}>\r\n"
        msg += f"Content-Type: application/sdp\r\n"
        msg += f"Content-Length: 200\r\n"
        msg += f"Max-Forwards: 70\r\n"
        msg += f"User-Agent: GhostCaller/NoCaller-SIP/1.0\r\n"
        
        # Add caller ID spoofing in display name
        caller_display = f'"{caller_id}"'
        msg = msg.replace("From: <sip:", f"From: {caller_display} <sip:")
        
        # Add custom headers for SMS data if provided
        if pdu_message:
            for header, value in pdu_message.items():
                if header.startswith('X-'):
                    msg += f"{header}: {value}\r\n"
        
        # Add basic SDP
        sdp = f"v=0\r\no=- 0 0 IN IP4 {self.domain}\r\ns=Session\r\nc=IN IP4 {self.domain}\r\nt=0 0\r\nm=audio 5004 RTP/AVP 0"
        msg += f"\r\n{sdp}"
        
        return msg
    
    def _build_auth_header(self, method, uri):
        """Build SIP authentication header"""
        if not self.nonce:
            return None
            
        ha1 = hashlib.md5(f"{self.username}:{self.realm}:{self.password}".encode()).hexdigest()
        ha2 = hashlib.md5(f"{method}:{uri}".encode()).hexdigest()
        response = hashlib.md5(f"{ha1}:{self.nonce}:00000001:{random.randint(1000,9999)}:{self.qop}:{ha2}".encode()).hexdigest()
        
        return f'Digest username="{self.username}", realm="{self.realm}", nonce="{self.nonce}", uri="{uri}", response="{response}", qop={self.qop}, nc=00000001, cnonce="{random.randint(1000,9999)}"'
    
    def _handle_401(self, response):
        """Handle 401 Unauthorized response"""
        try:
            if 'WWW-Authenticate:' in response:
                auth_line = [line for line in response.split('\n') if 'WWW-Authenticate:' in line][0]
                
                # Parse realm and nonce
                realm_match = re.search(r'realm="([^"]*)"', auth_line)
                nonce_match = re.search(r'nonce="([^"]*)"', auth_line)
                
                if realm_match and nonce_match:
                    self.realm = realm_match.group(1)
                    self.nonce = nonce_match.group(1)
                    print(f"✓ Extracted authentication info - realm: {self.realm}")
                    
        except Exception as e:
            print(f"✗ Error parsing 401 response: {e}")
    
    def _receive_response(self):
        """Receive and parse SIP response"""
        try:
            data, addr = self.sock.recvfrom(4096)
            response = data.decode('utf-8', errors='ignore')
            print(f"SIP Response received ({len(response)} bytes)")
            return response
        except socket.timeout:
            print("✗ SIP response timeout")
            return None
        except Exception as e:
            print(f"✗ Error receiving SIP response: {e}")
            return None
    
    def _format_for_sip(self, phone_number):
        """Format phone number for SIP URI"""
        # Remove non-numeric characters except +
        cleaned = re.sub(r'[^\d+]', '', phone_number)
        
        # If it's already international format, use as is
        if cleaned.startswith('+'):
            return cleaned
        
        # Add country code if missing
        if len(cleaned) == 10:  # US number
            return f"+1{cleaned}"
        
        return cleaned
    
    def disconnect(self):
        """Disconnect from SIP server"""
        if self.sock:
            self.sock.close()
            self.connected = False
            print("✓ Disconnected from SIP server")


def test_sip_client():
    """Test SIP client functionality"""
    print("Testing SIP Client...")
    
    # Test configuration (should be updated with real SIP server details)
    config = {
        'sip_server': 'sip.example.com',
        'sip_port': 5060,
        'username': 'testuser',
        'password': 'testpass',
        'domain': 'example.com',
        'use_tls': False,
        'transport': 'UDP'
    }
    
    client = SIPClient(config)
    
    # Test connection (will fail with example.com)
    try:
        print("Attempting connection...")
        # Note: This will fail with the example configuration
        # In real use, configure with actual SIP server
        if client.connect():
            print("✓ Connection successful")
            
            # Test registration
            # client.register()
            
            # Test call
            # client.make_call("+1234567890", "+1987654321")
            
            # Test SMS
            # client.send_sms_via_sip("TestSender", "+1234567890", "Test message")
            
            client.disconnect()
        else:
            print("✗ Connection failed (expected with example config)")
            
    except Exception as e:
        print(f"Test error: {e}")


if __name__ == "__main__":
    test_sip_client()