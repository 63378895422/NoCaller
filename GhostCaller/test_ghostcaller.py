#!/usr/bin/env python3
"""
Test script for GhostCaller/NoCaller PDU construction functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from GhostCaller import construct_pdu

def test_basic_functionality():
    """Test basic PDU construction"""
    print("=== Testing Basic Functionality ===")
    
    sender = "CustomSender"
    recipient = "+1234567890"
    message = "Hello, this is a test message."
    
    pdu = construct_pdu(sender, recipient, message)
    
    if pdu:
        print(f"✓ Basic test passed")
        print(f"PDU: {pdu}")
        print(f"PDU Length: {len(pdu)} characters")
        return True
    else:
        print(f"✗ Basic test failed")
        return False

def test_different_inputs():
    """Test with various input combinations"""
    print("\n=== Testing Different Input Scenarios ===")
    
    test_cases = [
        # (sender, recipient, message, description)
        ("TestUser", "+15551234567", "Short message", "Standard case"),
        ("1234567890", "+1234567890", "A" * 50, "Long message"),
        ("Admin", "+15550000001", "", "Empty message"),
        ("Üser", "+15550000002", "Message with ünicode", "Unicode characters"),
        ("A" * 20, "+15550000003", "Maximum sender length", "Long sender name"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for sender, recipient, message, description in test_cases:
        try:
            pdu = construct_pdu(sender, recipient, message)
            if pdu:
                print(f"✓ {description}: PDU constructed successfully ({len(pdu)} chars)")
                passed += 1
            else:
                print(f"✗ {description}: Failed to construct PDU")
        except Exception as e:
            print(f"✗ {description}: Exception occurred - {e}")
    
    print(f"Input tests: {passed}/{total} passed")
    return passed == total

def test_error_handling():
    """Test error handling with invalid inputs"""
    print("\n=== Testing Error Handling ===")
    
    error_cases = [
        (None, "+1234567890", "message", "None sender"),
        ("sender", None, "message", "None recipient"),
        ("sender", "+1234567890", None, "None message"),
        ("", "", "", "Empty strings"),
        (123, "+1234567890", "message", "Non-string sender"),
        ("sender", 123, "message", "Non-string recipient"),
    ]
    
    handled_correctly = 0
    total = len(error_cases)
    
    for sender, recipient, message, description in error_cases:
        try:
            pdu = construct_pdu(sender, recipient, message)
            if pdu is None:
                print(f"✓ {description}: Correctly returned None for invalid input")
                handled_correctly += 1
            else:
                print(f"✗ {description}: Should have returned None but got: {pdu[:50]}...")
        except Exception as e:
            print(f"✗ {description}: Exception should be caught internally, got: {e}")
    
    print(f"Error handling tests: {handled_correctly}/{total} passed")
    return handled_correctly == total

def validate_pdu_structure(pdu):
    """Validate the structure of generated PDU"""
    print("\n=== Validating PDU Structure ===")
    
    if not pdu or len(pdu) < 10:
        return False
    
    # Check header structure
    expected_start = "00"  # SMSC length
    expected_type = "11"   # SMS-SUBMIT
    
    if not pdu.startswith(expected_start):
        print(f"✗ Invalid SMSC header: expected {expected_start}, got {pdu[:2]}")
        return False
    
    if pdu[2:4] != expected_type:
        print(f"✗ Invalid PDU type: expected {expected_type}, got {pdu[2:4]}")
        return False
    
    print("✓ PDU header structure is valid")
    print(f"  - SMSC length: {pdu[0:2]} (0 = use phone's SMSC)")
    print(f"  - PDU type: {pdu[2:4]} (11 = SMS-SUBMIT)")
    print(f"  - Message reference: {pdu[4:6]}")
    print(f"  - Full PDU length: {len(pdu)} characters")
    
    return True

def main():
    """Run all tests"""
    print("GhostCaller/NoCaller Functionality Test Suite")
    print("=" * 50)
    
    results = {
        'basic': test_basic_functionality(),
        'inputs': test_different_inputs(),
        'errors': test_error_handling(),
    }
    
    # Test PDU structure validation
    pdu = construct_pdu("TestUser", "+15551234567", "Test message")
    results['structure'] = validate_pdu_structure(pdu)
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {test_name.title()}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nOverall: {total_passed}/{total_tests} test suites passed")
    
    if total_passed == total_tests:
        print("🎉 All tests passed! The GhostCaller functionality is working correctly.")
    else:
        print("⚠️  Some tests failed. Review the output above for details.")
    
    return total_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)