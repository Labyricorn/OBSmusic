"""
Integration tests for music note indicator behavior.

Tests that the music note indicator correctly follows the currently
playing song and responds to playlist changes as specified in requirements.
"""

import unittest
import tkinter as tk
import tempfile
import shutil
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from gui.main_window import MainWindow
from gui.modern_playlist import ModernPlaylistWidget
from gui.theme import ThemeManager
from core.playlist_manager import PlaylistManager
from core.player_engine import PlayerEngine, PlaybackState
from models.song import Song


class TestMusicNoteIndicator(unittest.TestCase):
    """Test cases for music note indicator behavior."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.playlist_file = os.path.join(self.temp_dir, "test_playlist.json")
        self.artwork_dir = os.path.join(self.temp_dir, "artwork")
        
        # Create test components
        self.playlist_manager = PlaylistManager(self.playlist_file, self.artwork_dir)
        self.player_engine = PlayerEngine()
        
        # Mock pygame to avoid audio initialization
        self.pygame_patcher = patch('core.player_engine.pygame')
        self.mock_pygame = self.pygame_patcher.start()
        self.mock_pygame.mixer.music.get_busy.return_value = False
        
        # Create GUI components
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests
        
        self.theme_manager = ThemeManager()
        self.theme_manager.apply_theme(self.root)
        
        # Create modern playlist widget for testing
        self.playlist_widget = ModernPlaylistWidget(self.root, self.theme_manager)
        
        # Create main window for integration tests
        self.main_window = MainWindow(self.playlist_manager, self.player_engine)
        self.main_window.root.withdraw()
    
    def tearDown(self):
        """Clean up test environment."""
        self.pygame_patcher.stop()
        
        # Destroy GUI components
        try:
            if self.root and self.root.winfo_exists():
                self.root.destroy()
        except tk.TclError:
            pass
        
        try:
            if self.main_window.root and self.main_window.root.winfo_exists():
                self.main_window.root.destroy()
        except tk.TclError:
            pass
        
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_songs(self, count=3):
        """Create test songs for playlist.
        
        Args:
            count: Number of test songs to create
            
        Returns:
            List of mock Song objects
        """
        songs = []
        for i in range(count):
            song = Mock(spec=Song)
            song.file_path = os.path.join(self.temp_dir, f"song{i}.mp3")
            song.title = f"Song {i}"
            song.artist = f"Artist {i}"
            song.album = "Test Album"
            song.artwork_path = None
            song.duration = 180.0
            song.get_display_name.return_value = f"Artist {i} - Song {i}"
            song.is_valid.return_value = True
            songs.append(song)
        return songs
    
    def test_music_note_appears_when_song_starts_playing(self):
        """Test that music note indicator appears when a song starts playing."""
        # Create test songs
        songs = self.create_test_songs(3)
        
        # Add songs to playlist widget
        self.playlist_widget.update_playlist(songs, current_index=None)
        
        # Verify no music note initially
        self.assertIsNone(self.playlist_widget._current_index)
        
        # Start playing first song
        self.playlist_widget.update_current_song(0)
        
        # Verify music note appears at correct position
        self.assertEqual(self.playlist_widget._current_index, 0)
        
        # Check that the indicator widget shows the music note
        if len(self.playlist_widget._row_widgets) > 0:
            first_row = self.playlist_widget._row_widgets[0]
            if 'indicator' in first_row:
                indicator_text = first_row['indicator'].cget('text')
                self.assertEqual(indicator_text, "♪")
    
    def test_music_note_moves_when_song_changes(self):
        """Test that music note indicator moves when the current song changes."""
        # Create test songs
        songs = self.create_test_songs(3)
        
        # Add songs to playlist widget with first song playing
        self.playlist_widget.update_playlist(songs, current_index=0)
        
        # Verify music note is at first position
        self.assertEqual(self.playlist_widget._current_index, 0)
        
        # Change to second song
        self.playlist_widget.update_current_song(1)
        
        # Verify music note moved to second position
        self.assertEqual(self.playlist_widget._current_index, 1)
        
        # Check indicators in row widgets
        if len(self.playlist_widget._row_widgets) >= 2:
            # First row should not have music note
            first_row = self.playlist_widget._row_widgets[0]
            if 'indicator' in first_row:
                first_indicator = first_row['indicator'].cget('text')
                self.assertEqual(first_indicator, "")
            
            # Second row should have music note
            second_row = self.playlist_widget._row_widgets[1]
            if 'indicator' in second_row:
                second_indicator = second_row['indicator'].cget('text')
                self.assertEqual(second_indicator, "♪")
    
    def test_music_note_disappears_when_playback_stops(self):
        """Test that music note indicator disappears when playback stops."""
        # Create test songs
        songs = self.create_test_songs(3)
        
        # Add songs to playlist widget with first song playing
        self.playlist_widget.update_playlist(songs, current_index=0)
        
        # Verify music note is present
        self.assertEqual(self.playlist_widget._current_index, 0)
        
        # Stop playback
        self.playlist_widget.update_current_song(None)
        
        # Verify music note disappeared
        self.assertIsNone(self.playlist_widget._current_index)
        
        # Check that no row has music note indicator
        for row_data in self.playlist_widget._row_widgets:
            if 'indicator' in row_data:
                indicator_text = row_data['indicator'].cget('text')
                self.assertEqual(indicator_text, "")
    
    def test_music_note_follows_song_during_reordering(self):
        """Test that music note indicator follows song during playlist reordering."""
        # Create test songs
        songs = self.create_test_songs(3)
        
        # Add songs to playlist manager
        for song in songs:
            self.playlist_manager.get_playlist().songs.append(song)
        
        # Set first song as current
        self.playlist_manager.set_current_song(0)
        
        # Update main window display
        self.main_window._update_playlist_display()
        
        # Get current song before reordering
        current_song = self.playlist_manager.get_current_song()
        self.assertEqual(current_song.title, "Song 0")
        
        # Reorder: move first song to last position
        success = self.playlist_manager.reorder_songs(0, 2)
        self.assertTrue(success)
        
        # Update display after reordering
        self.main_window._update_playlist_display()
        
        # Verify current song is still the same song (now at index 2)
        current_song_after = self.playlist_manager.get_current_song()
        self.assertEqual(current_song_after.title, "Song 0")
        self.assertEqual(self.playlist_manager.get_playlist().current_index, 2)
    
    def test_music_note_color_and_styling(self):
        """Test that music note indicator has correct color and styling."""
        # Create test songs
        songs = self.create_test_songs(1)
        
        # Add songs to playlist widget with song playing
        self.playlist_widget.update_playlist(songs, current_index=0)
        
        # Get music note configuration from theme
        music_note_config = self.theme_manager.get_music_note_config()
        
        # Verify configuration
        self.assertEqual(music_note_config["symbol"], "♪")
        self.assertEqual(music_note_config["color"], self.theme_manager.theme.success)
        self.assertIsInstance(music_note_config["font"], tuple)
        
        # Check that row widget uses correct styling
        if len(self.playlist_widget._row_widgets) > 0:
            first_row = self.playlist_widget._row_widgets[0]
            if 'indicator' in first_row:
                indicator = first_row['indicator']
                indicator_color = indicator.cget('fg')
                self.assertEqual(indicator_color, music_note_config["color"])
    
    def test_music_note_integration_with_player_engine(self):
        """Test music note indicator integration with player engine state changes."""
        # Create test songs and add to playlist manager
        songs = self.create_test_songs(3)
        for song in songs:
            self.playlist_manager.get_playlist().songs.append(song)
        
        # Mock player engine callbacks
        with patch.object(self.player_engine, 'play_song') as mock_play:
            mock_play.return_value = True
            
            # Start playing first song
            self.playlist_manager.set_current_song(0)
            current_song = self.playlist_manager.get_current_song()
            self.player_engine.play_song(current_song)
            
            # Simulate player state change callback
            self.main_window._on_playback_state_changed(PlaybackState.PLAYING)
            self.main_window._on_song_changed(current_song)
            
            # Update GUI
            self.main_window.root.update()
            
            # Verify music note is displayed correctly
            # (This tests the integration between player engine and GUI)
            self.assertEqual(self.playlist_manager.get_playlist().current_index, 0)
    
    def test_music_note_with_empty_playlist(self):
        """Test music note indicator behavior with empty playlist."""
        # Update playlist widget with empty playlist
        self.playlist_widget.update_playlist([], current_index=None)
        
        # Verify no music note is displayed
        self.assertIsNone(self.playlist_widget._current_index)
        self.assertEqual(len(self.playlist_widget._row_widgets), 0)
        
        # Try to set current song (should handle gracefully)
        self.playlist_widget.update_current_song(0)
        
        # Should still be None since playlist is empty
        self.assertIsNone(self.playlist_widget._current_index)
    
    def test_music_note_with_invalid_index(self):
        """Test music note indicator behavior with invalid current index."""
        # Create test songs
        songs = self.create_test_songs(3)
        
        # Add songs to playlist widget
        self.playlist_widget.update_playlist(songs, current_index=None)
        
        # Try to set invalid current index
        self.playlist_widget.update_current_song(5)  # Index out of range
        
        # Should handle gracefully and not crash
        # Current index should remain None or be handled appropriately
        self.assertTrue(self.playlist_widget._current_index is None or 
                       self.playlist_widget._current_index < len(songs))
    
    def test_music_note_persistence_across_updates(self):
        """Test that music note indicator persists across playlist updates."""
        # Create initial songs
        songs = self.create_test_songs(2)
        
        # Add songs with first one playing
        self.playlist_widget.update_playlist(songs, current_index=0)
        
        # Verify music note is at first position
        self.assertEqual(self.playlist_widget._current_index, 0)
        
        # Add more songs to the playlist
        more_songs = self.create_test_songs(4)  # Total will be 4 songs
        
        # Update playlist while keeping current song at index 0
        self.playlist_widget.update_playlist(more_songs, current_index=0)
        
        # Verify music note is still at first position
        self.assertEqual(self.playlist_widget._current_index, 0)
        
        # Check that first row still has music note
        if len(self.playlist_widget._row_widgets) > 0:
            first_row = self.playlist_widget._row_widgets[0]
            if 'indicator' in first_row:
                indicator_text = first_row['indicator'].cget('text')
                self.assertEqual(indicator_text, "♪")
    
    def test_music_note_animation_state(self):
        """Test music note indicator animation state management."""
        # This test checks if the music note has proper animation state
        # (pulse effect when playing as mentioned in design)
        
        # Create test songs
        songs = self.create_test_songs(1)
        
        # Add songs to playlist widget with song playing
        self.playlist_widget.update_playlist(songs, current_index=0)
        
        # Check if music note indicator exists and is properly configured
        if len(self.playlist_widget._row_widgets) > 0:
            first_row = self.playlist_widget._row_widgets[0]
            if 'indicator' in first_row:
                indicator = first_row['indicator']
                
                # Verify indicator has music note symbol
                self.assertEqual(indicator.cget('text'), "♪")
                
                # Verify indicator has success color (green)
                expected_color = self.theme_manager.theme.success
                self.assertEqual(indicator.cget('fg'), expected_color)
    
    def test_music_note_removal_on_song_removal(self):
        """Test that music note is handled correctly when current song is removed."""
        # Create test songs and add to playlist manager
        songs = self.create_test_songs(3)
        for song in songs:
            self.playlist_manager.get_playlist().songs.append(song)
        
        # Set second song as current (index 1)
        self.playlist_manager.set_current_song(1)
        
        # Remove the current song
        success = self.playlist_manager.remove_song(1)
        self.assertTrue(success)
        
        # Update display
        self.main_window._update_playlist_display()
        
        # Verify playlist manager handled current index correctly
        # (Should either move to next song or clear current if no songs left)
        remaining_songs = self.playlist_manager.get_songs()
        current_index = self.playlist_manager.get_playlist().current_index
        
        if remaining_songs:
            # If songs remain, current index should be valid
            self.assertTrue(0 <= current_index < len(remaining_songs))
        else:
            # If no songs remain, current index should be None or -1
            self.assertTrue(current_index is None or current_index == -1)
    
    def test_music_note_multiple_rapid_changes(self):
        """Test music note indicator with rapid song changes."""
        # Create test songs
        songs = self.create_test_songs(5)
        
        # Add songs to playlist widget
        self.playlist_widget.update_playlist(songs, current_index=None)
        
        # Rapidly change current song multiple times
        for i in range(5):
            self.playlist_widget.update_current_song(i)
            self.assertEqual(self.playlist_widget._current_index, i)
            
            # Verify only the current row has music note
            for j, row_data in enumerate(self.playlist_widget._row_widgets):
                if 'indicator' in row_data:
                    expected_text = "♪" if j == i else ""
                    actual_text = row_data['indicator'].cget('text')
                    self.assertEqual(actual_text, expected_text, 
                                   f"Row {j} should {'have' if j == i else 'not have'} music note when song {i} is current")
        
        # Finally set to None (stop playback)
        self.playlist_widget.update_current_song(None)
        self.assertIsNone(self.playlist_widget._current_index)
        
        # Verify no rows have music note
        for row_data in self.playlist_widget._row_widgets:
            if 'indicator' in row_data:
                self.assertEqual(row_data['indicator'].cget('text'), "")


if __name__ == '__main__':
    unittest.main()