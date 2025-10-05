#!/usr/bin/env python3
"""
Simple test script to verify configuration web interface functionality.
"""

import requests
import json
import time
import threading
from web.server import WebServer
from core.config_manager import ConfigManager, WebDisplayConfig


def test_config_interface():
    """Test the configuration web interface functionality."""
    print("Testing Configuration Web Interface...")
    
    # Start web server
    server = WebServer(host='127.0.0.1', port=8080)
    if not server.start():
        print("❌ Failed to start web server")
        return False
    
    try:
        time.sleep(2)  # Wait for server to start
        base_url = f"http://127.0.0.1:{server.port}"
        
        # Test 1: GET /api/config returns default configuration
        print("\n1. Testing GET /api/config...")
        response = requests.get(f"{base_url}/api/config")
        if response.status_code == 200:
            config = response.json()
            print(f"✅ Default config loaded: {config['font_family']}, {config['font_size']}px")
        else:
            print(f"❌ Failed to get config: {response.status_code}")
            return False
        
        # Test 2: POST /api/config with valid data
        print("\n2. Testing POST /api/config...")
        new_config = {
            'font_family': 'Helvetica',
            'font_size': 32,
            'font_weight': 'bold',
            'background_color': '#ff0000',
            'text_color': '#00ff00',
            'show_artwork': False,
            'layout': 'vertical'
        }
        
        response = requests.post(
            f"{base_url}/api/config",
            json=new_config,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Configuration saved successfully")
            else:
                print(f"❌ Save failed: {result}")
                return False
        else:
            print(f"❌ POST failed: {response.status_code}")
            return False
        
        # Test 3: Verify configuration was saved
        print("\n3. Testing configuration persistence...")
        response = requests.get(f"{base_url}/api/config")
        if response.status_code == 200:
            saved_config = response.json()
            if (saved_config['font_family'] == 'Helvetica' and 
                saved_config['font_size'] == 32 and
                saved_config['layout'] == 'vertical'):
                print("✅ Configuration persisted correctly")
            else:
                print(f"❌ Configuration not saved correctly: {saved_config}")
                return False
        else:
            print(f"❌ Failed to verify saved config: {response.status_code}")
            return False
        
        # Test 4: Test configuration page loads
        print("\n4. Testing configuration page...")
        response = requests.get(f"{base_url}/config")
        if response.status_code == 200 and 'text/html' in response.headers.get('content-type', ''):
            print("✅ Configuration page loads successfully")
        else:
            print(f"❌ Configuration page failed: {response.status_code}")
            return False
        
        # Test 5: Test invalid JSON handling
        print("\n5. Testing invalid JSON handling...")
        response = requests.post(
            f"{base_url}/api/config",
            data="invalid json",
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 400:
            print("✅ Invalid JSON properly rejected")
        else:
            print(f"❌ Invalid JSON not handled correctly: {response.status_code}")
            return False
        
        # Test 6: Test configuration validation
        print("\n6. Testing configuration validation...")
        config_manager = ConfigManager(config_file="data/test_config.json")
        
        invalid_config = {
            'background_color': 'invalid_color',
            'font_size': -10,
            'layout': 'invalid_layout'
        }
        
        validated_config = WebDisplayConfig.from_dict(invalid_config)
        if (validated_config.background_color == '#000000' and  # Default
            validated_config.font_size == 24 and  # Default
            validated_config.layout == 'horizontal'):  # Default
            print("✅ Configuration validation works correctly")
        else:
            print(f"❌ Configuration validation failed: {validated_config}")
            return False
        
        print("\n🎉 All configuration interface tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    finally:
        server.stop()


if __name__ == '__main__':
    success = test_config_interface()
    exit(0 if success else 1)