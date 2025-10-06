#!/usr/bin/env python3
"""
Test to verify progress bar floats properly inside the frame.
"""

import sys
import os
import time
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web.server import create_web_server

def test_frame_progress_positioning():
    """Test that progress bar floats inside the frame correctly."""
    
    # Create web server with debug mode
    server = create_web_server(debug_mode=True)
    
    if not server.start():
        print("Failed to start web server")
        return
    
    print(f"✅ Web server started at {server.get_server_url()}")
    print(f"🌐 Open {server.get_server_url()} in your browser")
    print("\n🧪 Testing progress bar positioning inside frame...")
    
    # Wait a moment for server to fully start
    time.sleep(2)
    
    # Update song data
    server.update_song_data(
        title="Frame Position Test",
        artist="Test Artist",
        artwork_url="/static/artwork/placeholder.jpg",
        is_playing=True,
        status="Playing",
        audio_url="/api/audio/test_song_file.mp3"
    )
    
    # Test different frame configurations
    test_configs = [
        {
            "name": "Default Frame with Bottom Progress Bar",
            "config": {
                "font_family": "Arial",
                "font_size": 24,
                "background_color": "#000000",
                "text_color": "#ffffff",
                "show_artwork": True,
                "artwork_size": 200,
                "layout": "horizontal",
                "show_status": True,
                "progress_bar": {
                    "show": True,
                    "position": "bottom",
                    "width": 80,
                    "height": 6,
                    "spacing": 20,
                    "background_color": "#333333",
                    "fill_color": "#ff6b6b",
                    "border_radius": 3
                },
                "frame": {
                    "show": True,
                    "thickness": 2,
                    "corner_radius": 10,
                    "frame_color": "#ffffff",
                    "fill_color": "transparent"
                }
            }
        },
        {
            "name": "Thick Frame with Top Progress Bar",
            "config": {
                "font_family": "Arial",
                "font_size": 24,
                "background_color": "#000000",
                "text_color": "#ffffff",
                "show_artwork": True,
                "artwork_size": 200,
                "layout": "horizontal",
                "show_status": True,
                "progress_bar": {
                    "show": True,
                    "position": "top",
                    "width": 90,
                    "height": 8,
                    "spacing": 30,
                    "background_color": "#222222",
                    "fill_color": "#4CAF50",
                    "border_radius": 4
                },
                "frame": {
                    "show": True,
                    "thickness": 8,
                    "corner_radius": 20,
                    "frame_color": "#FFD700",
                    "fill_color": "#1a1a1a"
                }
            }
        },
        {
            "name": "Minimal Frame with Inline Progress Bar",
            "config": {
                "font_family": "Arial",
                "font_size": 24,
                "background_color": "#000000",
                "text_color": "#ffffff",
                "show_artwork": True,
                "artwork_size": 200,
                "layout": "vertical",
                "show_status": True,
                "progress_bar": {
                    "show": True,
                    "position": "inline",
                    "width": 70,
                    "height": 4,
                    "spacing": 15,
                    "background_color": "#444444",
                    "fill_color": "#2196F3",
                    "border_radius": 2
                },
                "frame": {
                    "show": True,
                    "thickness": 1,
                    "corner_radius": 5,
                    "frame_color": "#888888",
                    "fill_color": "transparent"
                }
            }
        }
    ]
    
    try:
        for i, test_case in enumerate(test_configs):
            print(f"\n🧪 Test {i+1}: {test_case['name']}")
            
            # Save configuration to file
            config_path = Path('data/config.json')
            config_path.parent.mkdir(exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(test_case['config'], f, indent=2)
            
            # Emit configuration update via WebSocket
            server.socketio.emit('config_updated', test_case['config'])
            
            progress_config = test_case['config']['progress_bar']
            frame_config = test_case['config']['frame']
            
            print(f"   📊 Progress Bar:")
            print(f"      - Position: {progress_config['position']}")
            print(f"      - Width: {progress_config['width']}%")
            print(f"      - Spacing: {progress_config['spacing']}px")
            print(f"   🖼️  Frame:")
            print(f"      - Thickness: {frame_config['thickness']}px")
            print(f"      - Corner Radius: {frame_config['corner_radius']}px")
            print(f"      - Frame Color: {frame_config['frame_color']}")
            print(f"      - Fill Color: {frame_config['fill_color']}")
            
            print(f"\n   ✅ Expected Result:")
            if progress_config['position'] == 'bottom':
                print(f"      - Progress bar should float {progress_config['spacing']}px above the frame bottom edge")
            elif progress_config['position'] == 'top':
                print(f"      - Progress bar should float {progress_config['spacing']}px below the frame top edge")
            else:
                print(f"      - Progress bar should be inline with {progress_config['spacing']}px margin")
            
            input("   ⏸️  Press Enter to continue to next test...")
        
        print(f"\n🎉 All positioning tests completed!")
        print(f"\n📝 What you should have observed:")
        print(f"1. Progress bar always stays inside the frame boundaries")
        print(f"2. Progress bar respects both frame margin AND spacing configuration")
        print(f"3. Different frame thicknesses don't affect progress bar positioning")
        print(f"4. Progress bar maintains proper distance from frame edges")
        
        input("\n⏸️  Press Enter to stop the server...")
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
    finally:
        server.stop()
        print("✅ Server stopped")

if __name__ == "__main__":
    test_frame_progress_positioning()