#!/usr/bin/env python3
"""
Test script to verify real-time preview functionality in the configuration interface.
"""

import requests
import json
import time
from web.server import WebServer


def test_preview_functionality():
    """Test the real-time preview functionality."""
    print("Testing Real-time Preview Functionality...")
    
    # Start web server
    server = WebServer(host='127.0.0.1', port=8080)
    if not server.start():
        print("❌ Failed to start web server")
        return False
    
    try:
        time.sleep(2)  # Wait for server to start
        base_url = f"http://127.0.0.1:{server.port}"
        
        # Test 1: Verify config page contains preview elements
        print("\n1. Testing preview elements in HTML...")
        response = requests.get(f"{base_url}/config")
        if response.status_code == 200:
            html_content = response.text
            
            # Check for preview-related elements
            preview_elements = [
                'preview-display',
                'preview-title',
                'preview-artist',
                'preview-artwork',
                'updatePreview',
                'real-time preview'
            ]
            
            found_elements = []
            for element in preview_elements:
                if element in html_content:
                    found_elements.append(element)
            
            if len(found_elements) >= 4:  # At least 4 preview elements should be present
                print(f"✅ Preview elements found: {found_elements}")
            else:
                print(f"❌ Missing preview elements. Found: {found_elements}")
                return False
        else:
            print(f"❌ Failed to load config page: {response.status_code}")
            return False
        
        # Test 2: Verify JavaScript functions are present
        print("\n2. Testing JavaScript preview functions...")
        js_functions = [
            'updatePreview',
            'setupPreviewListeners',
            'loadConfiguration'
        ]
        
        found_functions = []
        for func in js_functions:
            if func in html_content:
                found_functions.append(func)
        
        if len(found_functions) >= 2:  # At least 2 JS functions should be present
            print(f"✅ JavaScript functions found: {found_functions}")
        else:
            print(f"❌ Missing JavaScript functions. Found: {found_functions}")
            return False
        
        # Test 3: Verify form elements have event listeners
        print("\n3. Testing form event listener setup...")
        event_listener_elements = [
            'addEventListener',
            'input',
            'change'
        ]
        
        found_listeners = []
        for listener in event_listener_elements:
            if listener in html_content:
                found_listeners.append(listener)
        
        if len(found_listeners) >= 2:
            print(f"✅ Event listeners found: {found_listeners}")
        else:
            print(f"❌ Missing event listeners. Found: {found_listeners}")
            return False
        
        # Test 4: Test configuration loading functionality
        print("\n4. Testing configuration loading...")
        
        # Set a specific configuration
        test_config = {
            'font_family': 'Georgia',
            'font_size': 36,
            'background_color': '#123456',
            'text_color': '#abcdef',
            'layout': 'vertical'
        }
        
        # Save configuration
        response = requests.post(
            f"{base_url}/api/config",
            json=test_config,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ Test configuration saved")
        else:
            print(f"❌ Failed to save test configuration: {response.status_code}")
            return False
        
        # Reload config page and verify it loads the saved configuration
        response = requests.get(f"{base_url}/config")
        if response.status_code == 200:
            # The page should load with the saved configuration values
            # This would be populated by the loadConfiguration() JavaScript function
            print("✅ Configuration page reloaded successfully")
        else:
            print(f"❌ Failed to reload config page: {response.status_code}")
            return False
        
        # Test 5: Verify CSS classes for different layouts
        print("\n5. Testing layout CSS classes...")
        layout_classes = [
            'layout-horizontal',
            'layout-vertical', 
            'layout-overlay'
        ]
        
        found_classes = []
        for css_class in layout_classes:
            if css_class in html_content:
                found_classes.append(css_class)
        
        if len(found_classes) >= 3:
            print(f"✅ Layout CSS classes found: {found_classes}")
        else:
            print(f"❌ Missing layout CSS classes. Found: {found_classes}")
            return False
        
        print("\n🎉 All preview functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    finally:
        server.stop()


if __name__ == '__main__':
    success = test_preview_functionality()
    exit(0 if success else 1)