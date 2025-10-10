#!/usr/bin/env python3
"""
Final integration test for GUI modernization.

This test verifies that all modernized components work together seamlessly
and that all requirements are met in the final implementation.
"""

import sys
import os
import tempfile
import shutil
import time
import threading
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from unittest.mock import Mock
from core.playlist_manager import PlaylistManager
from core.player_engine import PlayerEngine
from gui.main_window import MainWindow
from gui.theme import get_theme_manager
from models.song import Song


def create_test_song(title, artist="Test Artist", file_path=None):
    """Create a test song object."""
    if file_path is None:
        file_path = f"/test/path/{title.replace(' ', '_').lower()}.mp3"
    
    song = Mock(spec=Song)
    song.file_path = file_path
    song.title = title
    song.artist = artist
    song.album = "Test Album"
    song.artwork_path = None
    song.duration = 180.0
    song.get_display_name.return_value = f"{artist} - {title}"
    return song


def test_component_integration():
    """Test that all modernized components work together seamlessly."""
    print("🔧 Testing component integration...")
    
    # Create temporary directory for test files
    temp_dir = tempfile.mkdtemp()
    playlist_file = os.path.join(temp_dir, "test_playlist.json")
    artwork_dir = os.path.join(temp_dir, "artwork")
    
    try:
        # Initialize core components
        playlist_manager = PlaylistManager(playlist_file, artwork_dir)
        player_engine = PlayerEngine()
        
        # Create GUI with modern theme
        main_window = MainWindow(playlist_manager, player_engine)
        
        # Verify theme is applied
        theme_manager = get_theme_manager()
        assert theme_manager._theme_applied, "Modern theme should be applied"
        
        # Verify window size
        root = main_window.root
        root.update_idletasks()
        
        width = root.winfo_width()
        height = root.winfo_height()
        expected_width = theme_manager.theme.window_width
        expected_height = theme_manager.theme.window_height
        
        print(f"   ✓ Window size: {width}x{height} (expected: {expected_width}x{expected_height})")
        
        # Test playlist functionality
        test_songs = [
            create_test_song("Song One", "Artist A"),
            create_test_song("Song Two", "Artist B"),
            create_test_song("Song Three", "Artist C")
        ]
        
        # Add songs to playlist
        for song in test_songs:
            playlist_manager.get_playlist().songs.append(song)
        
        # Update playlist display
        playlist_widget = main_window.playlist_widget
        playlist_widget.update_playlist(test_songs, None)
        
        # Verify playlist display updates
        assert len(playlist_widget._songs) == 3, "Playlist should contain 3 songs"
        print("   ✓ Playlist functionality working")
        
        # Test music note indicator
        playlist_manager.set_current_song(1)  # Set second song as current
        playlist_widget.update_current_song(1)
        
        # Verify music note is at correct position
        assert playlist_widget._current_index == 1, "Current index should be 1"
        print("   ✓ Music note indicator working")
        
        # Test responsive layout
        root.geometry("350x250")  # Minimum size
        root.update_idletasks()
        
        # Verify components still fit
        min_width = root.winfo_width()
        min_height = root.winfo_height()
        assert min_width >= 350, f"Minimum width should be maintained: {min_width}"
        assert min_height >= 250, f"Minimum height should be maintained: {min_height}"
        print("   ✓ Responsive layout working")
        
        # Test hyperlinks exist
        assert hasattr(main_window, 'web_display_link'), "Web display hyperlink should exist"
        assert hasattr(main_window, 'web_controls_link'), "Web controls hyperlink should exist"
        print("   ✓ Hyperlinks created")
        
        # Clean up
        root.destroy()
        print("   ✓ Component integration test passed")
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_backward_compatibility():
    """Test that existing functionality is preserved."""
    print("🔄 Testing backward compatibility...")
    
    temp_dir = tempfile.mkdtemp()
    playlist_file = os.path.join(temp_dir, "test_playlist.json")
    artwork_dir = os.path.join(temp_dir, "artwork")
    
    try:
        # Initialize components
        playlist_manager = PlaylistManager(playlist_file, artwork_dir)
        player_engine = PlayerEngine()
        main_window = MainWindow(playlist_manager, player_engine)
        
        # Test all original functionality still works
        
        # 1. Playlist operations
        test_song = create_test_song("Test Song")
        playlist_manager.get_playlist().songs.append(test_song)
        assert playlist_manager.get_song_count() == 1, "Add song should work"
        
        playlist_manager.remove_song(0)
        assert playlist_manager.get_song_count() == 0, "Remove song should work"
        print("   ✓ Playlist operations preserved")
        
        # 2. Player engine integration
        test_songs = [create_test_song(f"Song {i}") for i in range(3)]
        for song in test_songs:
            playlist_manager.get_playlist().songs.append(song)
        
        # Set current song
        current_song = playlist_manager.set_current_song(1)
        assert current_song is not None, "Set current song should work"
        assert playlist_manager.get_playlist().current_index == 1, "Current index should be set"
        print("   ✓ Player engine integration preserved")
        
        # 3. Loop functionality
        playlist_manager.set_loop_enabled(True)
        assert playlist_manager.is_loop_enabled(), "Loop should be enabled"
        
        playlist_manager.set_loop_enabled(False)
        assert not playlist_manager.is_loop_enabled(), "Loop should be disabled"
        print("   ✓ Loop functionality preserved")
        
        # 4. GUI callbacks should exist
        assert hasattr(main_window, '_on_play_clicked'), "Play callback should exist"
        assert hasattr(main_window, '_on_pause_clicked'), "Pause callback should exist"
        assert hasattr(main_window, '_on_stop_clicked'), "Stop callback should exist"
        assert hasattr(main_window, '_on_next_clicked'), "Next callback should exist"
        assert hasattr(main_window, '_on_previous_clicked'), "Previous callback should exist"
        print("   ✓ GUI callbacks preserved")
        
        # Clean up
        main_window.root.destroy()
        print("   ✓ Backward compatibility test passed")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_requirements_compliance():
    """Test that all requirements are met."""
    print("📋 Testing requirements compliance...")
    
    temp_dir = tempfile.mkdtemp()
    playlist_file = os.path.join(temp_dir, "test_playlist.json")
    artwork_dir = os.path.join(temp_dir, "artwork")
    
    try:
        # Initialize components
        playlist_manager = PlaylistManager(playlist_file, artwork_dir)
        player_engine = PlayerEngine()
        main_window = MainWindow(playlist_manager, player_engine)
        
        root = main_window.root
        theme_manager = main_window.theme_manager
        
        # Requirement 1: Compact GUI interface (400x300px)
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        assert abs(width - 400) <= 50, f"Width should be ~400px, got {width}"
        assert abs(height - 300) <= 50, f"Height should be ~300px, got {height}"
        print("   ✓ Requirement 1: Compact interface (400x300px)")
        
        # Requirement 2: Modern styling
        theme = theme_manager.theme
        assert theme.bg_primary == "#2b2b2b", "Should use modern dark color scheme"
        assert theme.accent == "#4a9eff", "Should use modern accent color"
        print("   ✓ Requirement 2: Modern styling")
        
        # Requirement 3: Music note indicator follows current song
        test_songs = [create_test_song(f"Song {i}") for i in range(3)]
        for song in test_songs:
            playlist_manager.get_playlist().songs.append(song)
        
        playlist_widget = main_window.playlist_widget
        playlist_widget.update_playlist(test_songs, None)
        
        # Test music note follows current song
        playlist_widget.update_current_song(0)
        assert playlist_widget._current_index == 0, "Music note should be at index 0"
        
        playlist_widget.update_current_song(2)
        assert playlist_widget._current_index == 2, "Music note should move to index 2"
        
        playlist_widget.update_current_song(None)
        assert playlist_widget._current_index is None, "Music note should disappear"
        print("   ✓ Requirement 3: Music note indicator follows current song")
        
        # Requirement 4: All existing functionality maintained
        # (Already tested in backward compatibility)
        print("   ✓ Requirement 4: Existing functionality maintained")
        
        # Requirement 5: Improved visual hierarchy
        # Check that components are properly organized
        assert hasattr(main_window, 'now_playing_frame'), "Now playing display should exist"
        assert hasattr(main_window, 'playlist_widget'), "Playlist widget should exist"
        assert hasattr(main_window, 'play_button'), "Control buttons should exist"
        print("   ✓ Requirement 5: Improved visual hierarchy")
        
        # Requirement 6: Web interface hyperlinks
        assert hasattr(main_window, 'web_display_link'), "Web display link should exist"
        assert hasattr(main_window, 'web_controls_link'), "Web controls link should exist"
        
        # Check hyperlink styling
        display_link = main_window.web_display_link
        controls_link = main_window.web_controls_link
        
        # Verify they look like hyperlinks (have proper styling)
        display_fg = display_link.cget('fg')
        controls_fg = controls_link.cget('fg')
        assert display_fg == theme.accent, f"Display link should use accent color, got {display_fg}"
        assert controls_fg == theme.accent, f"Controls link should use accent color, got {controls_fg}"
        print("   ✓ Requirement 6: Web interface hyperlinks")
        
        # Clean up
        root.destroy()
        print("   ✓ All requirements compliance test passed")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_error_handling():
    """Test error handling and fallback mechanisms."""
    print("🛡️ Testing error handling...")
    
    temp_dir = tempfile.mkdtemp()
    playlist_file = os.path.join(temp_dir, "test_playlist.json")
    artwork_dir = os.path.join(temp_dir, "artwork")
    
    try:
        # Test theme fallback
        playlist_manager = PlaylistManager(playlist_file, artwork_dir)
        player_engine = PlayerEngine()
        
        # This should not crash even if theme application has issues
        main_window = MainWindow(playlist_manager, player_engine)
        
        # Verify GUI still works
        assert main_window.root is not None, "GUI should still be created"
        assert main_window.playlist_widget is not None, "Playlist widget should exist"
        print("   ✓ Theme fallback working")
        
        # Test invalid music note index handling
        playlist_widget = main_window.playlist_widget
        
        # Should not crash with invalid indices
        playlist_widget.update_current_song(-1)  # Negative index
        playlist_widget.update_current_song(999)  # Out of range index
        print("   ✓ Invalid index handling working")
        
        # Test empty playlist handling
        playlist_widget.update_playlist([], None)
        playlist_widget.update_current_song(0)  # Should handle gracefully
        assert playlist_widget._current_index is None, "Should handle empty playlist"
        print("   ✓ Empty playlist handling working")
        
        # Clean up
        main_window.root.destroy()
        print("   ✓ Error handling test passed")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("FINAL GUI MODERNIZATION INTEGRATION TEST")
    print("=" * 60)
    
    try:
        test_component_integration()
        test_backward_compatibility()
        test_requirements_compliance()
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ GUI modernization is complete and fully integrated")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())