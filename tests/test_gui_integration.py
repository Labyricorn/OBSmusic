"""
Integration tests for GUI playlist operations.

These tests verify that the GUI components work correctly with the
playlist manager and player engine.
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


class TestGUIIntegration(unittest.TestCase):
    """Test GUI integration with playlist operations."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.playlist_file = os.path.join(self.temp_dir, "test_playlist.json")
        self.artwork_dir = os.path.join(self.temp_dir, "artwork")
        
        # Create test MP3 file path (we'll mock the actual file operations)
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
    
    @patch('models.song.Song.from_file')
    @patch('os.path.exists')
    @patch('os.access')
    def test_playlist_display_updates_when_songs_added(self, mock_access, mock_exists, mock_from_file):
        """Test that playlist display updates when songs are added."""
        # Mock file operations
        mock_exists.return_value = True
        mock_access.return_value = True
        
        # Mock song creation
        test_song = Song(
            file_path=self.test_mp3_path,
            title="Test Song",
            artist="Test Artist",
            album="Test Album"
        )
        mock_from_file.return_value = test_song
        
        # Initially playlist should be empty
        self.assertEqual(self.main_window.playlist_listbox.size(), 0)
        
        # Add a song
        success = self.playlist_manager.add_song(self.test_mp3_path)
        self.assertTrue(success)
        
        # Update GUI display
        self.main_window._update_playlist_display()
        
        # Check that listbox was updated
        self.assertEqual(self.main_window.playlist_listbox.size(), 1)
        
        # Check display text format
        display_text = self.main_window.playlist_listbox.get(0)
        self.assertIn("Test Artist - Test Song", display_text)
        self.assertIn("1.", display_text)  # Should show track number
    
    @patch('models.song.Song.from_file')
    @patch('os.path.exists')
    @patch('os.access')
    def test_playlist_selection_highlights_current_song(self, mock_access, mock_exists, mock_from_file):
        """Test that current song is highlighted in playlist."""
        # Mock file operations
        mock_exists.return_value = True
        mock_access.return_value = True
        
        # Create test songs
        songs = []
        for i in range(3):
            song = Song(
                file_path=f"{self.temp_dir}/song{i}.mp3",
                title=f"Song {i}",
                artist=f"Artist {i}",
                album="Test Album"
            )
            songs.append(song)
            mock_from_file.return_value = song
            self.playlist_manager.add_song(song.file_path)
        
        # Update display
        self.main_window._update_playlist_display()
        
        # Set current song to index 1
        self.playlist_manager.set_current_song(1)
        self.main_window._update_playlist_selection()
        
        # Check that correct item is selected
        selection = self.main_window.playlist_listbox.curselection()
        self.assertEqual(len(selection), 1)
        self.assertEqual(selection[0], 1)
    
    @patch('models.song.Song.from_file')
    @patch('os.path.exists')
    @patch('os.access')
    def test_double_click_plays_song(self, mock_access, mock_exists, mock_from_file):
        """Test that double-clicking a song starts playback."""
        # Mock file operations
        mock_exists.return_value = True
        mock_access.return_value = True
        
        # Create test song
        test_song = Song(
            file_path=self.test_mp3_path,
            title="Test Song",
            artist="Test Artist",
            album="Test Album"
        )
        mock_from_file.return_value = test_song
        
        # Add song to playlist
        self.playlist_manager.add_song(self.test_mp3_path)
        self.main_window._update_playlist_display()
        
        # Mock player engine methods
        with patch.object(self.player_engine, 'play_song') as mock_play:
            mock_play.return_value = True
            
            # Simulate double-click on first item
            self.main_window.playlist_listbox.selection_set(0)
            event = Mock()
            self.main_window._on_playlist_double_click(event)
            
            # Verify play_song was called
            mock_play.assert_called_once()
            called_song = mock_play.call_args[0][0]
            self.assertEqual(called_song.title, "Test Song")
    
    @patch('models.song.Song.from_file')
    @patch('os.path.exists')
    @patch('os.access')
    def test_drag_and_drop_reordering(self, mock_access, mock_exists, mock_from_file):
        """Test drag-and-drop reordering of playlist items."""
        # Mock file operations
        mock_exists.return_value = True
        mock_access.return_value = True
        
        # Create test songs
        songs = []
        for i in range(3):
            song = Song(
                file_path=f"{self.temp_dir}/song{i}.mp3",
                title=f"Song {i}",
                artist=f"Artist {i}",
                album="Test Album"
            )
            songs.append(song)
            mock_from_file.return_value = song
            self.playlist_manager.add_song(song.file_path)
        
        # Update display
        self.main_window._update_playlist_display()
        
        # Simulate drag from index 0 to index 2
        self.main_window._drag_start_index = 0
        
        # Mock event for drop at index 2
        event = Mock()
        event.y = 50  # Simulate y coordinate
        
        with patch.object(self.main_window.playlist_listbox, 'nearest') as mock_nearest:
            mock_nearest.return_value = 2
            
            # Simulate drop
            self.main_window._on_playlist_drop(event)
            
            # Check that reordering occurred
            reordered_songs = self.playlist_manager.get_songs()
            self.assertEqual(reordered_songs[2].title, "Song 0")  # First song moved to end
    
    @patch('os.path.exists')
    def test_current_song_display_updates(self, mock_exists):
        """Test that current song display updates correctly."""
        # Mock file existence
        mock_exists.return_value = True
        
        # Initially should show no song
        self.assertEqual(self.main_window.current_song_label.cget("text"), "No song selected")
        
        # Create a test song and set as current
        test_song = Song(
            file_path=self.test_mp3_path,
            title="Test Song",
            artist="Test Artist",
            album="Test Album"
        )
        
        # Add to playlist and set as current
        self.playlist_manager.get_playlist().songs.append(test_song)
        self.playlist_manager.set_current_song(0)
        
        # Update display
        self.main_window._update_current_song_display()
        
        # Check display text
        display_text = self.main_window.current_song_label.cget("text")
        self.assertIn("Test Artist - Test Song", display_text)
        self.assertIn("Test Album", display_text)
    
    def test_playback_controls_state_updates(self):
        """Test that playback control buttons update based on player state."""
        # Initially should be in stopped state
        self.main_window._update_playback_controls(PlaybackState.STOPPED)
        
        # Play button should be enabled, others disabled
        self.assertEqual(str(self.main_window.play_button.cget("state")), "normal")
        self.assertEqual(str(self.main_window.pause_button.cget("state")), "disabled")
        self.assertEqual(str(self.main_window.stop_button.cget("state")), "disabled")
        
        # Update to playing state
        self.main_window._update_playback_controls(PlaybackState.PLAYING)
        
        # Play button should be disabled, pause/stop enabled
        self.assertEqual(str(self.main_window.play_button.cget("state")), "disabled")
        self.assertEqual(str(self.main_window.pause_button.cget("state")), "normal")
        self.assertEqual(str(self.main_window.stop_button.cget("state")), "normal")
        
        # Update to paused state
        self.main_window._update_playback_controls(PlaybackState.PAUSED)
        
        # Play button should be enabled, pause disabled, stop enabled
        self.assertEqual(str(self.main_window.play_button.cget("state")), "normal")
        self.assertEqual(str(self.main_window.pause_button.cget("state")), "disabled")
        self.assertEqual(str(self.main_window.stop_button.cget("state")), "normal")
    
    def test_volume_control_updates_player(self):
        """Test that volume slider updates player engine volume."""
        with patch.object(self.player_engine, 'set_volume') as mock_set_volume:
            mock_set_volume.return_value = True
            
            # Simulate volume change
            self.main_window._on_volume_changed("0.5")
            
            # Verify set_volume was called
            mock_set_volume.assert_called_once_with(0.5)
    
    def test_loop_checkbox_updates_playlist_manager(self):
        """Test that loop checkbox updates playlist manager."""
        # Initially loop should be disabled
        self.assertFalse(self.playlist_manager.is_loop_enabled())
        
        # Enable loop via checkbox
        self.main_window.loop_var.set(True)
        self.main_window._on_loop_toggled()
        
        # Check that playlist manager was updated
        self.assertTrue(self.playlist_manager.is_loop_enabled())
        
        # Disable loop
        self.main_window.loop_var.set(False)
        self.main_window._on_loop_toggled()
        
        # Check that playlist manager was updated
        self.assertFalse(self.playlist_manager.is_loop_enabled())
    
    @patch('tkinter.filedialog.askopenfilenames')
    @patch('models.song.Song.from_file')
    @patch('os.path.exists')
    @patch('os.access')
    def test_add_songs_button_opens_file_dialog(self, mock_access, mock_exists, mock_from_file, mock_filedialog):
        """Test that add songs button opens file dialog and adds selected files."""
        # Mock file operations
        mock_exists.return_value = True
        mock_access.return_value = True
        mock_filedialog.return_value = [self.test_mp3_path]
        
        # Mock song creation
        test_song = Song(
            file_path=self.test_mp3_path,
            title="Test Song",
            artist="Test Artist",
            album="Test Album"
        )
        mock_from_file.return_value = test_song
        
        # Mock messagebox to avoid showing dialog
        with patch('tkinter.messagebox.showinfo') as mock_showinfo:
            # Click add songs button
            self.main_window._on_add_songs_clicked()
            
            # Verify file dialog was opened
            mock_filedialog.assert_called_once()
            
            # Verify song was added
            self.assertEqual(self.playlist_manager.get_song_count(), 1)
            
            # Verify success message was shown
            mock_showinfo.assert_called_once()
    
    @patch('models.song.Song.from_file')
    @patch('os.path.exists')
    @patch('os.access')
    @patch('tkinter.messagebox.askyesno')
    def test_remove_song_button_removes_selected_song(self, mock_askyesno, mock_access, mock_exists, mock_from_file):
        """Test that remove song button removes the selected song."""
        # Mock file operations
        mock_exists.return_value = True
        mock_access.return_value = True
        mock_askyesno.return_value = True  # User confirms removal
        
        # Create and add test song
        test_song = Song(
            file_path=self.test_mp3_path,
            title="Test Song",
            artist="Test Artist",
            album="Test Album"
        )
        mock_from_file.return_value = test_song
        self.playlist_manager.add_song(self.test_mp3_path)
        
        # Update display and select first item
        self.main_window._update_playlist_display()
        self.main_window.playlist_listbox.selection_set(0)
        
        # Click remove button
        self.main_window._on_remove_song_clicked()
        
        # Verify confirmation dialog was shown
        mock_askyesno.assert_called_once()
        
        # Verify song was removed
        self.assertEqual(self.playlist_manager.get_song_count(), 0)
    
    @patch('tkinter.messagebox.askyesno')
    @patch('os.path.exists')
    def test_clear_playlist_button_clears_all_songs(self, mock_exists, mock_askyesno):
        """Test that clear playlist button removes all songs."""
        mock_askyesno.return_value = True  # User confirms clearing
        mock_exists.return_value = True  # Mock file existence
        
        # Add some test songs directly to playlist
        for i in range(3):
            song = Song(
                file_path=f"{self.temp_dir}/song{i}.mp3",
                title=f"Song {i}",
                artist=f"Artist {i}",
                album="Test Album"
            )
            self.playlist_manager.get_playlist().songs.append(song)
        
        # Verify songs were added
        self.assertEqual(self.playlist_manager.get_song_count(), 3)
        
        # Click clear button
        self.main_window._on_clear_playlist_clicked()
        
        # Verify confirmation dialog was shown
        mock_askyesno.assert_called_once()
        
        # Verify playlist was cleared
        self.assertEqual(self.playlist_manager.get_song_count(), 0)
    
    @patch('tkinter.messagebox.showinfo')
    def test_save_playlist_button_saves_playlist(self, mock_showinfo):
        """Test that save playlist button saves the playlist."""
        with patch.object(self.playlist_manager, 'save_playlist') as mock_save:
            mock_save.return_value = True
            
            # Click save button
            self.main_window._on_save_playlist_clicked()
            
            # Verify save was called
            mock_save.assert_called_once()
            
            # Verify success message was shown
            mock_showinfo.assert_called_once()
    
    @patch('os.path.exists')
    def test_player_callbacks_update_gui(self, mock_exists):
        """Test that player engine callbacks update the GUI."""
        mock_exists.return_value = True
        
        # Test state change callback
        with patch.object(self.main_window, '_update_playback_controls') as mock_update_controls:
            self.main_window._on_playback_state_changed(PlaybackState.PLAYING)
            
            # Should schedule GUI update
            self.main_window.root.update()  # Process scheduled events
            mock_update_controls.assert_called_once_with(PlaybackState.PLAYING)
        
        # Test song change callback
        with patch.object(self.main_window, '_update_current_song_display') as mock_update_display:
            with patch.object(self.main_window, '_update_playlist_selection') as mock_update_selection:
                test_song = Song(
                    file_path=self.test_mp3_path,
                    title="Test Song",
                    artist="Test Artist",
                    album="Test Album"
                )
                
                self.main_window._on_song_changed(test_song)
                
                # Process scheduled events
                self.main_window.root.update()
                
                mock_update_display.assert_called_once()
                mock_update_selection.assert_called_once()
    
    @patch('tkinter.messagebox.showerror')
    def test_playback_error_shows_error_dialog(self, mock_showerror):
        """Test that playback errors show error dialog."""
        error_message = "Test error message"
        
        self.main_window._on_playback_error(error_message)
        
        # Process scheduled events
        self.main_window.root.update()
        
        # Verify error dialog was shown
        mock_showerror.assert_called_once()
        args = mock_showerror.call_args[0]
        self.assertIn(error_message, args)
    
    def test_window_close_saves_playlist_and_stops_playback(self):
        """Test that closing window saves playlist and stops playback."""
        with patch.object(self.playlist_manager, 'save_playlist') as mock_save:
            with patch.object(self.player_engine, 'stop') as mock_stop:
                mock_save.return_value = True
                mock_stop.return_value = True
                
                # Simulate window close
                self.main_window._on_window_close()
                
                # Verify save and stop were called
                mock_save.assert_called_once()
                mock_stop.assert_called_once()


if __name__ == '__main__':
    # Run tests
    unittest.main()