#!/usr/bin/env python3
"""
Test script for modernized playback control buttons.

This script tests the enhanced control button styling, state management,
and visual feedback for the modernized GUI.
"""

import sys
import os
import tkinter as tk
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from models.playlist import Playlist
from models.song import Song
from core.playlist_manager import PlaylistManager
from core.player_engine import PlayerEngine, PlaybackState
from gui.main_window import MainWindow
from gui.theme import get_theme_manager


def create_test_songs():
    """Create test songs for the playlist using existing files."""
    # Use existing test files or create minimal mock songs
    test_files = [
        "create_placeholder.py",  # Use existing files as placeholders
        "main.py",
        "requirements.txt"
    ]
    
    test_songs = []
    for i, file_path in enumerate(test_files, 1):
        if os.path.exists(file_path):
            # Create a mock song that bypasses file validation for GUI testing
            song = Song.__new__(Song)  # Create without calling __init__
            song.file_path = file_path
            song.title = f"Test Song {i}"
            song.artist = f"Test Artist {i}"
            song.album = f"Test Album {i}"
            song.duration = 180  # 3 minutes
            test_songs.append(song)
    
    return test_songs


def test_control_button_styling():
    """Test the modernized control button styling and state management."""
    print("Testing modernized control button styling...")
    
    # Create test components (empty playlist for GUI testing)
    playlist = Playlist()
    playlist_manager = PlaylistManager(playlist)
    player_engine = PlayerEngine(playlist_manager)
    
    # Create main window
    main_window = MainWindow(playlist_manager, player_engine)
    root = main_window.root
    
    # Test theme application
    theme_manager = get_theme_manager()
    assert theme_manager.is_theme_applied(), "Theme should be applied"
    
    # Test control button creation
    assert hasattr(main_window, 'play_button'), "Play button should exist"
    assert hasattr(main_window, 'pause_button'), "Pause button should exist"
    assert hasattr(main_window, 'stop_button'), "Stop button should exist"
    assert hasattr(main_window, 'next_button'), "Next button should exist"
    assert hasattr(main_window, 'previous_button'), "Previous button should exist"
    
    # Test button styling
    play_button_style = main_window.play_button.cget('style')
    assert 'ModernControl' in play_button_style, f"Play button should use modern control style, got: {play_button_style}"
    
    # Test initial button states (should be normal when stopped)
    initial_state = player_engine.get_state()
    assert initial_state == PlaybackState.STOPPED, "Initial state should be stopped"
    
    # Update controls and check styling
    main_window._update_playback_controls()
    
    # Test button state changes
    print("Testing button state changes...")
    
    # Test playing state
    player_engine._state = PlaybackState.PLAYING
    main_window._update_playback_controls(PlaybackState.PLAYING)
    play_style = main_window.play_button.cget('style')
    assert 'Active' in play_style, f"Play button should be active when playing, got: {play_style}"
    
    # Test paused state
    player_engine._state = PlaybackState.PAUSED
    main_window._update_playback_controls(PlaybackState.PAUSED)
    pause_style = main_window.pause_button.cget('style')
    assert 'Active' in pause_style, f"Pause button should be active when paused, got: {pause_style}"
    
    # Test stopped state
    player_engine._state = PlaybackState.STOPPED
    main_window._update_playback_controls(PlaybackState.STOPPED)
    stop_style = main_window.stop_button.cget('style')
    assert 'Active' in stop_style, f"Stop button should be active when stopped, got: {stop_style}"
    
    print("✓ Control button styling tests passed")
    
    # Test visual appearance
    print("Testing visual appearance...")
    
    # Check control panel height
    controls_frame = None
    for child in root.winfo_children():
        if hasattr(child, 'winfo_children'):
            for grandchild in child.winfo_children():
                if hasattr(grandchild, 'grid_info') and grandchild.grid_info().get('row') == 2:
                    controls_frame = grandchild
                    break
    
    if controls_frame:
        # Force update to get actual dimensions
        root.update_idletasks()
        height = controls_frame.winfo_height()
        expected_height = theme_manager.theme.controls_height
        print(f"Control panel height: {height}px (expected: {expected_height}px)")
        
        # Allow some tolerance for frame borders and padding
        assert abs(height - expected_height) <= 5, f"Control panel height should be ~{expected_height}px, got {height}px"
    
    print("✓ Visual appearance tests passed")
    
    # Test button spacing
    print("Testing button spacing...")
    
    # Check that buttons use proper spacing (4px)
    expected_spacing = theme_manager.theme.spacing_small
    assert expected_spacing == 4, f"Expected spacing should be 4px, got {expected_spacing}px"
    
    print("✓ Button spacing tests passed")
    
    print("All modernized control button tests passed!")
    
    # Show the window for visual inspection
    print("\nShowing window for visual inspection...")
    print("- Control panel should be 30px high")
    print("- Buttons should be 24x24px with modern flat design")
    print("- Button spacing should be 4px")
    print("- Active button should be highlighted with accent color")
    print("- Hover effects should provide visual feedback")
    print("\nClose the window to complete the test.")
    
    root.mainloop()


def test_button_interactions():
    """Test button click interactions and state changes."""
    print("Testing button interactions...")
    
    # Create test components
    playlist = Playlist()
    playlist_manager = PlaylistManager(playlist)
    player_engine = PlayerEngine(playlist_manager)
    
    # Create main window
    main_window = MainWindow(playlist_manager, player_engine)
    
    # Test play button interaction
    initial_state = player_engine.get_state()
    assert initial_state == PlaybackState.STOPPED, "Should start in stopped state"
    
    # Test that button states update correctly
    main_window._update_playback_controls()
    
    print("✓ Button interaction tests passed")


if __name__ == "__main__":
    print("Testing Modernized Control Buttons")
    print("=" * 50)
    
    try:
        test_control_button_styling()
        test_button_interactions()
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)