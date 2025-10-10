#!/usr/bin/env python3
"""
Test script for Task 4: Modern playlist display with alternating row colors.

This script tests the implementation of the modern playlist widget with:
- 24px compact row height
- Alternating row colors for better readability
- Modern selection highlighting with rounded corners
- 10px regular weight font styling
"""

import tkinter as tk
import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.theme import get_theme_manager, apply_modern_theme
from gui.modern_playlist import ModernPlaylistWidget
from models.song import Song


class MockSong:
    """Mock song class for testing."""
    
    def __init__(self, title: str, artist: str = "Test Artist", album: str = "Test Album"):
        self.title = title
        self.artist = artist
        self.album = album
        self.file_path = f"/mock/path/{title}.mp3"
    
    def get_display_name(self) -> str:
        return f"{self.title} - {self.artist}"


def test_modern_playlist_display():
    """Test the modern playlist display functionality."""
    
    # Create root window
    root = tk.Tk()
    root.title("Task 4: Modern Playlist Display Test")
    
    # Apply modern theme
    apply_modern_theme(root)
    theme_manager = get_theme_manager()
    
    # Create main frame
    main_frame = theme_manager.create_modern_frame(root)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)
    
    # Create modern playlist widget
    playlist_widget = ModernPlaylistWidget(main_frame, theme_manager)
    playlist_widget.grid(row=0, column=0, sticky="nsew")
    
    # Create test songs
    test_songs = [
        MockSong("Song One", "Artist A", "Album 1"),
        MockSong("Song Two", "Artist B", "Album 2"),
        MockSong("Song Three", "Artist A", "Album 1"),
        MockSong("Song Four", "Artist C", "Album 3"),
        MockSong("Song Five", "Artist B", "Album 2"),
        MockSong("Song Six", "Artist D", "Album 4"),
        MockSong("Song Seven", "Artist A", "Album 1"),
        MockSong("Song Eight", "Artist E", "Album 5"),
        MockSong("Song Nine", "Artist C", "Album 3"),
        MockSong("Song Ten", "Artist F", "Album 6"),
    ]
    
    # Update playlist with test songs (song 2 is currently playing)
    playlist_widget.update_playlist(test_songs, current_index=2)
    
    # Set up callbacks
    def on_selection_changed(index):
        print(f"Selected song at index {index}: {test_songs[index].get_display_name()}")
    
    def on_reorder(from_index, to_index):
        print(f"Reordered song from {from_index} to {to_index}")
        # Simulate reordering
        song = test_songs.pop(from_index)
        test_songs.insert(to_index, song)
        # Update display
        playlist_widget.update_playlist(test_songs, current_index=2)
    
    playlist_widget.set_selection_callback(on_selection_changed)
    playlist_widget.set_drag_drop_callback(on_reorder)
    
    # Create control buttons for testing
    control_frame = theme_manager.create_modern_frame(root)
    control_frame.pack(fill="x", padx=10, pady=5)
    
    def change_current_song():
        """Change the currently playing song for testing music note indicator."""
        import random
        new_current = random.randint(0, len(test_songs) - 1)
        playlist_widget.update_current_song(new_current)
        print(f"Changed current song to index {new_current}")
    
    def clear_selection():
        """Clear the current selection."""
        playlist_widget.set_selection(None)
        print("Cleared selection")
    
    # Test buttons
    change_song_btn = theme_manager.create_modern_button(
        control_frame,
        text="Change Current Song",
        command=change_current_song
    )
    change_song_btn.pack(side="left", padx=5)
    
    clear_btn = theme_manager.create_modern_button(
        control_frame,
        text="Clear Selection",
        command=clear_selection
    )
    clear_btn.pack(side="left", padx=5)
    
    # Add info label
    info_label = theme_manager.create_modern_label(
        root,
        text="Test Features: Alternating row colors, 24px row height, 10px font, hover effects, drag-and-drop reordering",
        style_type="secondary"
    )
    info_label.pack(fill="x", padx=10, pady=5)
    
    # Print test information
    print("=== Task 4: Modern Playlist Display Test ===")
    print("Features being tested:")
    print("✓ Compact 24px row height")
    print("✓ Alternating row colors for better readability")
    print("✓ Modern selection highlighting")
    print("✓ 10px regular weight font styling")
    print("✓ Music note indicator following current song")
    print("✓ Hover effects")
    print("✓ Drag-and-drop reordering")
    print("\nInteraction instructions:")
    print("- Click rows to select them")
    print("- Drag rows to reorder them")
    print("- Use buttons to test functionality")
    print("- Observe alternating row colors and hover effects")
    
    # Start the GUI
    root.mainloop()


if __name__ == "__main__":
    test_modern_playlist_display()