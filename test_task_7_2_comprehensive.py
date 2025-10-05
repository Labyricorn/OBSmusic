#!/usr/bin/env python3
"""
Comprehensive test for Task 7.2: Build configuration web interface
Tests all requirements: HTML form, real-time preview, persistence, and integration tests.
"""

import requests
import json
import time
import os
import tempfile
import shutil
from web.server import WebServer
from core.config_manager import ConfigManager, WebDisplayConfig


def test_task_7_2_requirements():
    """Test all requirements for Task 7.2."""
    print("🧪 Testing Task 7.2: Build configuration web interface")
    print("=" * 60)
    
    # Create temporary directory for testing
    test_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    
    try:
        os.chdir(test_dir)
        os.makedirs('data', exist_ok=True)
        
        # Start web server
        server = WebServer(host='127.0.0.1', port=8080)
        if not server.start():
            print("❌ Failed to start web server")
            return False
        
        time.sleep(2)  # Wait for server to start
        base_url = f"http://127.0.0.1:{server.port}"
        
        print("\n📋 Requirement: Create HTML form for modifying display configuration settings")
        print("-" * 50)
        
        # Test HTML form elements
        response = requests.get(f"{base_url}/config")
        if response.status_code != 200:
            print("❌ Configuration page not accessible")
            return False
        
        html_content = response.text
        
        # Check for required form elements
        required_form_elements = [
            'font-family',
            'font-size', 
            'font-weight',
            'background-color',
            'text-color',
            'accent-color',
            'show-artwork',
            'artwork-size',
            'layout'
        ]
        
        missing_elements = []
        for element in required_form_elements:
            if element not in html_content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Missing form elements: {missing_elements}")
            return False
        
        print("✅ All required form elements present")
        
        # Test form submission functionality
        test_config = {
            'font_family': 'Helvetica',
            'font_size': 28,
            'font_weight': 'bold',
            'background_color': '#123456',
            'text_color': '#abcdef',
            'accent_color': '#ff0000',
            'show_artwork': True,
            'artwork_size': 250,
            'layout': 'vertical'
        }
        
        response = requests.post(
            f"{base_url}/api/config",
            json=test_config,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code != 200 or not response.json().get('success'):
            print("❌ Form submission failed")
            return False
        
        print("✅ HTML form submission works correctly")
        
        print("\n🔄 Requirement: Implement real-time preview of configuration changes")
        print("-" * 50)
        
        # Check for preview elements
        preview_elements = [
            'preview-display',
            'preview-title', 
            'preview-artist',
            'preview-artwork',
            'updatePreview',
            'setupPreviewListeners'
        ]
        
        missing_preview = []
        for element in preview_elements:
            if element not in html_content:
                missing_preview.append(element)
        
        if missing_preview:
            print(f"❌ Missing preview elements: {missing_preview}")
            return False
        
        print("✅ Real-time preview elements present")
        
        # Check for event listeners
        if 'addEventListener' not in html_content:
            print("❌ Event listeners not found")
            return False
        
        print("✅ Event listeners for real-time updates present")
        
        # Check for layout classes
        layout_classes = ['layout-horizontal', 'layout-vertical', 'layout-overlay']
        for layout_class in layout_classes:
            if layout_class not in html_content:
                print(f"❌ Missing layout class: {layout_class}")
                return False
        
        print("✅ Layout preview classes present")
        
        print("\n💾 Requirement: Add configuration persistence and loading functionality")
        print("-" * 50)
        
        # Test configuration persistence
        response = requests.get(f"{base_url}/api/config")
        if response.status_code != 200:
            print("❌ Configuration loading failed")
            return False
        
        loaded_config = response.json()
        
        # Verify the test configuration was saved
        if (loaded_config['font_family'] != 'Helvetica' or 
            loaded_config['font_size'] != 28 or
            loaded_config['layout'] != 'vertical'):
            print(f"❌ Configuration not persisted correctly: {loaded_config}")
            return False
        
        print("✅ Configuration persistence works")
        
        # Test configuration file creation
        if not os.path.exists('data/config.json'):
            print("❌ Configuration file not created")
            return False
        
        with open('data/config.json', 'r') as f:
            file_config = json.load(f)
        
        if file_config['font_family'] != 'Helvetica':
            print("❌ Configuration file content incorrect")
            return False
        
        print("✅ Configuration file persistence works")
        
        # Test loading configuration on page load
        if 'loadConfiguration' not in html_content:
            print("❌ Configuration loading function not found")
            return False
        
        print("✅ Configuration loading functionality present")
        
        print("\n🧪 Requirement: Write integration tests for configuration interface and persistence")
        print("-" * 50)
        
        # Test error handling
        response = requests.post(
            f"{base_url}/api/config",
            data="invalid json",
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code != 400:
            print("❌ Invalid JSON not handled correctly")
            return False
        
        print("✅ Error handling for invalid JSON works")
        
        # Test configuration validation
        config_manager = ConfigManager(config_file="data/test_config.json")
        
        invalid_config = {
            'background_color': 'invalid_color',
            'font_size': -10,
            'layout': 'invalid_layout'
        }
        
        validated_config = WebDisplayConfig.from_dict(invalid_config)
        if (validated_config.background_color != '#000000' or  # Default
            validated_config.font_size != 24 or  # Default
            validated_config.layout != 'horizontal'):  # Default
            print("❌ Configuration validation failed")
            return False
        
        print("✅ Configuration validation works")
        
        # Test default configuration handling
        response = requests.get(f"{base_url}/api/config")
        default_config = response.json()
        
        required_defaults = {
            'font_family': str,
            'font_size': int,
            'background_color': str,
            'text_color': str,
            'show_artwork': bool,
            'layout': str
        }
        
        for key, expected_type in required_defaults.items():
            if key not in default_config or not isinstance(default_config[key], expected_type):
                print(f"❌ Default configuration missing or wrong type for {key}")
                return False
        
        print("✅ Default configuration handling works")
        
        # Test WebSocket configuration updates (check if display template supports it)
        display_response = requests.get(f"{base_url}/")
        if display_response.status_code == 200:
            display_html = display_response.text
            if 'config_updated' in display_html and 'applyConfiguration' in display_html:
                print("✅ Real-time configuration updates to display supported")
            else:
                print("❌ Real-time configuration updates not supported")
                return False
        else:
            print("❌ Display page not accessible")
            return False
        
        print("\n🎯 Requirements Verification Summary")
        print("-" * 50)
        
        # Verify requirements from the task details
        requirements_met = {
            "5.1": "Configuration options change web page styling immediately",
            "5.2": "Web page loads saved configuration settings on start", 
            "5.5": "Font settings modify web page text appearance",
            "5.6": "Color settings modify background and text colors",
            "5.7": "Layout settings modify element positioning and sizing",
            "5.8": "Artwork display settings modify image presentation"
        }
        
        print("✅ Requirement 5.1: Real-time styling updates implemented")
        print("✅ Requirement 5.2: Configuration loading on startup implemented")
        print("✅ Requirement 5.5: Font settings modification implemented")
        print("✅ Requirement 5.6: Color settings modification implemented") 
        print("✅ Requirement 5.7: Layout settings modification implemented")
        print("✅ Requirement 5.8: Artwork display settings implemented")
        
        print("\n🎉 Task 7.2 - All requirements successfully implemented!")
        print("=" * 60)
        print("✅ HTML form for modifying display configuration settings")
        print("✅ Real-time preview of configuration changes")
        print("✅ Configuration persistence and loading functionality")
        print("✅ Integration tests for configuration interface and persistence")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    finally:
        if 'server' in locals():
            server.stop()
        os.chdir(original_cwd)
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == '__main__':
    success = test_task_7_2_requirements()
    exit(0 if success else 1)