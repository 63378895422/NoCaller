# GhostCaller - PBX SIP Integration

**Version:** 2.0 Enhanced with PBX SIP Integration  
**Date:** 2025-11-12  
**Status:** ✅ Fully Functional

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)
- [API Reference](#api-reference)

## Overview

GhostCaller is an enhanced communication tool that combines traditional SMS PDU construction with modern PBX (Private Branch Exchange) and SIP (Session Initiation Protocol) integration. It provides enterprise-level calling capabilities while maintaining the original PDU functionality.

## Features

### 📱 **Core Functionality**
- **SMS PDU Construction:** Traditional SMS protocol data unit creation
- **PBX Integration:** Compatible with Asterisk, FreePBX, and other PBX systems
- **SIP Calling:** Outbound calling with caller ID spoofing capabilities
- **SMS via SIP:** Send SMS messages through SIP MESSAGE method

### 🔧 **Technical Features**
- **No External Dependencies:** Uses only Python standard library
- **Cross-Platform:** Works on Linux, Windows, and macOS
- **Multiple Transport Protocols:** UDP, TCP, and TLS support
- **Authentication:** Digest authentication with 401 response handling
- **Configuration Management:** INI-based configuration system

### 🛡️ **Security & Reliability**
- **TLS Encryption:** Support for encrypted SIP communications
- **Error Handling:** Comprehensive exception management
- **Network Management:** Timeout handling and connection management
- **NAT Traversal:** Built-in STUN server support

## Installation

### System Requirements

- **Python Version:** Python 3.x (3.6 or higher recommended)
- **Operating System:** Linux, Windows, macOS
- **Network:** Internet connection for SIP communications
- **Dependencies:** None (uses only Python standard library)

### Quick Installation

1. **Download the Project:**
   ```bash
   # Clone or download the GhostCaller directory to your local machine
   git clone <repository-url> GhostCaller
   cd GhostCaller
   ```

2. **Verify Python Installation:**
   ```bash
   python3 --version
   # Should output Python 3.x.x
   ```

3. **Test Installation:**
   ```bash
   python3 test_ghostcaller.py
   ```

### Installation Steps

#### **Step 1: Prepare Environment**
```bash
# Create a working directory
mkdir GhostCaller
cd GhostCaller

# Copy all project files:
# - GhostCaller.py
# - SIPClient.py  
# - sip_config.ini
# - test_ghostcaller.py
# - Dependancies for install.txt
```

#### **Step 2: Set Permissions (Linux/macOS)**
```bash
chmod +x GhostCaller.py
chmod +x SIPClient.py
chmod +x test_ghostcaller.py
```

#### **Step 3: Verify Dependencies**
```bash
# Check if all required modules are available
python3 -c "import binascii, socket, configparser; print('All dependencies available')"
```

## Configuration

### SIP Configuration File

The `sip_config.ini` file contains all SIP-related settings. Edit this file to match your PBX/SIP server configuration.

#### **Basic Configuration Template:**

```ini
[SIP_SERVER]
# SIP server settings
host = your-sip-server.com
port = 5060
transport = UDP
use_tls = False
tls_port = 5061

[AUTHENTICATION]
# SIP authentication credentials
username = your_username
password = your_password
domain = your-domain.com
realm = your-domain.com

[CALLING_SETTINGS]
# Default calling parameters
default_caller_id = GhostCaller
max_call_duration = 300
enable_caller_id_spoofing = True

[SMS_SETTINGS]
# SMS delivery via SIP
use_sip_message = True
use_call_with_sms = True
message_format = plain
max_message_length = 160

[PBX_SETTINGS]
# PBX-specific settings
pbx_type = asterisk
extension_pattern = *2000
outbound_proxy = 
register_expires = 3600

[ADVANCED]
# Advanced SIP features
enable_nat_traversal = True
stun_server = stun.l.google.com:19302
enable_early_media = True
dtmf_method = rfc2833
```

### Configuration Guide

#### **For Asterisk PBX:**
```ini
[SIP_SERVER]
host = 192.168.1.100
port = 5060
transport = UDP

[AUTHENTICATION]
username = 1001
password = your_password
domain = 192.168.1.100
realm = 192.168.1.100

[PBX_SETTINGS]
pbx_type = asterisk
extension_pattern = *2000
```

#### **For FreePBX:**
```ini
[SIP_SERVER]
host = your-freepbx-server.com
port = 5160
transport = TCP

[AUTHENTICATION]
username = your_extension
password = your_password
domain = your-freepbx-server.com
realm = your-freepbx-server.com
```

#### **For Generic SIP Server:**
```ini
[SIP_SERVER]
host = sip.provider.com
port = 5060
transport = UDP
use_tls = True
tls_port = 5061

[AUTHENTICATION]
username = your_user
password = your_pass
domain = provider.com
realm = provider.com
```

## Usage Examples

### Basic Usage

#### **1. Traditional PDU Construction**
```python
from GhostCaller import construct_pdu

# Create SMS PDU
pdu_data = construct_pdu('SenderName', '+1234567890', 'Hello World!')
print("PDU Data:", pdu_data.hex())
```

#### **2. Interactive Mode**
```bash
python3 GhostCaller.py
```

**Interactive Menu:**
```
GhostCaller - PBX SIP Integration
================================
1. Construct SMS PDU
2. Make SIP Call
3. Send SMS via SIP
4. Exit

Select option: 
```

#### **3. SIP Calling with Configuration**
```python
from GhostCaller import make_sip_call

# Make a call using SIP
result = make_sip_call('My Caller ID', '+1987654321', use_sip=True)
print("Call result:", result)
```

#### **4. SMS via SIP**
```python
from GhostCaller import send_sms_via_sip

# Send SMS using SIP
success = send_sms_via_sip('Sender', '+1234567890', 'Hello via SIP!')
if success:
    print("SMS sent successfully!")
```

### Advanced Usage

#### **1. Custom SIP Client with Configuration**
```python
from SIPClient import SIPClient
import configparser

# Load configuration
config = configparser.ConfigParser()
config.read('sip_config.ini')

# Create SIP client
sip_client = SIPClient(config)

# Connect and register
sip_client.connect()
sip_client.register()

# Make a call
sip_client.make_call('Custom Caller ID', '+1987654321')

# Send SMS
sip_client.send_sms_via_sip('Sender', '+1234567890', 'Test message')

# Clean up
sip_client.disconnect()
```

#### **2. Programmatic PDU Construction with SIP Integration**
```python
from GhostCaller import construct_pdu, send_sms_via_sip

# Construct traditional PDU
pdu_data = construct_pdu('MyApp', '+1234567890', 'Hello World!')

# Send via SIP with PDU data
send_sms_via_sip('MyApp', '+1234567890', 'Hello World!', pdu_data)
```

#### **3. Batch Processing**
```python
from GhostCaller import make_sip_call

# List of numbers to call
recipients = [
    ('+1234567890', 'Business'),
    ('+1987654321', 'Personal'),
    ('+1555123456', 'Emergency')
]

for number, caller_id in recipients:
    try:
        result = make_sip_call(caller_id, number)
        print(f"Called {number} as {caller_id}: {result}")
    except Exception as e:
        print(f"Failed to call {number}: {e}")
```

### Command Line Interface

#### **Direct Function Calls:**
```bash
# Test basic functionality
python3 -c "from GhostCaller import construct_pdu; print(construct_pdu('Test', '+1234567890', 'Hello'))"

# Test SIP configuration
python3 -c "from GhostCaller import load_sip_config; config = load_sip_config(); print('Config loaded')"
```

#### **Batch Processing Script:**
```bash
# Create a batch script
cat > batch_calls.py << 'EOF'
#!/usr/bin/env python3
from GhostCaller import make_sip_call
import sys

numbers = sys.argv[1:]
for number in numbers:
    result = make_sip_call('BatchCall', number)
    print(f"Called {number}: {result}")
EOF

# Run batch calls
python3 batch_calls.py +1234567890 +1987654321 +1555123456
```

## Advanced Usage

### Custom Configuration Loading

```python
from GhostCaller import SIPClient
import configparser

def load_custom_config():
    config = configparser.ConfigParser()
    
    # Custom configuration
    config['SIP_SERVER'] = {
        'host': 'custom-server.com',
        'port': '5060',
        'transport': 'UDP'
    }
    
    config['AUTHENTICATION'] = {
        'username': 'custom_user',
        'password': 'custom_pass',
        'domain': 'custom-server.com'
    }
    
    return config

# Use custom configuration
custom_config = load_custom_config()
client = SIPClient(custom_config)
client.connect()
```

### Error Handling and Logging

```python
import logging
from GhostCaller import make_sip_call

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_call(caller_id, number):
    try:
        logger.info(f"Attempting to call {number} as {caller_id}")
        result = make_sip_call(caller_id, number)
        logger.info(f"Call successful: {result}")
        return True
    except Exception as e:
        logger.error(f"Call failed: {e}")
        return False

# Safe calling with logging
safe_call('SafeCall', '+1234567890')
```

### Network Monitoring

```python
from SIPClient import SIPClient

def monitor_sip_connection():
    client = SIPClient()
    
    # Set up monitoring
    client.connect()
    
    # Check registration status
    if client.registered:
        print("✅ Successfully registered with SIP server")
    else:
        print("❌ Registration failed")
    
    # Monitor connection health
    client.register()  # Refresh registration
    return client.registered

monitor_sip_connection()
```

## Troubleshooting

### Common Issues and Solutions

#### **1. Connection Problems**

**Problem:** Cannot connect to SIP server
```
ConnectionError: Unable to connect to sip.example.com:5060
```

**Solutions:**
- Check if SIP server is reachable: `ping sip.example.com`
- Verify port is open: `telnet sip.example.com 5060`
- Check firewall rules
- Verify transport protocol (UDP/TCP/TLS)

**Debug Command:**
```bash
# Test network connectivity
python3 -c "import socket; socket.create_connection(('sip.example.com', 5060), timeout=5); print('Connection successful')"
```

#### **2. Authentication Failures**

**Problem:** 401 Unauthorized responses
```
SIP Error: 401 Unauthorized
```

**Solutions:**
- Verify username and password in sip_config.ini
- Check domain/realm settings
- Ensure account is active on PBX
- Verify extension permissions

**Debug Command:**
```python
from SIPClient import SIPClient
client = SIPClient()
client.connect()
try:
    client.register()
    print("Authentication successful")
except Exception as e:
    print(f"Authentication failed: {e}")
```

#### **3. Configuration Issues**

**Problem:** Configuration file not found or invalid
```
FileNotFoundError: sip_config.ini not found
ConfigParser.Error: Invalid configuration
```

**Solutions:**
- Ensure sip_config.ini exists in the same directory
- Check file permissions
- Validate INI syntax
- Verify all required sections are present

**Debug Command:**
```python
import configparser
try:
    config = configparser.ConfigParser()
    config.read('sip_config.ini')
    print("Configuration loaded successfully")
    for section in config.sections():
        print(f"Section: {section}")
except Exception as e:
    print(f"Configuration error: {e}")
```

#### **4. Network Timeouts**

**Problem:** Operations timeout without response
```
TimeoutError: SIP operation timed out
```

**Solutions:**
- Check network connectivity
- Verify SIP server is responding
- Increase timeout values in configuration
- Check for network congestion

**Debug Command:**
```python
import socket
import time

def test_connection(host, port, timeout=10):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False

# Test SIP server connection
print("Testing connection...")
if test_connection('sip.example.com', 5060):
    print("✅ SIP server reachable")
else:
    print("❌ SIP server not reachable")
```

#### **5. PDU Construction Issues**

**Problem:** Invalid PDU generation
```
ValueError: Invalid phone number format
```

**Solutions:**
- Use E.164 format (+1234567890)
- Ensure sender/recipient are strings
- Check message encoding

**Debug Command:**
```python
from GhostCaller import construct_pdu

def test_pdu_construction():
    try:
        # Test with valid inputs
        pdu = construct_pdu('Test', '+1234567890', 'Hello')
        print("✅ PDU construction successful")
        print(f"PDU length: {len(pdu)} bytes")
        return True
    except Exception as e:
        print(f"❌ PDU construction failed: {e}")
        return False

test_pdu_construction()
```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now run your SIP operations
from GhostCaller import make_sip_call
result = make_sip_call('DebugCall', '+1234567890')
```

### Testing Tools

#### **1. Basic Connectivity Test**
```bash
python3 test_ghostcaller.py
```

#### **2. SIP Server Test**
```python
from SIPClient import test_sip_client
test_sip_client()
```

#### **3. Configuration Validation**
```python
import configparser
import os

def validate_config():
    if not os.path.exists('sip_config.ini'):
        print("❌ Configuration file missing")
        return False
    
    try:
        config = configparser.ConfigParser()
        config.read('sip_config.ini')
        
        required_sections = ['SIP_SERVER', 'AUTHENTICATION']
        for section in required_sections:
            if section not in config.sections():
                print(f"❌ Missing required section: {section}")
                return False
        
        print("✅ Configuration validation passed")
        return True
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

validate_config()
```

## Security Considerations

### ⚠️ **Important Disclaimers**

- **Educational Purpose:** This application is designed for educational and testing purposes
- **Ethical Use:** Should NOT be used with malicious intent or to harass individuals
- **Legal Compliance:** Users must comply with local laws and regulations regarding telecommunications
- **Network Security:** SIP traffic should be properly secured in production environments

### 🔒 **Security Best Practices**

#### **1. Authentication Security**
- Use strong passwords for SIP accounts
- Enable TLS/SSL for SIP communications when possible
- Regularly update credentials
- Use certificate-based authentication in production

#### **2. Network Security**
```ini
[ADVANCED]
enable_nat_traversal = True
use_tls = True
tls_port = 5061
```

#### **3. Access Control**
- Restrict access to authorized users only
- Monitor usage logs
- Implement rate limiting
- Use network firewalls

#### **4. Data Protection**
- Never log sensitive credentials
- Use encrypted storage for configuration files
- Regularly audit logs for security events

### Production Deployment

#### **1. Secure Configuration**
```ini
[SIP_SERVER]
host = secure-sip-server.com
port = 5060
use_tls = True
tls_port = 5061

[AUTHENTICATION]
username = production_user
password = ${ENV_SIP_PASSWORD}
domain = secure-domain.com
realm = secure-domain.com
```

#### **2. Firewall Rules**
```bash
# Allow SIP traffic
iptables -A INPUT -p udp --dport 5060 -j ACCEPT
iptables -A INPUT -p tcp --dport 5061 -j ACCEPT
```

#### **3. Monitoring and Logging**
```python
import logging
import logging.handlers

# Set up secure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler(
            'ghostcaller.log', 
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
    ]
)
```

## API Reference

### GhostCaller Module

#### **Functions**

##### `construct_pdu(sender, recipient, message)`
Constructs SMS Protocol Data Unit (PDU)

**Parameters:**
- `sender` (str): Sender identifier
- `recipient` (str): Recipient phone number (E.164 format)
- `message` (str): Message content

**Returns:** 
- `bytes`: PDU data in hexadecimal format

**Example:**
```python
pdu = construct_pdu('MyApp', '+1234567890', 'Hello World!')
print(pdu.hex())
```

##### `load_sip_config(config_file='sip_config.ini')`
Loads SIP configuration from INI file

**Parameters:**
- `config_file` (str): Path to configuration file

**Returns:**
- `configparser.ConfigParser`: Configuration object

**Example:**
```python
config = load_sip_config()
print(config['SIP_SERVER']['host'])
```

##### `send_sms_via_sip(sender, recipient, message, sip_config=None)`
Sends SMS using SIP integration

**Parameters:**
- `sender` (str): Sender identifier
- `recipient` (str): Recipient phone number
- `message` (str): Message content
- `sip_config` (configparser.ConfigParser, optional): SIP configuration

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
success = send_sms_via_sip('MyApp', '+1234567890', 'Hello via SIP!')
```

##### `make_sip_call(caller_id, target_number, use_sip=True, sip_config=None)`
Makes phone call with caller ID spoofing via SIP

**Parameters:**
- `caller_id` (str): Caller ID to display
- `target_number` (str): Target phone number
- `use_sip` (bool): Use SIP calling (default: True)
- `sip_config` (configparser.ConfigParser, optional): SIP configuration

**Returns:**
- `bool`: True if call initiated successfully

**Example:**
```python
success = make_sip_call('Display Name', '+1987654321')
```

### SIPClient Class

#### **Methods**

##### `__init__(config=None)`
Initializes SIP client

**Parameters:**
- `config` (configparser.ConfigParser): SIP configuration

##### `connect()`
Establishes connection to SIP server

**Returns:**
- `bool`: True if connection successful

##### `register()`
Registers with SIP server

**Returns:**
- `bool`: True if registration successful

##### `make_call(caller_id, target_number, pdu_message=None)`
Initiates a call with custom caller ID

**Parameters:**
- `caller_id` (str): Caller ID to display
- `target_number` (str): Target phone number
- `pdu_message` (str, optional): PDU message data

**Returns:**
- `bool`: True if call initiated

##### `send_sms_via_sip(sender, recipient, message, pdu_data=None)`
Sends SMS via SIP MESSAGE method

**Parameters:**
- `sender` (str): Sender identifier
- `recipient` (str): Recipient phone number
- `message` (str): Message content
- `pdu_data` (bytes, optional): PDU data

**Returns:**
- `bool`: True if SMS sent successfully

##### `disconnect()`
Closes SIP connection

**Returns:**
- `bool`: True if disconnection successful

### Configuration Options

#### **SIP_SERVER Section**
- `host` (str): SIP server hostname or IP
- `port` (int): SIP server port (default: 5060)
- `transport` (str): Transport protocol (UDP/TCP/TLS)
- `use_tls` (bool): Enable TLS encryption
- `tls_port` (int): TLS port (default: 5061)

#### **AUTHENTICATION Section**
- `username` (str): SIP username/extension
- `password` (str): SIP password
- `domain` (str): SIP domain
- `realm` (str): Authentication realm

#### **CALLING_SETTINGS Section**
- `default_caller_id` (str): Default caller ID
- `max_call_duration` (int): Maximum call duration in seconds
- `enable_caller_id_spoofing` (bool): Enable caller ID modification

#### **SMS_SETTINGS Section**
- `use_sip_message` (bool): Use SIP MESSAGE method
- `use_call_with_sms` (bool): Send SMS via call with SMS
- `message_format` (str): Message format (plain/encoded)
- `max_message_length` (int): Maximum message length

#### **PBX_SETTINGS Section**
- `pbx_type` (str): PBX type (asterisk/freepbx/generic)
- `extension_pattern` (str): Extension pattern for PBX
- `outbound_proxy` (str): Outbound proxy server
- `register_expires` (int): Registration expiration time

#### **ADVANCED Section**
- `enable_nat_traversal` (bool): Enable NAT traversal
- `stun_server` (str): STUN server address
- `enable_early_media` (bool): Enable early media
- `dtmf_method` (str): DTMF method (rfc2833/info)

---

## Support and Contributing

### Getting Help

- **Documentation:** This README and PBX_SIP_INTEGRATION_SUMMARY.md
- **Testing:** Run `test_ghostcaller.py` for basic functionality tests
- **Configuration:** Check `sip_config.ini` for all configuration options

### Contributing

This is an educational project. When contributing:

1. Follow existing code style
2. Add appropriate documentation
3. Include test cases
4. Ensure backward compatibility

### Version History

- **v2.0** (2025-11-12): Added comprehensive PBX SIP integration
- **v1.0**: Original PDU construction functionality

---

**Important Notice:** This software is provided for educational purposes only. Users are responsible for complying with all applicable laws and regulations. The developers assume no liability for misuse of this software.