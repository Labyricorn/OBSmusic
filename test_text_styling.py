#!/usr/bin/env python3
"""
Test script to demonstrate separate title and artist text styling.
"""

import sys
import os
import time
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web.server import create_web_server

def test_text_styling():
    """Test different title and artist text styling configurations."""
    
    # Create web server
    server = create_web_server(debug_mode=True)
    
    if not server.start():
        print("Failed to start web server")
        return
    
    print(f"✅ Web server started at {server.get_server_url()}")
    print(f"🌐 Open {server.get_server_url()} in your browser")
    print("\n🎨 Testing title and artist text styling...")
    
    # Wait a moment for server to fully start
    time.sleep(2)
    
    # Update song data to simulate playback
    server.update_song_data(
        title="Beautiful Song Title",
        artist="Amazing Artist Name",
        artwork_url="/static/artwork/placeholder.jpg",
        is_playing=True,
        status="Playing",
        audio_url="/api/audio/test_song_file.mp3"
    )
    
    print("✅ Song data updated")
    print("🎵 Current song: 'Beautiful Song Title' by Amazing Artist Name")
    
    # Test configurations
    configs = [
        {
            "name": "Default Styling (Bold Title, Normal Artist)",
            "config": {
                "font_family": "Arial",
                "font_size": 16,
                "background_color": "#000000",
                "text_color": "#ffffff",
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
                },
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
            "name": "Elegant Serif Styling",
            "config": {
                "font_family": "Arial",
                "font_size": 16,
                "background_color": "#1a1a1a",
                "text_color": "#ffffff",
                "show_artwork": True,
                "artwork_size": 80,
                "layout": "vertical",
                "show_status": False,
                "title": {
                    "font_family": "Georgia, serif",
                    "font_size": 28,
                    "font_weight": "normal",
                    "color": "#f0f0f0"
                },
                "artist": {
                    "font_family": "Georgia, serif",
                    "font_size": 20,
                    "font_weight": "normal",
                    "color": "#cccccc"
                },
                "progress_bar": {
                    "show": True,
                    "position": "inline",
                    "width": 70,
                    "height": 4,
                    "spacing": 15,
                    "background_color": "#444444",
                    "fill_color": "#d4af37",
                    "border_radius": 2
                },
                "frame": {
                    "show": True,
                    "thickness": 1,
                    "corner_radius": 15,
                    "frame_color": "#d4af37",
                    "fill_color": "transparent"
                }
            }
        },
        {
            "name": "Gaming/Streaming Style (Green Theme)",
            "config": {
                "font_family": "Arial",
                "font_size": 16,
                "background_color": "#000000",
                "text_color": "#ffffff",
                "show_artwork": True,
                "artwork_size": 80,
                "layout": "horizontal",
                "show_status": False,
                "title": {
                    "font_family": "Impact, sans-serif",
                    "font_size": 32,
                    "font_weight": "bold",
                    "color": "#00ff00"
                },
                "artist": {
                    "font_family": "Arial, sans-serif",
                    "font_size": 16,
                    "font_weight": "normal",
                    "color": "#66ff66"
                },
                "progress_bar": {
                    "show": True,
                    "position": "top",
                    "width": 100,
                    "height": 8,
                    "spacing": 0,
                    "background_color": "#003300",
                    "fill_color": "#00ff00",
                    "border_radius": 0
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
            "name": "Minimalist Modern (Light Weight Fonts)",
            "config": {
                "font_family": "Arial",
                "font_size": 16,
                "background_color": "#f5f5f5",
                "text_color": "#333333",
                "show_artwork": True,
                "artwork_size": 80,
                "layout": "horizontal",
                "show_status": False,
                "title": {
                    "font_family": "Helvetica, sans-serif",
                    "font_size": 24,
                    "font_weight": "300",
                    "color": "#333333"
                },
                "artist": {
                    "font_family": "Helvetica, sans-serif",
                    "font_size": 16,
                    "font_weight": "200",
                    "color": "#666666"
                },
                "progress_bar": {
                    "show": True,
                    "position": "bottom",
                    "width": 60,
                    "height": 2,
                    "spacing": 30,
                    "background_color": "#e0e0e0",
                    "fill_color": "#333333",
                    "border_radius": 1
                },
                "frame": {
                    "show": True,
                    "thickness": 1,
                    "corner_radius": 5,
                    "frame_color": "#cccccc",
                    "fill_color": "transparent"
                }
            }
        },
        {
            "name": "Bold Contrast (Large Title, Small Artist)",
            "config": {
                "font_family": "Arial",
                "font_size": 16,
                "background_color": "#000000",
                "text_color": "#ffffff",
                "show_artwork": True,
                "artwork_size": 80,
                "layout": "vertical",
                "show_status": False,
                "title": {
                    "font_family": "Arial Black, sans-serif",
                    "font_size": 40,
                    "font_weight": "900",
                    "color": "#ffffff"
                },
                "artist": {
                    "font_family": "Arial, sans-serif",
                    "font_size": 14,
                    "font_weight": "normal",
                    "color": "#888888"
                },
                "progress_bar": {
                    "show": True,
                    "position": "inline",
                    "width": 90,
                    "height": 10,
                    "spacing": 20,
                    "background_color": "#333333",
                    "fill_color": "#ff6b6b",
                    "border_radius": 5
                },
                "frame": {
                    "show": True,
                    "thickness": 4,
                    "corner_radius": 12,
                    "frame_color": "#ff6b6b",
                    "fill_color": "transparent"
                }
            }
        },
        {
            "name": "Colorful Creative (Different Colors)",
            "config": {
                "font_family": "Arial",
                "font_size": 16,
                "background_color": "#2c2c2c",
                "text_color": "#ffffff",
                "show_artwork": True,
                "artwork_size": 80,
                "layout": "horizontal",
                "show_status": False,
                "title": {
                    "font_family": "Comic Sans MS, cursive",
                    "font_size": 30,
                    "font_weight": "bold",
                    "color": "#ff69b4"
                },
                "artist": {
                    "font_family": "Verdana, sans-serif",
                    "font_size": 18,
                    "font_weight": "normal",
                    "color": "#87ceeb"
                },
                "progress_bar": {
                    "show": True,
                    "position": "bottom",
                    "width": 75,
                    "height": 6,
                    "spacing": 25,
                    "background_color": "#444444",
                    "fill_color": "#ff69b4",
                    "border_radius": 3
                },
                "frame": {
                    "show": True,
                    "thickness": 2,
                    "corner_radius": 8,
                    "frame_color": "#87ceeb",
                    "fill_color": "transparent"
                }
            }
        }
    ]
    
    try:
        for i, test_case in enumerate(configs):
            print(f"\n🎨 Test {i+1}: {test_case['name']}")
            
            # Save configuration to file
            config_path = Path('data/config.json')
            config_path.parent.mkdir(exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(test_case['config'], f, indent=2)
            
            # Emit configuration update via WebSocket
            server.socketio.emit('config_updated', test_case['config'])
            
            title_config = test_case['config']['title']
            artist_config = test_case['config']['artist']
            
            print(f"   📝 Title Styling:")
            print(f"      - Font: {title_config['font_family']}")
            print(f"      - Size: {title_config['font_size']}px")
            print(f"      - Weight: {title_config['font_weight']}")
            print(f"      - Color: {title_config['color']}")
            print(f"   🎤 Artist Styling:")
            print(f"      - Font: {artist_config['font_family']}")
            print(f"      - Size: {artist_config['font_size']}px")
            print(f"      - Weight: {artist_config['font_weight']}")
            print(f"      - Color: {artist_config['color']}")
            
            input("   ⏸️  Press Enter to continue to next style...")
        
        print(f"\n🎉 All text styling tests completed!")
        print(f"\n📝 What you should have observed:")
        print(f"1. Title and artist can have completely different fonts")
        print(f"2. Font sizes are independently configurable")
        print(f"3. Font weights (bold, normal, light) work separately")
        print(f"4. Colors can be set independently for title and artist")
        print(f"5. Font families can be different (serif, sans-serif, etc.)")
        
        print(f"\n⚙️  Configuration options available:")
        print(f"Title & Artist:")
        print(f"- font_family: 'Arial', 'Georgia', 'Helvetica', 'Impact', etc.")
        print(f"- font_size: number (pixels)")
        print(f"- font_weight: 'normal', 'bold', 'lighter', 'bolder', or 100-900")
        print(f"- color: hex color (e.g., '#ffffff', '#ff6b6b')")
        
        input("\n⏸️  Press Enter to stop the server...")
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
    finally:
        server.stop()
        print("✅ Server stopped")

if __name__ == "__main__":
    test_text_styling()