#!/usr/bin/env python3
"""
Demo script for the music player GUI.

This script demonstrates the desktop GUI interface functionality.
"""

import logging
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
from core.playlist_manager import PlaylistManager
from core.player_engine import PlayerEngine

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main function to run the GUI demo."""
    try:
        logger.info("Starting Music Player GUI Demo")
        
        # Create playlist manager and player engine
        playlist_manager = PlaylistManager("data/playlist.json", "data/artwork")
        player_engine = PlayerEngine()
        
        # Set up playlist integration
        player_engine.set_playlist(playlist_manager.get_playlist())
        
        # Create and run the main window
        main_window = MainWindow(playlist_manager, player_engine)
        
        logger.info("GUI initialized successfully")
        logger.info("Features available:")
        logger.info("- Playlist display with drag-and-drop reordering")
        logger.info("- Playback controls (Play, Pause, Stop, Next, Previous)")
        logger.info("- Volume slider with real-time adjustment")
        logger.info("- Loop checkbox with state persistence")
        logger.info("- File management (Add Songs, Remove Song, Clear Playlist, Save Playlist)")
        logger.info("- Current song display with title and artist")
        logger.info("- Error handling and user feedback")
        
        # Start the GUI main loop
        main_window.run()
        
    except Exception as e:
        logger.error(f"Error running GUI demo: {e}")
        sys.exit(1)
    finally:
        logger.info("GUI demo finished")


if __name__ == "__main__":
    main()