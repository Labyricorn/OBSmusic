#!/usr/bin/env python3
"""
Simple test to verify progress bar functionality.
"""

import sys
import os
import time
import threading

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web.server import create_web_server

def test_progress_bar():
    """Test the progress bar with a simple setup."""
    
    # Create web server with debug mode
    server = create_web_server(debug_mode=True)
    
    if not server.start():
        print("Failed to start web server")
        return
    
    print(f"✅ Web server started at {server.get_server_url()}")
    print(f"🌐 Open {server.get_server_url()} in your browser")
    print("\n📊 Testing progress bar functionality...")
    
    # Wait a moment for server to fully start
    time.sleep(2)
    
    # Update song data to simulate a playing song
    server.update_song_data(
        title="Test Song for Progress Bar",
        artist="Test Artist",
        artwork_url="/static/artwork/placeholder.jpg",
        is_playing=True,
        status="Playing",
        audio_url="/api/audio/test_song_file.mp3"
    )
    
    print("✅ Song data updated")
    print("🎵 Current song: 'Test Song for Progress Bar' by Test Artist")
    print("▶️  Status: Playing")
    
    print("\n🔧 Progress bar should now be visible with these settings:")
    print("   - Position: bottom")
    print("   - Height: 4px")
    print("   - Background: #333333")
    print("   - Fill color: #ff6b6b")
    print("   - Border radius: 2px")
    
    print(f"\n📝 Instructions:")
    print(f"1. Open {server.get_server_url()} in your browser")
    print(f"2. You should see the progress bar at the bottom of the screen")
    print(f"3. If you have an audio file, the progress bar will update in real-time")
    print(f"4. Check the browser console (F12) for configuration logs")
    
    print(f"\n🎛️  To test different configurations, edit data/config.json")
    print(f"   Available positions: 'top', 'bottom', 'inline'")
    print(f"   Available colors: any hex color (e.g., '#4CAF50', '#2196F3')")
    
    try:
        input("\n⏸️  Press Enter to stop the server...")
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
    finally:
        server.stop()
        print("✅ Server stopped")

if __name__ == "__main__":
    test_progress_bar()