"""
Unit tests for PlayerEngine.
"""

import unittest
import tempfile
import os
import shutil
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, call

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.player_engine import PlayerEngine, PlaybackState
from models.song import Song
from models.playlist import Playlist


class TestPlayerEngine(unittest.TestCase):
    """Test cases for PlayerEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create dummy MP3 files for testing
        self.test_files = []
        for i in range(3):
            test_file = os.path.join(self.temp_dir, f"test_song_{i}.mp3")
            with open(test_file, 'wb') as f:
                f.write(b'dummy mp3 content')
            self.test_files.append(test_file)
        
        self.test_mp3_path = self.test_files[0]  # For backward compatibility
        
        # Create test songs and playlist
        self.test_songs = [
            Song(
                file_path=self.test_files[0],
                title="Song 1",
                artist="Artist 1",
                album="Album 1"
            ),
            Song(
                file_path=self.test_files[1],
                title="Song 2",
                artist="Artist 2",
                album="Album 2"
            ),
            Song(
                file_path=self.test_files[2],
                title="Song 3",
                artist="Artist 3",
                album="Album 3"
            )
        ]
        
        self.test_playlist = Playlist(songs=self.test_songs.copy())
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    @patch('core.player_engine.pygame')
    def test_player_engine_initialization(self, mock_pygame):
        """Test PlayerEngine initialization."""
        # Mock pygame mixer
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.USEREVENT = 24  # Typical pygame value
        
        player = PlayerEngine()
        
        # Verify initialization
        self.assertEqual(player.get_state(), PlaybackState.STOPPED)
        self.assertEqual(player.get_volume(), 0.7)
        self.assertIsNone(player.get_current_file())
        self.assertEqual(player.get_position(), 0.0)
        self.assertEqual(player.get_duration(), 0.0)
        
        # Verify pygame calls
        mock_pygame.mixer.pre_init.assert_called_once()
        mock_pygame.mixer.init.assert_called_once()
        mock_pygame.mixer.music.set_endevent.assert_called_once()
    
    @patch('core.player_engine.pygame')
    def test_player_engine_initialization_failure(self, mock_pygame):
        """Test PlayerEngine initialization failure."""
        # Mock pygame mixer failure
        mock_pygame.mixer.pre_init.side_effect = Exception("Mixer init failed")
        
        with self.assertRaises(RuntimeError):
            PlayerEngine()
    
    @patch('core.player_engine.pygame')
    def test_set_volume(self, mock_pygame):
        """Test setting volume."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.mixer.music.set_volume.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        
        # Test valid volume
        result = player.set_volume(0.5)
        self.assertTrue(result)
        self.assertEqual(player.get_volume(), 0.5)
        mock_pygame.mixer.music.set_volume.assert_called_with(0.5)
        
        # Test volume clamping
        player.set_volume(1.5)  # Should clamp to 1.0
        self.assertEqual(player.get_volume(), 1.0)
        
        player.set_volume(-0.5)  # Should clamp to 0.0
        self.assertEqual(player.get_volume(), 0.0)
    
    @patch('core.player_engine.pygame')
    def test_play_new_file(self, mock_pygame):
        """Test playing a new file."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.mixer.music.load.return_value = None
        mock_pygame.mixer.music.play.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        
        # Mock file duration
        with patch.object(player, '_get_file_duration', return_value=180.0):
            result = player.play(self.test_mp3_path)
        
        self.assertTrue(result)
        self.assertEqual(player.get_state(), PlaybackState.PLAYING)
        self.assertEqual(player.get_current_file(), self.test_mp3_path)
        self.assertTrue(player.is_playing())
        
        mock_pygame.mixer.music.load.assert_called_with(self.test_mp3_path)
        mock_pygame.mixer.music.play.assert_called_once()
    
    @patch('core.player_engine.pygame')
    def test_play_nonexistent_file(self, mock_pygame):
        """Test playing a nonexistent file."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        
        result = player.play("/nonexistent/file.mp3")
        
        self.assertFalse(result)
        self.assertEqual(player.get_state(), PlaybackState.STOPPED)
    
    @patch('core.player_engine.pygame')
    def test_pause_and_resume(self, mock_pygame):
        """Test pausing and resuming playback."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.mixer.music.load.return_value = None
        mock_pygame.mixer.music.play.return_value = None
        mock_pygame.mixer.music.pause.return_value = None
        mock_pygame.mixer.music.unpause.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        
        # Start playing
        with patch.object(player, '_get_file_duration', return_value=180.0):
            player.play(self.test_mp3_path)
        
        # Pause
        result = player.pause()
        self.assertTrue(result)
        self.assertEqual(player.get_state(), PlaybackState.PAUSED)
        self.assertTrue(player.is_paused())
        mock_pygame.mixer.music.pause.assert_called_once()
        
        # Resume
        result = player.play()
        self.assertTrue(result)
        self.assertEqual(player.get_state(), PlaybackState.PLAYING)
        mock_pygame.mixer.music.unpause.assert_called_once()
    
    @patch('core.player_engine.pygame')
    def test_stop(self, mock_pygame):
        """Test stopping playback."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.mixer.music.load.return_value = None
        mock_pygame.mixer.music.play.return_value = None
        mock_pygame.mixer.music.stop.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        
        # Start playing
        with patch.object(player, '_get_file_duration', return_value=180.0):
            player.play(self.test_mp3_path)
        
        # Stop
        result = player.stop()
        self.assertTrue(result)
        self.assertEqual(player.get_state(), PlaybackState.STOPPED)
        self.assertEqual(player.get_position(), 0.0)
        self.assertTrue(player.is_stopped())
        mock_pygame.mixer.music.stop.assert_called_once()
    
    @patch('core.player_engine.pygame')
    def test_state_queries(self, mock_pygame):
        """Test state query methods."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        
        # Initial state
        self.assertTrue(player.is_stopped())
        self.assertFalse(player.is_playing())
        self.assertFalse(player.is_paused())
        self.assertEqual(player.get_state(), PlaybackState.STOPPED)
    
    @patch('core.player_engine.pygame')
    def test_callbacks(self, mock_pygame):
        """Test event callbacks."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        
        # Set up callbacks
        finished_callback = MagicMock()
        error_callback = MagicMock()
        state_callback = MagicMock()
        
        player.set_on_playback_finished(finished_callback)
        player.set_on_playback_error(error_callback)
        player.set_on_state_changed(state_callback)
        
        # Trigger state change
        player._set_state(PlaybackState.PLAYING)
        state_callback.assert_called_with(PlaybackState.PLAYING)
        
        # Trigger error
        player._handle_error("Test error")
        error_callback.assert_called_with("Test error")
    
    @patch('core.player_engine.pygame')
    def test_get_file_duration(self, mock_pygame):
        """Test getting file duration."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        
        # Mock mutagen by patching the import inside the method
        with patch('mutagen.File') as mock_mutagen:
            mock_audio = MagicMock()
            mock_audio.info.length = 240.0
            mock_mutagen.return_value = mock_audio
            
            duration = player._get_file_duration(self.test_mp3_path)
            self.assertEqual(duration, 240.0)
        
        # Test with no mutagen available
        with patch('mutagen.File', side_effect=ImportError()):
            duration = player._get_file_duration(self.test_mp3_path)
            self.assertEqual(duration, 0.0)
    
    @patch('core.player_engine.pygame')
    def test_seek_not_supported(self, mock_pygame):
        """Test that seeking is not supported."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        
        result = player.seek(60.0)
        self.assertFalse(result)
    
    @patch('core.player_engine.pygame')
    def test_update_method(self, mock_pygame):
        """Test the update method for processing events."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.USEREVENT = 24
        
        # Mock pygame events
        mock_event = MagicMock()
        mock_event.type = 25  # USEREVENT + 1
        mock_pygame.event.get.return_value = [mock_event]
        
        player = PlayerEngine()
        player._state = PlaybackState.PLAYING
        
        # Set up callback
        finished_callback = MagicMock()
        player.set_on_playback_finished(finished_callback)
        
        # Call update
        player.update()
        
        # Should have processed the music end event
        finished_callback.assert_called_once()
        self.assertEqual(player.get_state(), PlaybackState.STOPPED)
    
    @patch('core.player_engine.pygame')
    def test_shutdown(self, mock_pygame):
        """Test player shutdown."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.mixer.music.stop.return_value = None
        mock_pygame.mixer.quit.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        
        player.shutdown()
        
        mock_pygame.mixer.quit.assert_called_once()
        self.assertEqual(player.get_state(), PlaybackState.STOPPED)
    
    @patch('core.player_engine.pygame')
    def test_get_info(self, mock_pygame):
        """Test getting player information."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        
        info = player.get_info()
        
        expected_keys = ['state', 'current_file', 'position', 'duration', 'volume', 
                        'is_playing', 'is_paused', 'is_stopped']
        
        for key in expected_keys:
            self.assertIn(key, info)
        
        self.assertEqual(info['state'], 'stopped')
        self.assertFalse(info['is_playing'])
        self.assertTrue(info['is_stopped'])
    
    @patch('core.player_engine.pygame')
    def test_string_representations(self, mock_pygame):
        """Test string representations."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        
        # Test without file
        str_repr = str(player)
        self.assertIn("no file loaded", str_repr)
        
        repr_str = repr(player)
        self.assertIn("PlayerEngine", repr_str)
        
        # Test with file
        player._current_file = self.test_mp3_path
        player._duration = 180.0
        
        str_repr = str(player)
        self.assertIn("test_song_0.mp3", str_repr)  # Updated to match actual filename
        self.assertIn("180.0s", str_repr)
    
    @patch('core.player_engine.pygame')
    def test_error_handling_in_callbacks(self, mock_pygame):
        """Test error handling in callbacks."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        
        # Set up callback that raises exception
        def failing_callback():
            raise Exception("Callback error")
        
        player.set_on_state_changed(failing_callback)
        
        # Should not raise exception, just log error
        player._set_state(PlaybackState.PLAYING)
        
        # Player should still work
        self.assertEqual(player.get_state(), PlaybackState.PLAYING)
    
    # Playlist Integration Tests
    
    @patch('core.player_engine.pygame')
    def test_set_playlist(self, mock_pygame):
        """Test setting a playlist."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        
        # Test setting playlist
        player.set_playlist(self.test_playlist)
        
        self.assertEqual(player.get_playlist(), self.test_playlist)
        self.assertIsNone(player.get_current_song())
    
    @patch('core.player_engine.pygame')
    def test_auto_advance_setting(self, mock_pygame):
        """Test auto-advance setting."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        
        # Default should be True
        self.assertTrue(player.is_auto_advance_enabled())
        
        # Test disabling
        player.set_auto_advance(False)
        self.assertFalse(player.is_auto_advance_enabled())
        
        # Test enabling
        player.set_auto_advance(True)
        self.assertTrue(player.is_auto_advance_enabled())
    
    @patch('core.player_engine.pygame')
    def test_play_song(self, mock_pygame):
        """Test playing a specific song."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.mixer.music.load.return_value = None
        mock_pygame.mixer.music.play.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        player.set_playlist(self.test_playlist)
        
        # Mock file duration
        with patch.object(player, '_get_file_duration', return_value=180.0):
            result = player.play_song(self.test_songs[1])
        
        self.assertTrue(result)
        self.assertEqual(player.get_current_song(), self.test_songs[1])
        self.assertEqual(player.get_playlist().current_index, 1)
        self.assertEqual(player.get_state(), PlaybackState.PLAYING)
    
    @patch('core.player_engine.pygame')
    def test_play_invalid_song(self, mock_pygame):
        """Test playing an invalid song."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        
        # Use existing song but mock is_valid to return False
        invalid_song = self.test_songs[0]
        
        # Mock is_valid to return False
        with patch.object(invalid_song, 'is_valid', return_value=False):
            result = player.play_song(invalid_song)
        
        self.assertFalse(result)
    
    @patch('core.player_engine.pygame')
    def test_next_song(self, mock_pygame):
        """Test advancing to next song."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.mixer.music.load.return_value = None
        mock_pygame.mixer.music.play.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        player.set_playlist(self.test_playlist)
        
        # Mock file duration
        with patch.object(player, '_get_file_duration', return_value=180.0):
            # Start with first song
            player.play_song(self.test_songs[0])
            
            # Advance to next
            result = player.next_song()
        
        self.assertTrue(result)
        self.assertEqual(player.get_current_song(), self.test_songs[1])
        self.assertEqual(player.get_playlist().current_index, 1)
    
    @patch('core.player_engine.pygame')
    def test_next_song_no_playlist(self, mock_pygame):
        """Test next song without playlist."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        
        result = player.next_song()
        
        self.assertFalse(result)
    
    @patch('core.player_engine.pygame')
    def test_previous_song(self, mock_pygame):
        """Test going to previous song."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.mixer.music.load.return_value = None
        mock_pygame.mixer.music.play.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        player.set_playlist(self.test_playlist)
        
        # Mock file duration
        with patch.object(player, '_get_file_duration', return_value=180.0):
            # Start with second song
            player.play_song(self.test_songs[1])
            
            # Go to previous
            result = player.previous_song()
        
        self.assertTrue(result)
        self.assertEqual(player.get_current_song(), self.test_songs[0])
        self.assertEqual(player.get_playlist().current_index, 0)
    
    @patch('core.player_engine.pygame')
    def test_play_current_playlist_song(self, mock_pygame):
        """Test playing current song from playlist."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.mixer.music.load.return_value = None
        mock_pygame.mixer.music.play.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        player.set_playlist(self.test_playlist)
        
        # Mock file duration
        with patch.object(player, '_get_file_duration', return_value=180.0):
            result = player.play_current_playlist_song()
        
        self.assertTrue(result)
        self.assertEqual(player.get_current_song(), self.test_songs[0])
        self.assertEqual(player.get_state(), PlaybackState.PLAYING)
    
    @patch('core.player_engine.pygame')
    def test_song_changed_callback(self, mock_pygame):
        """Test song changed callback."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.mixer.music.load.return_value = None
        mock_pygame.mixer.music.play.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        player.set_playlist(self.test_playlist)
        
        # Set up callback
        song_changed_callback = MagicMock()
        player.set_on_song_changed(song_changed_callback)
        
        # Mock file duration
        with patch.object(player, '_get_file_duration', return_value=180.0):
            player.play_song(self.test_songs[0])
        
        song_changed_callback.assert_called_with(self.test_songs[0])
    
    @patch('core.player_engine.pygame')
    def test_auto_advance_on_song_finish(self, mock_pygame):
        """Test automatic advancement when song finishes."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.mixer.music.load.return_value = None
        mock_pygame.mixer.music.play.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        player.set_playlist(self.test_playlist)
        player.set_auto_advance(True)
        
        # Mock file duration and play first song
        with patch.object(player, '_get_file_duration', return_value=180.0):
            player.play_song(self.test_songs[0])
            
            # Simulate song finishing
            player._handle_song_finished()
        
        # Should have advanced to next song
        self.assertEqual(player.get_current_song(), self.test_songs[1])
        self.assertEqual(player.get_playlist().current_index, 1)
    
    @patch('core.player_engine.pygame')
    def test_no_auto_advance_on_song_finish(self, mock_pygame):
        """Test no advancement when auto-advance is disabled."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.mixer.music.load.return_value = None
        mock_pygame.mixer.music.play.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        player.set_playlist(self.test_playlist)
        player.set_auto_advance(False)
        
        # Mock file duration and play first song
        with patch.object(player, '_get_file_duration', return_value=180.0):
            player.play_song(self.test_songs[0])
            original_song = player.get_current_song()
            
            # Simulate song finishing
            player._handle_song_finished()
        
        # Should not have advanced
        self.assertEqual(player.get_current_song(), original_song)
        self.assertEqual(player.get_playlist().current_index, 0)
    
    @patch('core.player_engine.pygame')
    def test_playlist_loop_behavior(self, mock_pygame):
        """Test playlist looping behavior."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.mixer.music.load.return_value = None
        mock_pygame.mixer.music.play.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        self.test_playlist.loop_enabled = True
        player.set_playlist(self.test_playlist)
        
        # Mock file duration and play last song
        with patch.object(player, '_get_file_duration', return_value=180.0):
            player.play_song(self.test_songs[2])  # Last song
            
            # Advance to next (should loop to first)
            result = player.next_song()
        
        self.assertTrue(result)
        self.assertEqual(player.get_current_song(), self.test_songs[0])
        self.assertEqual(player.get_playlist().current_index, 0)
    
    @patch('core.player_engine.pygame')
    def test_get_info_with_playlist(self, mock_pygame):
        """Test get_info with playlist information."""
        mock_pygame.mixer.pre_init.return_value = None
        mock_pygame.mixer.init.return_value = None
        mock_pygame.mixer.music.set_endevent.return_value = None
        mock_pygame.mixer.music.load.return_value = None
        mock_pygame.mixer.music.play.return_value = None
        mock_pygame.USEREVENT = 24
        
        player = PlayerEngine()
        player.set_playlist(self.test_playlist)
        
        # Mock file duration and play a song
        with patch.object(player, '_get_file_duration', return_value=180.0):
            player.play_song(self.test_songs[1])
        
        info = player.get_info()
        
        # Check playlist info
        self.assertIn('playlist', info)
        self.assertIn('current_song', info)
        self.assertIn('auto_advance', info)
        
        playlist_info = info['playlist']
        self.assertEqual(playlist_info['total_songs'], 3)
        self.assertEqual(playlist_info['current_index'], 1)
        
        song_info = info['current_song']
        self.assertEqual(song_info['title'], 'Song 2')
        self.assertEqual(song_info['artist'], 'Artist 2')


if __name__ == '__main__':
    unittest.main()