#!/usr/bin/env python3
"""
Manual test for minimum size layout behavior.

This script opens the GUI at minimum size to verify that all components
are properly visible and functional at the smallest allowed window size.
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


def test_minimum_size_layout():
    """Test the layout at minimum window size."""
    print("Testing GUI at minimum window size (350x250)")
    print("Please verify that:")
    print("1. All components are visible")
    print("2. Text is properly truncated")
    print("3. Buttons are clickable")
    print("4. Playlist area has adequate space")
    print("5. Window cannot be resized smaller")
    print("\nClose the window when done testing.")
    
    # Create components
    playlist_manager = PlaylistManager()
    player_engine = PlayerEngine(playlist_manager)
    main_window = MainWindow(playlist_manager, player_engine)
    
    # Set to minimum size
    root = main_window.root
    min_width = main_window.theme_manager.theme.window_min_width
    min_height = main_window.theme_manager.theme.window_min_height
    
    root.geometry(f"{min_width}x{min_height}")
    root.update()
    
    print(f"\nWindow set to minimum size: {min_width}x{min_height}")
    print("GUI is now running at minimum size...")
    
    # Start the GUI
    root.mainloop()
    
    print("Test completed.")


if __name__ == "__main__":
    test_minimum_size_layout()