#!/usr/bin/env python3
"""
Test script for playlist scrolling functionality.

This script tests that the playlist can be scrolled when there are more
songs than can fit in the visible area.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.playlist_manager import PlaylistManager
from core.player_engine import PlayerEngine
from gui.main_window import MainWindow


def test_playlist_scrolling():
    """Test playlist scrolling functionality."""
    print("Testing Playlist Scrolling")
    print("=" * 30)
    print("This test will:")
    print("1. Load the existing playlist")
    print("2. Set window to a small size to force scrolling")
    print("3. You should be able to:")
    print("   - See a scrollbar on the right side of the playlist")
    print("   - Scroll with mouse wheel over the playlist area")
    print("   - Drag the scrollbar to navigate")
    print("   - See all songs by scrolling")
    print("\nClose the window when done testing.")
    
    # Create components
    playlist_manager = PlaylistManager()
    player_engine = PlayerEngine(playlist_manager)
    main_window = MainWindow(playlist_manager, player_engine)
    
    # Set to a small size to force scrolling
    root = main_window.root
    root.geometry("400x250")  # Small height to force playlist scrolling
    root.update()
    
    print(f"\nWindow set to 400x250 to test scrolling")
    print(f"Playlist has {playlist_manager.get_song_count()} songs")
    print("GUI is now running - test the scrolling functionality...")
    
    # Start the GUI
    root.mainloop()
    
    print("Scrolling test completed.")


if __name__ == "__main__":
    test_playlist_scrolling()