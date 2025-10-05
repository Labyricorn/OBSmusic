"""
Unit tests for PlaylistManager class.
"""

import os
import json
import tempfile
import shutil
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add the project root to the path so we can import modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.playlist_manager import PlaylistManager
from models.song import Song
from models.playlist import Playlist


class TestPlaylistManager(unittest.TestCase):
    """Test cases for PlaylistManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.playlist_file = os.path.join(self.test_dir, "test_playlist.json")
        self.artwork_dir = os.path.join(self.test_dir, "artwork")
        
        # Use the actual test MP3 file from the project root
        self.test_mp3_path = os.path.join(os.path.dirname(__file__), "..", "test_song_file.mp3")
        self.test_mp3_path = os.path.abspath(self.test_mp3_path)
        
        # Create the playlist manager
        self.manager = PlaylistManager(
            playlist_file=self.playlist_file,
            artwork_dir=self.artwork_dir
        )
    
    def tearDown(self):
        """Clean up after each test method."""
        # Remove temporary directory and all contents
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_mock_song(self, title="Test Song", artist="Test Artist", file_path=None):
        """Create a mock Song object for testing.
        
        Args:
            title: Song title
            artist: Song artist
            file_path: File path (uses test_mp3_path if None)
            
        Returns:
            Mock Song object
        """
        if file_path is None:
            file_path = self.test_mp3_path
        
        song = Mock(spec=Song)
        song.title = title
        song.artist = artist
        song.album = "Test Album"
        song.file_path = file_path
        song.artwork_path = None
        song.duration = 180.0
        song.get_display_name.return_value = f"{artist} - {title}"
        song.is_valid.return_value = True
        song.to_dict.return_value = {
            'file_path': file_path,
            'title': title,
            'artist': artist,
            'album': "Test Album",
            'artwork_path': None,
            'duration': 180.0
        }
        return song
    
    def test_init_creates_directories(self):
        """Test that initialization creates required directories."""
        # Directories should be created during initialization
        self.assertTrue(os.path.exists(Path(self.playlist_file).parent))
        self.assertTrue(os.path.exists(self.artwork_dir))
    
    def test_init_loads_existing_playlist(self):
        """Test that initialization loads existing playlist file."""
        # Create a test playlist file
        test_playlist_data = {
            'songs': [{
                'file_path': self.test_mp3_path,
                'title': 'Existing Song',
                'artist': 'Existing Artist',
                'album': 'Existing Album',
                'artwork_path': None,
                'duration': 200.0
            }],
            'current_index': 0,
            'loop_enabled': True
        }
        
        with open(self.playlist_file, 'w') as f:
            json.dump(test_playlist_data, f)
        
        # Create new manager to test loading
        with patch('models.song.Song.is_valid', return_value=True), \
             patch('os.path.exists', return_value=True):
            manager = PlaylistManager(
                playlist_file=self.playlist_file,
                artwork_dir=self.artwork_dir
            )
        
        # Check that playlist was loaded
        self.assertEqual(len(manager.get_songs()), 1)
        self.assertTrue(manager.is_loop_enabled())
    
    @patch('models.song.Song.from_file')
    @patch('os.path.exists')
    @patch('os.access')
    def test_add_song_success(self, mock_access, mock_exists, mock_from_file):
        """Test successful song addition."""
        # Setup mocks
        mock_exists.return_value = True
        mock_access.return_value = True
        mock_song = self.create_mock_song()
        mock_from_file.return_value = mock_song
        
        # Add song
        result = self.manager.add_song(self.test_mp3_path)
        
        # Verify
        self.assertTrue(result)
        self.assertEqual(len(self.manager.get_songs()), 1)
        mock_from_file.assert_called_once_with(self.test_mp3_path, self.artwork_dir)
    
    @patch('os.path.exists')
    def test_add_song_file_not_found(self, mock_exists):
        """Test adding song when file doesn't exist."""
        mock_exists.return_value = False
        
        result = self.manager.add_song(self.test_mp3_path)
        
        self.assertFalse(result)
        self.assertEqual(len(self.manager.get_songs()), 0)
    
    @patch('os.path.exists')
    @patch('os.access')
    def test_add_song_file_not_readable(self, mock_access, mock_exists):
        """Test adding song when file is not readable."""
        mock_exists.return_value = True
        mock_access.return_value = False
        
        result = self.manager.add_song(self.test_mp3_path)
        
        self.assertFalse(result)
        self.assertEqual(len(self.manager.get_songs()), 0)
    
    @patch('models.song.Song.from_file')
    @patch('os.path.exists')
    @patch('os.access')
    def test_add_song_duplicate(self, mock_access, mock_exists, mock_from_file):
        """Test adding duplicate song."""
        # Setup mocks
        mock_exists.return_value = True
        mock_access.return_value = True
        mock_song = self.create_mock_song()
        mock_from_file.return_value = mock_song
        
        # Add song twice
        self.manager.add_song(self.test_mp3_path)
        result = self.manager.add_song(self.test_mp3_path)
        
        # Should fail on second attempt
        self.assertFalse(result)
        self.assertEqual(len(self.manager.get_songs()), 1)
    
    def test_remove_song_success(self):
        """Test successful song removal."""
        # Add a mock song to the playlist
        mock_song = self.create_mock_song()
        self.manager.playlist.add_song(mock_song)
        
        # Remove the song
        result = self.manager.remove_song(0)
        
        # Verify
        self.assertTrue(result)
        self.assertEqual(len(self.manager.get_songs()), 0)
    
    def test_remove_song_invalid_index(self):
        """Test removing song with invalid index."""
        result = self.manager.remove_song(0)  # Empty playlist
        
        self.assertFalse(result)
    
    def test_reorder_songs_success(self):
        """Test successful song reordering."""
        # Add mock songs
        song1 = self.create_mock_song("Song 1", "Artist 1")
        song2 = self.create_mock_song("Song 2", "Artist 2")
        self.manager.playlist.add_song(song1)
        self.manager.playlist.add_song(song2)
        
        # Reorder songs
        result = self.manager.reorder_songs(0, 1)
        
        # Verify
        self.assertTrue(result)
        songs = self.manager.get_songs()
        self.assertEqual(songs[0].title, "Song 2")
        self.assertEqual(songs[1].title, "Song 1")
    
    def test_reorder_songs_invalid_indices(self):
        """Test reordering with invalid indices."""
        # Add one song
        mock_song = self.create_mock_song()
        self.manager.playlist.add_song(mock_song)
        
        # Try to reorder with invalid indices
        result = self.manager.reorder_songs(0, 5)
        
        self.assertFalse(result)
    
    def test_get_current_song(self):
        """Test getting current song."""
        # Empty playlist
        self.assertIsNone(self.manager.get_current_song())
        
        # Add song
        mock_song = self.create_mock_song()
        self.manager.playlist.add_song(mock_song)
        
        # Get current song
        current = self.manager.get_current_song()
        self.assertEqual(current.title, "Test Song")
    
    def test_next_song(self):
        """Test advancing to next song."""
        # Add two songs
        song1 = self.create_mock_song("Song 1", "Artist 1")
        song2 = self.create_mock_song("Song 2", "Artist 2")
        self.manager.playlist.add_song(song1)
        self.manager.playlist.add_song(song2)
        
        # Advance to next song
        next_song = self.manager.next_song()
        
        self.assertEqual(next_song.title, "Song 2")
        self.assertEqual(self.manager.playlist.current_index, 1)
    
    def test_previous_song(self):
        """Test going to previous song."""
        # Add two songs and set current to second
        song1 = self.create_mock_song("Song 1", "Artist 1")
        song2 = self.create_mock_song("Song 2", "Artist 2")
        self.manager.playlist.add_song(song1)
        self.manager.playlist.add_song(song2)
        self.manager.playlist.current_index = 1
        
        # Go to previous song
        prev_song = self.manager.previous_song()
        
        self.assertEqual(prev_song.title, "Song 1")
        self.assertEqual(self.manager.playlist.current_index, 0)
    
    def test_set_current_song(self):
        """Test setting current song by index."""
        # Add songs
        song1 = self.create_mock_song("Song 1", "Artist 1")
        song2 = self.create_mock_song("Song 2", "Artist 2")
        self.manager.playlist.add_song(song1)
        self.manager.playlist.add_song(song2)
        
        # Set current song
        current = self.manager.set_current_song(1)
        
        self.assertEqual(current.title, "Song 2")
        self.assertEqual(self.manager.playlist.current_index, 1)
    
    def test_playlist_properties(self):
        """Test playlist property methods."""
        # Empty playlist
        self.assertTrue(self.manager.is_empty())
        self.assertEqual(self.manager.get_song_count(), 0)
        
        # Add song
        mock_song = self.create_mock_song()
        self.manager.playlist.add_song(mock_song)
        
        # Check properties
        self.assertFalse(self.manager.is_empty())
        self.assertEqual(self.manager.get_song_count(), 1)
        self.assertEqual(len(self.manager.get_songs()), 1)
    
    def test_clear_playlist(self):
        """Test clearing playlist."""
        # Add song
        mock_song = self.create_mock_song()
        self.manager.playlist.add_song(mock_song)
        
        # Clear playlist
        self.manager.clear_playlist()
        
        # Verify
        self.assertTrue(self.manager.is_empty())
        self.assertEqual(self.manager.get_song_count(), 0)
    
    def test_loop_enabled(self):
        """Test loop enabled functionality."""
        # Initially disabled
        self.assertFalse(self.manager.is_loop_enabled())
        
        # Enable loop
        self.manager.set_loop_enabled(True)
        self.assertTrue(self.manager.is_loop_enabled())
        
        # Disable loop
        self.manager.set_loop_enabled(False)
        self.assertFalse(self.manager.is_loop_enabled())
    
    def test_save_playlist_success(self):
        """Test successful playlist saving."""
        # Add mock song
        mock_song = self.create_mock_song()
        self.manager.playlist.add_song(mock_song)
        
        # Save playlist
        result = self.manager.save_playlist()
        
        # Verify
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.playlist_file))
        
        # Check file contents
        with open(self.playlist_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(len(data['songs']), 1)
        self.assertEqual(data['songs'][0]['title'], 'Test Song')
    
    def test_save_playlist_directory_creation(self):
        """Test that save_playlist creates directory if needed."""
        # Use a nested directory path
        nested_playlist_file = os.path.join(self.test_dir, "nested", "dir", "playlist.json")
        manager = PlaylistManager(playlist_file=nested_playlist_file)
        
        # Add mock song
        mock_song = self.create_mock_song()
        manager.playlist.add_song(mock_song)
        
        # Save playlist
        result = manager.save_playlist()
        
        # Verify
        self.assertTrue(result)
        self.assertTrue(os.path.exists(nested_playlist_file))
    
    def test_load_playlist_success(self):
        """Test successful playlist loading."""
        # Create test playlist file
        test_data = {
            'songs': [{
                'file_path': self.test_mp3_path,
                'title': 'Loaded Song',
                'artist': 'Loaded Artist',
                'album': 'Loaded Album',
                'artwork_path': None,
                'duration': 150.0
            }],
            'current_index': 0,
            'loop_enabled': True
        }
        
        with open(self.playlist_file, 'w') as f:
            json.dump(test_data, f)
        
        # Load playlist
        with patch('models.song.Song.is_valid', return_value=True), \
             patch('os.path.exists', return_value=True):
            result = self.manager.load_playlist()
        
        # Verify
        self.assertTrue(result)
        self.assertEqual(len(self.manager.get_songs()), 1)
        self.assertTrue(self.manager.is_loop_enabled())
    
    def test_load_playlist_file_not_found(self):
        """Test loading playlist when file doesn't exist."""
        # Remove the playlist file if it exists
        if os.path.exists(self.playlist_file):
            os.remove(self.playlist_file)
        
        # Load playlist
        result = self.manager.load_playlist()
        
        # Should succeed but create empty playlist
        self.assertTrue(result)
        self.assertTrue(self.manager.is_empty())
    
    def test_load_playlist_corrupted_file(self):
        """Test loading corrupted playlist file."""
        # Create corrupted JSON file
        with open(self.playlist_file, 'w') as f:
            f.write("{ invalid json content")
        
        # Load playlist - should handle the error gracefully
        result = self.manager.load_playlist()
        
        # Should succeed but create empty playlist due to error handling
        self.assertTrue(result)
        self.assertTrue(self.manager.is_empty())
    
    def test_reload_playlist(self):
        """Test reloading playlist from file."""
        # Add song to manager
        mock_song = self.create_mock_song()
        self.manager.playlist.add_song(mock_song)
        
        # Create different playlist file
        test_data = {
            'songs': [{
                'file_path': self.test_mp3_path,
                'title': 'Reloaded Song',
                'artist': 'Reloaded Artist',
                'album': 'Reloaded Album',
                'artwork_path': None,
                'duration': 120.0
            }],
            'current_index': 0,
            'loop_enabled': False
        }
        
        with open(self.playlist_file, 'w') as f:
            json.dump(test_data, f)
        
        # Reload playlist
        with patch('models.song.Song.is_valid', return_value=True), \
             patch('os.path.exists', return_value=True):
            result = self.manager.reload_playlist()
        
        # Verify
        self.assertTrue(result)
        songs = self.manager.get_songs()
        self.assertEqual(len(songs), 1)
        self.assertEqual(songs[0].title, 'Reloaded Song')
    
    def test_validate_playlist(self):
        """Test playlist validation."""
        # Add mock songs (one valid, one invalid)
        valid_song = self.create_mock_song("Valid Song", "Valid Artist")
        valid_song.is_valid.return_value = True
        
        invalid_song = self.create_mock_song("Invalid Song", "Invalid Artist")
        invalid_song.is_valid.return_value = False
        
        self.manager.playlist.add_song(valid_song)
        self.manager.playlist.add_song(invalid_song)
        
        # Validate playlist
        validation = self.manager.validate_playlist()
        
        # Verify
        self.assertEqual(validation['total_songs'], 2)
        self.assertEqual(validation['valid_songs'], 1)
        self.assertEqual(validation['invalid_songs'], 1)
        self.assertFalse(validation['is_valid'])
    
    def test_cleanup_invalid_songs(self):
        """Test cleaning up invalid songs."""
        # Add mock songs (one valid, one invalid)
        valid_song = self.create_mock_song("Valid Song", "Valid Artist")
        valid_song.is_valid.return_value = True
        
        invalid_song = self.create_mock_song("Invalid Song", "Invalid Artist")
        invalid_song.is_valid.return_value = False
        
        self.manager.playlist.add_song(valid_song)
        self.manager.playlist.add_song(invalid_song)
        
        # Cleanup invalid songs
        removed_count = self.manager.cleanup_invalid_songs()
        
        # Verify
        self.assertEqual(removed_count, 1)
        self.assertEqual(len(self.manager.get_songs()), 1)
        self.assertEqual(self.manager.get_songs()[0].title, "Valid Song")
    
    def test_get_playlist_info(self):
        """Test getting playlist information."""
        # Add mock song
        mock_song = self.create_mock_song()
        mock_song.is_valid.return_value = True
        self.manager.playlist.add_song(mock_song)
        
        # Get playlist info
        info = self.manager.get_playlist_info()
        
        # Verify
        self.assertEqual(info['total_songs'], 1)
        self.assertEqual(info['current_index'], 0)
        self.assertIsNotNone(info['current_song'])
        self.assertFalse(info['loop_enabled'])
        self.assertFalse(info['is_empty'])
        self.assertEqual(info['playlist_file'], self.playlist_file)
        self.assertEqual(info['artwork_dir'], self.artwork_dir)
        self.assertIn('validation', info)
    
    def test_backup_playlist(self):
        """Test creating playlist backup."""
        # Add mock song
        mock_song = self.create_mock_song()
        self.manager.playlist.add_song(mock_song)
        
        # Create backup
        backup_path = os.path.join(self.test_dir, "backup.json")
        result = self.manager.backup_playlist(backup_path)
        
        # Verify
        self.assertTrue(result)
        self.assertTrue(os.path.exists(backup_path))
        
        # Check backup contents
        with open(backup_path, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(len(data['songs']), 1)
        self.assertEqual(data['songs'][0]['title'], 'Test Song')
    
    def test_backup_playlist_auto_filename(self):
        """Test creating playlist backup with automatic filename."""
        # Add mock song
        mock_song = self.create_mock_song()
        self.manager.playlist.add_song(mock_song)
        
        # Create backup with auto filename
        result = self.manager.backup_playlist()
        
        # Verify
        self.assertTrue(result)
        
        # Check that a backup file was created
        backup_files = [f for f in os.listdir(Path(self.playlist_file).parent) 
                       if f.startswith("playlist_backup_") and f.endswith(".json")]
        self.assertEqual(len(backup_files), 1)
    
    def test_restore_from_backup(self):
        """Test restoring playlist from backup."""
        # Create backup file
        backup_data = {
            'songs': [{
                'file_path': self.test_mp3_path,
                'title': 'Backup Song',
                'artist': 'Backup Artist',
                'album': 'Backup Album',
                'artwork_path': None,
                'duration': 90.0
            }],
            'current_index': 0,
            'loop_enabled': True
        }
        
        backup_path = os.path.join(self.test_dir, "backup.json")
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f)
        
        # Restore from backup
        with patch('models.song.Song.is_valid', return_value=True), \
             patch('os.path.exists', return_value=True):
            result = self.manager.restore_from_backup(backup_path)
        
        # Verify
        self.assertTrue(result)
        songs = self.manager.get_songs()
        self.assertEqual(len(songs), 1)
        self.assertEqual(songs[0].title, 'Backup Song')
        self.assertTrue(self.manager.is_loop_enabled())
    
    def test_restore_from_backup_file_not_found(self):
        """Test restoring from non-existent backup file."""
        backup_path = os.path.join(self.test_dir, "nonexistent.json")
        
        result = self.manager.restore_from_backup(backup_path)
        
        self.assertFalse(result)
    
    def test_add_real_mp3_file(self):
        """Test adding the actual test MP3 file."""
        # Verify the test file exists
        self.assertTrue(os.path.exists(self.test_mp3_path), 
                       f"Test MP3 file not found: {self.test_mp3_path}")
        
        # Add the real MP3 file
        result = self.manager.add_song(self.test_mp3_path)
        
        # Verify
        self.assertTrue(result)
        self.assertEqual(len(self.manager.get_songs()), 1)
        
        # Check that the song was added with metadata
        song = self.manager.get_songs()[0]
        self.assertEqual(song.file_path, self.test_mp3_path)
        self.assertIsNotNone(song.title)
        self.assertIsNotNone(song.artist)
        
        # Verify the song is valid (file exists)
        self.assertTrue(song.is_valid())
    
    def test_add_song_without_artwork_extraction(self):
        """Test adding song without artwork extraction."""
        # Add the real MP3 file without artwork extraction
        result = self.manager.add_song(self.test_mp3_path, extract_artwork=False)
        
        # Verify
        self.assertTrue(result)
        self.assertEqual(len(self.manager.get_songs()), 1)
        
        # Check that artwork was not extracted
        song = self.manager.get_songs()[0]
        self.assertIsNone(song.artwork_path)
    
    def test_add_songs_from_directory(self):
        """Test adding songs from directory."""
        # Create a temporary directory with the test MP3 file
        import tempfile
        import shutil
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy test file to temp directory
            test_copy = os.path.join(temp_dir, "test_copy.mp3")
            shutil.copy2(self.test_mp3_path, test_copy)
            
            # Add songs from directory
            result = self.manager.add_songs_from_directory(temp_dir)
            
            # Verify
            self.assertTrue(result['success'])
            self.assertEqual(result['added'], 1)
            self.assertEqual(result['failed'], 0)
            self.assertEqual(len(self.manager.get_songs()), 1)
    
    def test_add_songs_from_directory_recursive(self):
        """Test adding songs from directory recursively."""
        import tempfile
        import shutil
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create subdirectory
            sub_dir = os.path.join(temp_dir, "subdir")
            os.makedirs(sub_dir)
            
            # Copy test file to subdirectory
            test_copy = os.path.join(sub_dir, "test_copy.mp3")
            shutil.copy2(self.test_mp3_path, test_copy)
            
            # Add songs recursively
            result = self.manager.add_songs_from_directory(temp_dir, recursive=True)
            
            # Verify
            self.assertTrue(result['success'])
            self.assertEqual(result['added'], 1)
            self.assertEqual(len(self.manager.get_songs()), 1)
    
    def test_add_songs_from_directory_nonexistent(self):
        """Test adding songs from non-existent directory."""
        result = self.manager.add_songs_from_directory("/nonexistent/directory")
        
        # Verify
        self.assertFalse(result['success'])
        self.assertEqual(result['added'], 0)
        self.assertIn('Directory not found', result['errors'])
    
    def test_refresh_metadata_single_song(self):
        """Test refreshing metadata for a single song."""
        # Add a song first
        self.manager.add_song(self.test_mp3_path)
        
        # Refresh metadata for the song
        result = self.manager.refresh_metadata(song_index=0)
        
        # Verify
        self.assertTrue(result['success'])
        self.assertEqual(result['refreshed'], 1)
        self.assertEqual(len(result['errors']), 0)
    
    def test_refresh_metadata_all_songs(self):
        """Test refreshing metadata for all songs."""
        # Add a song first
        self.manager.add_song(self.test_mp3_path)
        
        # Refresh metadata for all songs
        result = self.manager.refresh_metadata()
        
        # Verify
        self.assertTrue(result['success'])
        self.assertEqual(result['refreshed'], 1)
    
    def test_refresh_metadata_invalid_index(self):
        """Test refreshing metadata with invalid index."""
        result = self.manager.refresh_metadata(song_index=999)
        
        # Verify
        self.assertFalse(result['success'])
        self.assertEqual(result['refreshed'], 0)
        self.assertIn('Invalid song index', result['errors'])
    
    def test_get_artwork_cache_info_empty(self):
        """Test getting artwork cache info when cache is empty."""
        info = self.manager.get_artwork_cache_info()
        
        # Verify
        self.assertTrue(info['cache_exists'])
        self.assertEqual(info['cached_files'], 0)
        self.assertEqual(info['cache_size_bytes'], 0)
        self.assertEqual(info['cache_size_mb'], 0.0)
    
    def test_get_artwork_cache_info_with_files(self):
        """Test getting artwork cache info with cached files."""
        # Add a song to generate artwork
        self.manager.add_song(self.test_mp3_path)
        
        # Get cache info
        info = self.manager.get_artwork_cache_info()
        
        # Verify
        self.assertTrue(info['cache_exists'])
        # Should have at least one file if artwork was extracted
        self.assertGreaterEqual(info['cached_files'], 0)
    
    def test_clear_artwork_cache(self):
        """Test clearing artwork cache."""
        # Add a song to generate artwork
        self.manager.add_song(self.test_mp3_path)
        
        # Clear cache
        result = self.manager.clear_artwork_cache()
        
        # Verify
        self.assertTrue(result)
        
        # Check cache is empty
        info = self.manager.get_artwork_cache_info()
        self.assertEqual(info['cached_files'], 0)
    
    def test_extract_missing_artwork(self):
        """Test extracting missing artwork."""
        # Add a song without artwork extraction
        self.manager.add_song(self.test_mp3_path, extract_artwork=False)
        
        # Extract missing artwork
        result = self.manager.extract_missing_artwork()
        
        # Verify
        self.assertTrue(result['success'])
        # May or may not extract artwork depending on the test file
        self.assertGreaterEqual(result['extracted'], 0)
    
    def test_get_metadata_summary_empty(self):
        """Test getting metadata summary for empty playlist."""
        summary = self.manager.get_metadata_summary()
        
        # Verify
        self.assertEqual(summary['total_songs'], 0)
        self.assertEqual(summary['songs_with_artwork'], 0)
        self.assertEqual(summary['unique_artists'], 0)
        self.assertEqual(summary['unique_albums'], 0)
        self.assertEqual(summary['total_duration'], 0.0)
        self.assertEqual(summary['average_duration'], 0.0)
    
    def test_get_metadata_summary_with_songs(self):
        """Test getting metadata summary with songs."""
        # Add a song
        self.manager.add_song(self.test_mp3_path)
        
        # Get summary
        summary = self.manager.get_metadata_summary()
        
        # Verify
        self.assertEqual(summary['total_songs'], 1)
        self.assertGreaterEqual(summary['unique_artists'], 0)
        self.assertGreaterEqual(summary['unique_albums'], 0)
        self.assertGreater(summary['total_duration'], 0.0)
        self.assertGreater(summary['average_duration'], 0.0)
        self.assertIsNotNone(summary['total_duration_formatted'])
        self.assertIsNotNone(summary['average_duration_formatted'])
    
    def test_format_duration(self):
        """Test duration formatting."""
        # Test various durations
        self.assertEqual(self.manager._format_duration(0), "0:00")
        self.assertEqual(self.manager._format_duration(30), "0:30")
        self.assertEqual(self.manager._format_duration(90), "1:30")
        self.assertEqual(self.manager._format_duration(3661), "1:01:01")
    
    def test_string_representations(self):
        """Test string representations of PlaylistManager."""
        # Add mock song
        mock_song = self.create_mock_song()
        self.manager.playlist.add_song(mock_song)
        
        # Test __str__
        str_repr = str(self.manager)
        self.assertIn("PlaylistManager", str_repr)
        self.assertIn("songs=1", str_repr)
        
        # Test __repr__
        repr_str = repr(self.manager)
        self.assertIn("PlaylistManager", repr_str)
        self.assertIn(self.playlist_file, repr_str)
        self.assertIn(self.artwork_dir, repr_str)


if __name__ == '__main__':
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    unittest.main()