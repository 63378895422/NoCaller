import binascii
import configparser
import os
from SIPClient import SIPClient
#NoCaller: an Android CallerID spoofer developed by Deccatron; if you are confused why sometimes the term GhostCaller is used, it's because I changed the corny-ass name to NoCaller...

def construct_pdu(sender, recipient, message):
    """Construct SMS PDU with proper validation"""
    try:
        # Input validation
        if not sender or not recipient or not message:
            print("Error: Invalid input parameters")
            return None
        if not isinstance(sender, str) or not isinstance(recipient, str) or not isinstance(message, str):
            print("Error: All parameters must be strings")
            return None
            
        sender_hex = binascii.hexlify(sender.encode()).decode()
        recipient_hex = binascii.hexlify(recipient.encode()).decode()
        message_hex = binascii.hexlify(message.encode()).decode()

        pdu_length = len(message_hex) // 2 + 13  # Length of message + 7 bytes for SMS-SUBMIT + 6 bytes for sender + 1 byte for message length

        pdu = (
            f'00'  # SMSC address length (0, which means the SMSC stored in the phone should be used)
            f'11'  # PDU Type (11 for SMS-SUBMIT)
            f'00'  # Message reference (arbitrary value)
            f'00{len(sender_hex) // 2:02X}'  # Sender address length (0 for alphanumeric, length of sender in octets)
            f'91{sender_hex}F'  # Sender address (91 prefix for international format)
            f'00'  # Protocol identifier
            f'00'  # Data coding scheme (0 for default 7-bit alphabet)
            f'{pdu_length:02X}'  # Length of message
            f'{recipient_hex}'  # Recipient address
            f'00'  # Validity period (not used in this example)
            f'00'  # User data header length (not used in this example)
            f'{message_hex}'  # Message
        )

        return pdu

    except Exception as e:
        print(f"Error constructing PDU: {e}")
        return None

def load_sip_config(config_file='sip_config.ini'):
    """Load SIP configuration from INI file"""
    config = configparser.ConfigParser()
    
    if not os.path.exists(config_file):
        print(f"Warning: SIP config file {config_file} not found. Using default values.")
        return {}
    
    try:
        config.read(config_file)
        sip_config = {
            'sip_server': config.get('SIP_SERVER', 'host', fallback='sip.example.com'),
            'sip_port': config.getint('SIP_SERVER', 'port', fallback=5060),
            'username': config.get('AUTHENTICATION', 'username', fallback='user'),
            'password': config.get('AUTHENTICATION', 'password', fallback='pass'),
            'domain': config.get('AUTHENTICATION', 'domain', fallback='example.com'),
            'use_tls': config.getboolean('SIP_SERVER', 'use_tls', fallback=False),
            'transport': config.get('SIP_SERVER', 'transport', fallback='UDP'),
        }
        return sip_config
    except Exception as e:
        print(f"Error loading SIP config: {e}. Using defaults.")
        return {}

def send_sms_via_sip(sender, recipient, message, sip_config=None):
    """Send SMS using SIP integration"""
    try:
        # Load SIP configuration
        if sip_config is None:
            sip_config = load_sip_config()
        
        # Construct PDU for the SMS
        pdu = construct_pdu(sender, recipient, message)
        if not pdu:
            print("Failed to construct PDU")
            return False
        
        # Initialize SIP client
        client = SIPClient(sip_config)
        
        # Connect and send
        if client.connect():
            success = client.send_sms_via_sip(sender, recipient, message, pdu)
            client.disconnect()
            return success
        else:
            print("Failed to connect to SIP server")
            return False
            
    except Exception as e:
        print(f"Error sending SMS via SIP: {e}")
        return False

def make_sip_call(caller_id, target_number, use_sip=True, sip_config=None):
    """Make a phone call with caller ID spoofing via SIP"""
    try:
        if not use_sip:
            print("Error: SIP calling requires use_sip=True")
            return False
            
        # Load SIP configuration
        if sip_config is None:
            sip_config = load_sip_config()
        
        # Initialize SIP client
        client = SIPClient(sip_config)
        
        # Connect and make call
        if client.connect():
            success = client.make_call(caller_id, target_number)
            client.disconnect()
            return success
        else:
            print("Failed to connect to SIP server")
            return False
            
    except Exception as e:
        print(f"Error making SIP call: {e}")
        return False

def main():
    """Enhanced main function with SIP support"""
    print("GhostCaller/NoCaller with PBX SIP Integration")
    print("=" * 50)
    
    # Load SIP configuration
    sip_config = load_sip_config()
    
    # Test basic PDU construction
    print("\n1. Testing PDU Construction...")
    sender = "CustomSender"
    recipient = "+1234567890"
    message = "Hello, this is a test message."
    
    pdu = construct_pdu(sender, recipient, message)
    if pdu:
        print(f"✓ PDU constructed: {len(pdu)} characters")
        print(f"  PDU: {pdu[:50]}...")
    else:
        print("✗ PDU construction failed")
        return
    
    # Test SIP integration (if configured)
    if sip_config and sip_config.get('sip_server') != 'sip.example.com':
        print("\n2. Testing SIP Integration...")
        
        # Test SMS via SIP
        print("   Testing SMS via SIP...")
        success = send_sms_via_sip(sender, recipient, message, sip_config)
        if success:
            print("   ✓ SMS sent via SIP")
        else:
            print("   ✗ SMS via SIP failed")
        
        # Test SIP call
        print("   Testing SIP call...")
        success = make_sip_call(sender, recipient, True, sip_config)
        if success:
            print("   ✓ SIP call initiated")
        else:
            print("   ✗ SIP call failed")
    else:
        print("\n2. SIP Integration (skipped - no valid configuration)")
        print("   Configure sip_config.ini with your SIP server details")
    
    print("\n" + "=" * 50)
    print("GhostCaller/NoCaller Enhanced with PBX SIP Support")

if __name__ == "__main__":
    main()
