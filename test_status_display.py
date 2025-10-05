#!/usr/bin/env python3
"""
Test script to verify status display functionality.
"""

import sys
import os
import time
import json
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from web.server import WebServer
from core.player_engine import PlayerEngine, PlaybackState

def test_status_display():
    """Test the status display functionality."""
    print("Testing status display functionality...")
    
    # Create web server
    web_server = WebServer(host='127.0.0.1', port=8081)
    
    # Start web server
    if not web_server.start():
        print("Failed to start web server")
        return False
    
    print(f"Web server started at {web_server.get_server_url()}")
    
    # Test different status updates
    test_cases = [
        ("Test Song 1", "Test Artist 1", "Playing", True),
        ("Test Song 2", "Test Artist 2", "Paused", False),
        ("Test Song 3", "Test Artist 3", "Stopped", False),
        ("No song playing", "Music Player", "Stopped", False)
    ]
    
    for title, artist, status, is_playing in test_cases:
        print(f"Testing status: {status}")
        web_server.update_song_data(
            title=title,
            artist=artist,
            artwork_url="/static/artwork/placeholder.jpg",
            is_playing=is_playing,
            status=status
        )
        
        # Verify the data was updated correctly
        current_data = web_server.current_song_data
        assert current_data['title'] == title, f"Title mismatch: {current_data['title']} != {title}"
        assert current_data['artist'] == artist, f"Artist mismatch: {current_data['artist']} != {artist}"
        assert current_data['status'] == status, f"Status mismatch: {current_data['status']} != {status}"
        assert current_data['is_playing'] == is_playing, f"Playing state mismatch: {current_data['is_playing']} != {is_playing}"
        
        print(f"✓ Status update successful: {status}")
        time.sleep(1)
    
    # Test configuration with show_status option
    print("\nTesting configuration with show_status option...")
    
    # Test GET config
    import requests
    try:
        response = requests.get(f"{web_server.get_server_url()}/api/config")
        if response.status_code == 200:
            config = response.json()
            print(f"Current config: {config}")
            
            # Verify show_status is in default config
            assert 'show_status' in config, "show_status not found in default config"
            print(f"✓ show_status in config: {config['show_status']}")
        else:
            print(f"Failed to get config: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error testing config API: {e}")
        return False
    
    # Test POST config with show_status
    try:
        test_config = {
            "font_family": "Arial",
            "font_size": 24,
            "background_color": "#000000",
            "text_color": "#ffffff",
            "show_status": False  # Test hiding status
        }
        
        response = requests.post(
            f"{web_server.get_server_url()}/api/config",
            json=test_config,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✓ Config update successful")
        else:
            print(f"Failed to update config: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error testing config update: {e}")
        return False
    
    # Stop web server
    web_server.stop()
    print("\n✓ All status display tests passed!")
    return True

def test_player_engine_status():
    """Test player engine status conversion."""
    print("\nTesting player engine status conversion...")
    
    # Import the status conversion function
    from main import MusicPlayerApp
    app = MusicPlayerApp()
    
    # Test status conversion
    test_states = [
        (PlaybackState.PLAYING, "Playing"),
        (PlaybackState.PAUSED, "Paused"),
        (PlaybackState.STOPPED, "Stopped"),
        (PlaybackState.LOADING, "Loading")
    ]
    
    for state, expected_status in test_states:
        actual_status = app._get_status_string(state)
        assert actual_status == expected_status, f"Status conversion failed: {actual_status} != {expected_status}"
        print(f"✓ {state.value} -> {actual_status}")
    
    print("✓ All status conversion tests passed!")
    return True

if __name__ == "__main__":
    print("Running status display tests...\n")
    
    success = True
    
    try:
        success &= test_player_engine_status()
        success &= test_status_display()
    except Exception as e:
        print(f"Test failed with error: {e}")
        success = False
    
    if success:
        print("\n🎉 All tests passed! Status display functionality is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)