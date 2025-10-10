#!/usr/bin/env python3
"""
Test script for the modernized Now Playing display component.

This script tests the new features:
- Modern styling with dark background and rounded corners
- Compact 60px height layout with proper padding
- Text truncation with ellipsis for long song titles
- Smooth fade transitions for song changes
"""

import tkinter as tk
import sys
import os
import time
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.song import Song
from models.playlist import Playlist
from core.playlist_manager import PlaylistManager
from core.player_engine import PlayerEngine
from gui.main_window import MainWindow

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_now_playing_display():
    """Test the modernized Now Playing display component."""
    print("Testing modernized Now Playing display...")
    
    # Create test components
    playlist = Playlist()
    playlist_manager = PlaylistManager(playlist)
    player_engine = PlayerEngine(playlist_manager)
    
    # Create mock songs for testing (bypass file validation)
    test_songs = []
    
    # Create songs manually without file validation
    song1 = Song.__new__(Song)
    song1.file_path = "test1.mp3"
    song1.title = "Short Song"
    song1.artist = "Artist"
    song1.album = "Album"
    song1.duration = 180
    test_songs.append(song1)
    
    song2 = Song.__new__(Song)
    song2.file_path = "test2.mp3"
    song2.title = "This is a Very Long Song Title That Should Be Truncated With Ellipsis"
    song2.artist = "Very Long Artist Name That Also Needs Truncation"
    song2.album = "Very Long Album Name"
    song2.duration = 240
    test_songs.append(song2)
    
    song3 = Song.__new__(Song)
    song3.file_path = "test3.mp3"
    song3.title = "Medium Length Song Title"
    song3.artist = "Medium Artist"
    song3.album = "Medium Album"
    song3.duration = 200
    test_songs.append(song3)
    
    # Add songs to playlist manually
    for song in test_songs:
        playlist.songs.append(song)
    
    # Create main window
    main_window = MainWindow(playlist_manager, player_engine)
    
    def test_song_changes():
        """Test song changes with fade transitions."""
        print("Testing song changes and fade transitions...")
        
        # Test different songs to see fade transitions
        for i, song in enumerate(test_songs):
            print(f"Setting current song to: {song.get_display_name()}")
            playlist_manager.set_current_song(i)
            main_window.root.update()
            time.sleep(2)  # Wait to see the transition
    
    def test_text_truncation():
        """Test text truncation with very long titles."""
        print("Testing text truncation...")
        
        # Set to the long title song
        playlist_manager.set_current_song(1)  # Very long song
        main_window.root.update()
        
        print("Long title should be truncated with ellipsis")
        time.sleep(3)
    
    def test_no_song_state():
        """Test the 'No song selected' state."""
        print("Testing no song state...")
        
        # Clear current song
        playlist.current_index = None
        main_window._update_current_song_display()
        main_window.root.update()
        
        print("Should show 'No song selected'")
        time.sleep(2)
    
    # Schedule tests
    main_window.root.after(1000, test_song_changes)
    main_window.root.after(10000, test_text_truncation)
    main_window.root.after(15000, test_no_song_state)
    
    # Auto-close after tests
    main_window.root.after(20000, main_window.root.quit)
    
    print("Starting GUI for Now Playing display test...")
    print("The test will automatically cycle through different songs to demonstrate:")
    print("1. Modern styling with dark background")
    print("2. Compact 60px height layout")
    print("3. Text truncation with ellipsis")
    print("4. Smooth fade transitions")
    print("5. No song selected state")
    
    # Run the GUI
    main_window.run()
    
    print("Now Playing display test completed!")


if __name__ == "__main__":
    test_now_playing_display()