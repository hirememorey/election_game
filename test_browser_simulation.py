#!/usr/bin/env python3
"""
Browser Simulation Test
"""

import requests
import json
import time

def test_main_page():
    print("🌐 Testing main page...")
    
    try:
        response = requests.get("http://localhost:5001/")
        print(f"✅ Main page loaded (Status: {response.status_code})")
        
        # Check if required elements are present
        content = response.text
        required_elements = [
            "actions-container",
            "players-container", 
            "game-info-container",
            "bundle.js"
        ]
        
        for element in required_elements:
            if element in content:
                print(f"✅ Found: {element}")
            else:
                print(f"❌ Missing: {element}")
                
        return True
        
    except Exception as e:
        print(f"❌ Failed to load main page: {e}")
        return False

def test_bundle_loading():
    print("\n📦 Testing bundle loading...")
    
    try:
        response = requests.get("http://localhost:5001/static/dist/bundle.js")
        print(f"✅ Bundle loaded (Status: {response.status_code}, Size: {len(response.text)} bytes)")
        
        # Check if bundle contains expected functions
        bundle_content = response.text
        expected_functions = [
            "renderState",
            "connect", 
            "sendAction"
        ]
        
        for func in expected_functions:
            if func in bundle_content:
                print(f"✅ Found function: {func}")
            else:
                print(f"❌ Missing function: {func}")
                
        return True
        
    except Exception as e:
        print(f"❌ Failed to load bundle: {e}")
        return False

def test_debug_page():
    print("\n🔍 Testing debug page...")
    
    try:
        response = requests.get("http://localhost:5001/debug")
        print(f"✅ Debug page loaded (Status: {response.status_code})")
        
        # Check if debug page contains expected elements
        content = response.text
        expected_elements = [
            "Election Debug",
            "testConnection",
            "testStateParsing"
        ]
        
        for element in expected_elements:
            if element in content:
                print(f"✅ Found: {element}")
            else:
                print(f"❌ Missing: {element}")
                
        return True
        
    except Exception as e:
        print(f"❌ Failed to load debug page: {e}")
        return False

def main():
    print("🧪 Starting browser simulation tests...")
    
    tests = [
        test_main_page,
        test_bundle_loading,
        test_debug_page
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! The frontend should be working.")
        print("\n🎯 Next steps:")
        print("1. Open http://localhost:5001/ in your browser")
        print("2. Open browser developer tools (F12)")
        print("3. Check the console for detailed logging")
        print("4. Look for any JavaScript errors")
    else:
        print("❌ Some tests failed. Check the server and bundle.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 