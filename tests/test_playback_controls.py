"""
Integration tests for playback control functionality.

These tests verify that the playback controls work correctly with the
player engine and meet all requirements.
"""

import unittest
import tkinter as tk
import tempfile
import shutil
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from gui.main_window import MainWindow
from core.playlist_manager import PlaylistManager
from core.player_engine import PlayerEngine, PlaybackState
from models.song import Song


class TestPlaybackControls(unittest.TestCase):
    """Test playback control functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.playlist_file = os.path.join(self.temp_dir, "test_playlist.json")
        self.artwork_dir = os.path.join(self.temp_dir, "artwork")
        
        # Create test MP3 file path
        self.test_mp3_path = os.path.join(self.temp_dir, "test_song.mp3")
        
        # Create playlist manager and player engine
        self.playlist_manager = PlaylistManager(self.playlist_file, self.artwork_dir)
        self.player_engine = PlayerEngine()
        
        # Mock pygame to avoid audio initialization in tests
        self.pygame_patcher = patch('core.player_engine.pygame')
        self.mock_pygame = self.pygame_patcher.start()
        self.mock_pygame.mixer.music.get_busy.return_value = False
        
        # Create main window (but don't start main loop)
        self.main_window = MainWindow(self.playlist_manager, self.player_engine)
        
        # Don't actually show the window during tests
        self.main_window.root.withdraw()
    
    def tearDown(self):
        """Clean up test environment."""
        # Stop pygame mock
        self.pygame_patcher.stop()
        
        # Destroy GUI safely
        try:
            if self.main_window.root and self.main_window.root.winfo_exists():
                self.main_window.root.destroy()
        except tk.TclError:
            # Window already destroyed
            pass
        
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('os.path.exists')
    def test_play_button_starts_playback_with_current_song(self, mock_exists):
        """Test that play button starts playback when there's a current song (Requirement 7.1)."""
        mock_exists.return_value = True
        
        # Add a test song and set as current
        test_song = Song(
            file_path=self.test_mp3_path,
            title="Test Song",
            artist="Test Artist",
            album="Test Album"
        )
        self.playlist_manager.get_playlist().songs.append(test_song)
        self.playlist_manager.set_current_song(0)
        
        with patch.object(self.player_engine, 'play_song') as mock_play_song:
            with patch.object(self.player_engine, 'is_paused') as mock_is_paused:
                mock_play_song.return_value = True
                mock_is_paused.return_value = False
                
                # Click play button
                self.main_window._on_play_clicked()
                
                # Verify play_song was called
                mock_play_song.assert_called_once()
    
    def test_play_button_resumes_when_paused(self):
        """Test that play button resumes playback when paused (Requirement 7.1)."""
        with patch.object(self.player_engine, 'play') as mock_play:
            with patch.object(self.player_engine, 'is_paused') as mock_is_paused:
                mock_play.return_value = True
                mock_is_paused.return_value = True
                
                # Click play button when paused
                self.main_window._on_play_clicked()
                
                # Verify play was called (should resume)
                mock_play.assert_called_once()
    
    @patch('os.path.exists')
    def test_play_button_starts_first_song_when_no_current(self, mock_exists):
        """Test that play button starts first song when no current song."""
        mock_exists.return_value = True
        
        # Add a test song to playlist
        test_song = Song(
            file_path=self.test_mp3_path,
            title="Test Song",
            artist="Test Artist",
            album="Test Album"
        )
        self.playlist_manager.get_playlist().songs.append(test_song)
        
        with patch.object(self.player_engine, 'play_song') as mock_play_song:
            with patch.object(self.player_engine, 'is_paused') as mock_is_paused:
                mock_play_song.return_value = True
                mock_is_paused.return_value = False
                
                # Click play button when no current song
                self.main_window._on_play_clicked()
                
                # Verify play_song was called with first song
                mock_play_song.assert_called_once()
                called_song = mock_play_song.call_args[0][0]
                self.assertEqual(called_song.title, "Test Song")
    
    def test_pause_button_pauses_playback(self):
        """Test that pause button pauses playback (Requirement 7.2)."""
        with patch.object(self.player_engine, 'pause') as mock_pause:
            mock_pause.return_value = True
            
            # Click pause button
            self.main_window._on_pause_clicked()
            
            # Verify pause was called
            mock_pause.assert_called_once()
    
    def test_stop_button_stops_playback(self):
        """Test that stop button stops playback (Requirement 7.3)."""
        with patch.object(self.player_engine, 'stop') as mock_stop:
            mock_stop.return_value = True
            
            # Click stop button
            self.main_window._on_stop_clicked()
            
            # Verify stop was called
            mock_stop.assert_called_once()
    
    def test_next_button_advances_to_next_song(self):
        """Test that next button advances to next song (Requirement 7.4)."""
        with patch.object(self.player_engine, 'next_song') as mock_next:
            mock_next.return_value = True
            
            # Click next button
            self.main_window._on_next_clicked()
            
            # Verify next_song was called
            mock_next.assert_called_once()
    
    def test_previous_button_goes_to_previous_song(self):
        """Test that previous button goes to previous song (Requirement 7.5)."""
        with patch.object(self.player_engine, 'previous_song') as mock_previous:
            mock_previous.return_value = True
            
            # Click previous button
            self.main_window._on_previous_clicked()
            
            # Verify previous_song was called
            mock_previous.assert_called_once()
    
    def test_volume_slider_changes_playback_volume(self):
        """Test that volume slider changes playback volume (Requirement 7.6)."""
        with patch.object(self.player_engine, 'set_volume') as mock_set_volume:
            mock_set_volume.return_value = True
            
            # Test various volume levels
            test_volumes = [0.0, 0.25, 0.5, 0.75, 1.0]
            
            for volume in test_volumes:
                with self.subTest(volume=volume):
                    # Simulate volume slider change
                    self.main_window._on_volume_changed(str(volume))
                    
                    # Verify set_volume was called with correct value
                    mock_set_volume.assert_called_with(volume)
    
    def test_volume_slider_handles_invalid_values(self):
        """Test that volume slider handles invalid values gracefully."""
        with patch.object(self.player_engine, 'set_volume') as mock_set_volume:
            # Test invalid volume value
            self.main_window._on_volume_changed("invalid")
            
            # Verify set_volume was not called
            mock_set_volume.assert_not_called()
    
    def test_loop_checkbox_enables_looping(self):
        """Test that loop checkbox enables playlist looping (Requirement 3.1)."""
        # Initially loop should be disabled
        self.assertFalse(self.playlist_manager.is_loop_enabled())
        
        # Enable loop via checkbox
        self.main_window.loop_var.set(True)
        self.main_window._on_loop_toggled()
        
        # Verify loop was enabled
        self.assertTrue(self.playlist_manager.is_loop_enabled())
    
    def test_loop_checkbox_disables_looping(self):
        """Test that loop checkbox disables playlist looping (Requirement 3.2)."""
        # Enable loop first
        self.playlist_manager.set_loop_enabled(True)
        self.assertTrue(self.playlist_manager.is_loop_enabled())
        
        # Disable loop via checkbox
        self.main_window.loop_var.set(False)
        self.main_window._on_loop_toggled()
        
        # Verify loop was disabled
        self.assertFalse(self.playlist_manager.is_loop_enabled())
    
    def test_loop_setting_persists_across_sessions(self):
        """Test that loop setting persists for future sessions (Requirement 3.4)."""
        # Enable loop
        self.main_window.loop_var.set(True)
        self.main_window._on_loop_toggled()
        
        # Save playlist (which should save loop setting)
        self.playlist_manager.save_playlist()
        
        # Create new playlist manager (simulating new session)
        new_playlist_manager = PlaylistManager(self.playlist_file, self.artwork_dir)
        
        # Verify loop setting was persisted
        self.assertTrue(new_playlist_manager.is_loop_enabled())
    
    def test_playback_controls_update_based_on_state(self):
        """Test that playback controls update based on player state."""
        # Test stopped state
        self.main_window._update_playback_controls(PlaybackState.STOPPED)
        self.assertEqual(str(self.main_window.play_button.cget("state")), "normal")
        self.assertEqual(str(self.main_window.pause_button.cget("state")), "disabled")
        self.assertEqual(str(self.main_window.stop_button.cget("state")), "disabled")
        
        # Test playing state
        self.main_window._update_playback_controls(PlaybackState.PLAYING)
        self.assertEqual(str(self.main_window.play_button.cget("state")), "disabled")
        self.assertEqual(str(self.main_window.pause_button.cget("state")), "normal")
        self.assertEqual(str(self.main_window.stop_button.cget("state")), "normal")
        
        # Test paused state
        self.main_window._update_playback_controls(PlaybackState.PAUSED)
        self.assertEqual(str(self.main_window.play_button.cget("state")), "normal")
        self.assertEqual(str(self.main_window.pause_button.cget("state")), "disabled")
        self.assertEqual(str(self.main_window.stop_button.cget("state")), "normal")
    
    @patch('os.path.exists')
    def test_navigation_buttons_disabled_when_no_songs(self, mock_exists):
        """Test that navigation buttons are disabled when playlist is empty."""
        mock_exists.return_value = True
        
        # Ensure playlist is empty
        self.playlist_manager.clear_playlist()
        
        # Update controls
        self.main_window._update_playback_controls()
        
        # Navigation buttons should be disabled
        self.assertEqual(str(self.main_window.next_button.cget("state")), "disabled")
        self.assertEqual(str(self.main_window.previous_button.cget("state")), "disabled")
    
    @patch('os.path.exists')
    def test_navigation_buttons_enabled_when_songs_present(self, mock_exists):
        """Test that navigation buttons are enabled when songs are present."""
        mock_exists.return_value = True
        
        # Add a test song
        test_song = Song(
            file_path=self.test_mp3_path,
            title="Test Song",
            artist="Test Artist",
            album="Test Album"
        )
        self.playlist_manager.get_playlist().songs.append(test_song)
        
        # Update controls
        self.main_window._update_playback_controls()
        
        # Navigation buttons should be enabled
        self.assertEqual(str(self.main_window.next_button.cget("state")), "normal")
        self.assertEqual(str(self.main_window.previous_button.cget("state")), "normal")
    
    def test_volume_slider_initializes_with_player_volume(self):
        """Test that volume slider initializes with current player volume."""
        # Set player volume
        test_volume = 0.8
        self.player_engine.set_volume(test_volume)
        
        # Create new main window
        new_main_window = MainWindow(self.playlist_manager, self.player_engine)
        new_main_window.root.withdraw()
        
        try:
            # Check that volume slider was initialized with player volume
            slider_volume = new_main_window.volume_scale.get()
            self.assertAlmostEqual(slider_volume, test_volume, places=2)
        finally:
            # Clean up
            if new_main_window.root:
                new_main_window.root.destroy()
    
    def test_loop_checkbox_initializes_with_playlist_setting(self):
        """Test that loop checkbox initializes with current playlist setting."""
        # Set playlist loop setting
        self.playlist_manager.set_loop_enabled(True)
        
        # Create new main window
        new_main_window = MainWindow(self.playlist_manager, self.player_engine)
        new_main_window.root.withdraw()
        
        try:
            # Check that loop checkbox was initialized with playlist setting
            checkbox_value = new_main_window.loop_var.get()
            self.assertTrue(checkbox_value)
        finally:
            # Clean up
            if new_main_window.root:
                new_main_window.root.destroy()
    
    def test_real_time_volume_adjustment(self):
        """Test that volume changes are applied in real-time."""
        with patch.object(self.player_engine, 'set_volume') as mock_set_volume:
            mock_set_volume.return_value = True
            
            # Simulate multiple rapid volume changes (real-time adjustment)
            volumes = [0.1, 0.2, 0.3, 0.4, 0.5]
            
            for volume in volumes:
                self.main_window._on_volume_changed(str(volume))
            
            # Verify all volume changes were applied
            self.assertEqual(mock_set_volume.call_count, len(volumes))
            
            # Verify final volume is correct
            final_call = mock_set_volume.call_args_list[-1]
            self.assertEqual(final_call[0][0], 0.5)
    
    def test_playback_controls_respond_to_player_callbacks(self):
        """Test that playback controls respond to player engine state changes."""
        # Mock the GUI update method
        with patch.object(self.main_window, '_update_playback_controls') as mock_update:
            # Simulate player state change
            self.main_window._on_playback_state_changed(PlaybackState.PLAYING)
            
            # Process scheduled GUI updates
            self.main_window.root.update()
            
            # Verify GUI update was scheduled and called
            mock_update.assert_called_once_with(PlaybackState.PLAYING)
    
    def test_all_control_buttons_exist_and_are_functional(self):
        """Test that all required control buttons exist and are functional."""
        # Verify all buttons exist
        self.assertIsNotNone(self.main_window.play_button)
        self.assertIsNotNone(self.main_window.pause_button)
        self.assertIsNotNone(self.main_window.stop_button)
        self.assertIsNotNone(self.main_window.next_button)
        self.assertIsNotNone(self.main_window.previous_button)
        
        # Verify volume slider exists
        self.assertIsNotNone(self.main_window.volume_scale)
        
        # Verify loop checkbox exists
        self.assertIsNotNone(self.main_window.loop_checkbox)
        self.assertIsNotNone(self.main_window.loop_var)
        
        # Verify buttons have proper text/symbols
        self.assertEqual(self.main_window.play_button.cget("text"), "▶")
        self.assertEqual(self.main_window.pause_button.cget("text"), "⏸")
        self.assertEqual(self.main_window.stop_button.cget("text"), "⏹")
        self.assertEqual(self.main_window.next_button.cget("text"), "⏭")
        self.assertEqual(self.main_window.previous_button.cget("text"), "⏮")
        
        # Verify loop checkbox has proper text
        self.assertEqual(self.main_window.loop_checkbox.cget("text"), "Loop")


if __name__ == '__main__':
    # Run tests
    unittest.main()