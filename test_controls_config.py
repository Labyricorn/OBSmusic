#!/usr/bin/env python3
"""
Test script to verify that the controls server configuration is working properly.
"""

import json
import os
import sys
import time
import threading
from web.controls_server import create_controls_server

def test_config_loading():
    """Test that configuration is loaded correctly."""
    print("Testing configuration loading...")
    
    # Create a test config
    test_config = {
        "background_color": "#000000",
        "player_background_color": "#ff0000",  # Red background
        "player_frame_fill_color": "rgba(0, 255, 0, 0.5)",  # Semi-transparent green
        "show_artwork": True,
        "artwork_size": 80,
        "layout": "horizontal",
        "show_status": False,
        "title": {
            "font_family": "Arial",
            "font_size": 32,
            "font_weight": "bold",
            "color": "#ffffff"
        },
        "artist": {
            "font_family": "Arial",
            "font_size": 24,
            "font_weight": "normal",
            "color": "#cccccc"
        }
    }
    
    # Save test config
    config_path = os.path.join('data', 'config.json')
    os.makedirs('data', exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(test_config, f, indent=2)
    
    print(f"Created test config at {config_path}")
    
    # Create controls server
    server = create_controls_server(port=8082)  # Use different port for testing
    
    # Check if config was loaded correctly
    print(f"Loaded config: {server.config}")
    
    # Verify specific values
    assert server.config.get('player_background_color') == '#ff0000', "player_background_color not loaded correctly"
    assert server.config.get('player_frame_fill_color') == 'rgba(0, 255, 0, 0.5)', "player_frame_fill_color not loaded correctly"
    
    print("✅ Configuration loading test passed!")
    
    # Start server briefly to test template rendering
    print("Starting controls server for template test...")
    if server.start():
        print(f"✅ Controls server started at {server.get_server_url()}")
        print("You can test the configuration by opening the URL in your browser.")
        print("The background should be red and the controls container should have a green tint.")
        print("Press Ctrl+C to stop the test server...")
        
        try:
            while server.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping test server...")
            server.stop()
    else:
        print("❌ Failed to start controls server")
        return False
    
    return True

if __name__ == '__main__':
    try:
        success = test_config_loading()
        if success:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)