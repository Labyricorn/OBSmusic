#!/usr/bin/env python3
"""
Test script to demonstrate the progress bar functionality.
This script will start the web server and simulate song playback with progress updates.
"""

import sys
import os
import time
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web.server import create_web_server

def test_progress_bar_configurations():
    """Test different progress bar configurations."""
    
    # Create web server
    server = create_web_server(debug_mode=True)
    
    if not server.start():
        print("Failed to start web server")
        return
    
    print(f"Web server started at {server.get_server_url()}")
    print("Open the URL in your browser to see the progress bar")
    print("\nTesting different progress bar configurations...")
    
    # Test configurations
    configs = [
        {
            "name": "Floating Bottom Progress Bar (Default 80% width)",
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
            "name": "Full Width Top Progress Bar with Thick Gold Frame",
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
                    "width": 100,
                    "height": 6,
                    "spacing": 0,
                    "background_color": "#222222",
                    "fill_color": "#4CAF50",
                    "border_radius": 0
                },
                "frame": {
                    "show": True,
                    "thickness": 5,
                    "corner_radius": 15,
                    "frame_color": "#FFD700",
                    "fill_color": "#1a1a1a"
                }
            }
        },
        {
            "name": "Narrow Progress Bar with Minimal Rounded Frame",
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
                    "width": 50,
                    "height": 8,
                    "spacing": 40,
                    "background_color": "#444444",
                    "fill_color": "#2196F3",
                    "border_radius": 4
                },
                "frame": {
                    "show": True,
                    "thickness": 1,
                    "corner_radius": 20,
                    "frame_color": "#888888",
                    "fill_color": "transparent"
                }
            }
        },
        {
            "name": "Inline Progress Bar with Gaming Frame",
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
                    "width": 90,
                    "height": 10,
                    "spacing": 15,
                    "background_color": "#1a1a1a",
                    "fill_color": "#ff9800",
                    "border_radius": 5
                },
                "frame": {
                    "show": True,
                    "thickness": 3,
                    "corner_radius": 0,
                    "frame_color": "#00ff00",
                    "fill_color": "#001100"
                }
            }
        },
        {
            "name": "Minimal Setup with Subtle Frame",
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
                    "width": 60,
                    "height": 2,
                    "spacing": 5,
                    "background_color": "#555555",
                    "fill_color": "#ffffff",
                    "border_radius": 1
                },
                "frame": {
                    "show": True,
                    "thickness": 1,
                    "corner_radius": 5,
                    "frame_color": "#444444",
                    "fill_color": "transparent"
                }
            }
        },
        {
            "name": "No Frame, No Progress Bar (Clean)",
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
                    "show": False,
                    "position": "bottom",
                    "width": 80,
                    "height": 6,
                    "spacing": 20,
                    "background_color": "#333333",
                    "fill_color": "#ff6b6b",
                    "border_radius": 3
                },
                "frame": {
                    "show": False,
                    "thickness": 2,
                    "corner_radius": 10,
                    "frame_color": "#ffffff",
                    "fill_color": "transparent"
                }
            }
        }
    ]
    
    try:
        # Update song data to simulate playback
        server.update_song_data(
            title="Test Song",
            artist="Test Artist",
            artwork_url="/static/artwork/placeholder.jpg",
            is_playing=True,
            status="Playing",
            audio_url="/api/audio/test_song_file.mp3"
        )
        
        for i, test_case in enumerate(configs):
            print(f"\n{i+1}. Testing: {test_case['name']}")
            
            # Save configuration to file
            config_path = Path('data/config.json')
            config_path.parent.mkdir(exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(test_case['config'], f, indent=2)
            
            # Emit configuration update via WebSocket
            server.socketio.emit('config_updated', test_case['config'])
            
            print(f"   Progress Bar:")
            print(f"     - Position: {test_case['config']['progress_bar']['position']}")
            print(f"     - Width: {test_case['config']['progress_bar']['width']}%")
            print(f"     - Height: {test_case['config']['progress_bar']['height']}px")
            print(f"     - Spacing: {test_case['config']['progress_bar']['spacing']}px")
            print(f"     - Fill Color: {test_case['config']['progress_bar']['fill_color']}")
            print(f"     - Visible: {test_case['config']['progress_bar']['show']}")
            print(f"   Frame:")
            print(f"     - Show: {test_case['config']['frame']['show']}")
            print(f"     - Thickness: {test_case['config']['frame']['thickness']}px")
            print(f"     - Corner Radius: {test_case['config']['frame']['corner_radius']}px")
            print(f"     - Frame Color: {test_case['config']['frame']['frame_color']}")
            print(f"     - Fill Color: {test_case['config']['frame']['fill_color']}")
            
            # Wait for user to see the changes
            input("   Press Enter to continue to next configuration...")
        
        print(f"\nAll configurations tested!")
        print(f"You can now manually test the progress bar by:")
        print(f"1. Opening {server.get_server_url()} in your browser")
        print(f"2. Playing an audio file through the music player")
        print(f"3. Observing the progress bar update in real-time")
        print(f"\nConfiguration options available:")
        print(f"Progress Bar:")
        print(f"- show: true/false (show or hide the progress bar)")
        print(f"- position: 'top', 'bottom', or 'inline'")
        print(f"- width: number (width as percentage of screen, 1-100)")
        print(f"- height: number (height in pixels)")
        print(f"- spacing: number (distance from edges/margin in pixels)")
        print(f"- background_color: hex color (e.g., '#333333')")
        print(f"- fill_color: hex color (e.g., '#ff6b6b')")
        print(f"- border_radius: number (border radius in pixels)")
        print(f"Frame:")
        print(f"- show: true/false (show or hide the frame)")
        print(f"- thickness: number (frame border thickness in pixels)")
        print(f"- corner_radius: number (frame corner radius in pixels)")
        print(f"- frame_color: hex color (e.g., '#ffffff')")
        print(f"- fill_color: hex color or 'transparent' (background fill)")
        
        input("\nPress Enter to stop the server...")
        
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.stop()

if __name__ == "__main__":
    test_progress_bar_configurations()