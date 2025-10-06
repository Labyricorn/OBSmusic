#!/usr/bin/env python3
"""
Simple test to verify frame functionality.
"""

import sys
import os
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web.server import create_web_server

def test_frame():
    """Test the frame with a simple setup."""
    
    # Create web server with debug mode
    server = create_web_server(debug_mode=True)
    
    if not server.start():
        print("Failed to start web server")
        return
    
    print(f"✅ Web server started at {server.get_server_url()}")
    print(f"🌐 Open {server.get_server_url()} in your browser")
    print("\n🖼️  Testing frame functionality...")
    
    # Wait a moment for server to fully start
    time.sleep(2)
    
    # Update song data to simulate a playing song
    server.update_song_data(
        title="Test Song with Frame",
        artist="Test Artist",
        artwork_url="/static/artwork/placeholder.jpg",
        is_playing=True,
        status="Playing",
        audio_url="/api/audio/test_song_file.mp3"
    )
    
    print("✅ Song data updated")
    print("🎵 Current song: 'Test Song with Frame' by Test Artist")
    print("▶️  Status: Playing")
    
    print("\n🖼️  Frame should now be visible with these settings:")
    print("   - Show: true")
    print("   - Thickness: 2px")
    print("   - Corner radius: 10px")
    print("   - Frame color: #ffffff (white)")
    print("   - Fill color: transparent")
    
    print("\n📊 Progress bar should also be visible:")
    print("   - Position: bottom")
    print("   - Width: 80%")
    print("   - Height: 6px")
    print("   - Spacing: 20px from bottom")
    
    print(f"\n📝 What you should see:")
    print(f"1. A white frame border around the entire display")
    print(f"2. The frame has rounded corners (10px radius)")
    print(f"3. The progress bar floats inside the frame at the bottom")
    print(f"4. All elements (song info, artwork, progress bar) are contained within the frame")
    
    print(f"\n🎛️  To test different frame styles, edit data/config.json:")
    print(f"   Frame colors: '#FFD700' (gold), '#00ff00' (green), '#ff0000' (red)")
    print(f"   Fill colors: '#1a1a1a' (dark), '#001100' (dark green), 'transparent'")
    print(f"   Thickness: 1-10 pixels")
    print(f"   Corner radius: 0 (sharp), 5-20 (rounded)")
    
    try:
        input("\n⏸️  Press Enter to stop the server...")
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
    finally:
        server.stop()
        print("✅ Server stopped")

if __name__ == "__main__":
    test_frame()