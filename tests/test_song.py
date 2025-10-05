"""
Unit tests for Song model.
"""

import unittest
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.song import Song


class TestSong(unittest.TestCase):
    """Test cases for Song model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.artwork_dir = os.path.join(self.temp_dir, "artwork")
        
        # Create a dummy MP3 file for testing
        self.test_mp3_path = os.path.join(self.temp_dir, "test_song.mp3")
        with open(self.test_mp3_path, 'wb') as f:
            f.write(b'dummy mp3 content')
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_song_creation_with_valid_data(self):
        """Test creating a Song with valid data."""
        song = Song(
            file_path=self.test_mp3_path,
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            duration=180.0
        )
        
        self.assertEqual(song.title, "Test Song")
        self.assertEqual(song.artist, "Test Artist")
        self.assertEqual(song.album, "Test Album")
        self.assertEqual(song.duration, 180.0)
        self.assertEqual(song.file_path, self.test_mp3_path)
    
    def test_song_creation_with_empty_file_path(self):
        """Test that Song creation fails with empty file path."""
        with self.assertRaises(ValueError):
            Song(
                file_path="",
                title="Test Song",
                artist="Test Artist",
                album="Test Album"
            )
    
    def test_song_creation_with_nonexistent_file(self):
        """Test that Song creation fails with nonexistent file."""
        with self.assertRaises(FileNotFoundError):
            Song(
                file_path="/nonexistent/file.mp3",
                title="Test Song",
                artist="Test Artist",
                album="Test Album"
            )
    
    @patch('models.song.MutagenFile')
    def test_from_file_with_metadata(self, mock_mutagen):
        """Test creating Song from file with metadata."""
        # Mock mutagen file with metadata
        mock_audio = MagicMock()
        mock_audio.__getitem__.side_effect = lambda key: {
            'TIT2': ['Test Title'],
            'TPE1': ['Test Artist'],
            'TALB': ['Test Album']
        }.get(key, [])
        mock_audio.__contains__.side_effect = lambda key: key in ['TIT2', 'TPE1', 'TALB']
        mock_audio.info.length = 240.0
        mock_mutagen.return_value = mock_audio
        
        song = Song.from_file(self.test_mp3_path)
        
        self.assertEqual(song.title, "Test Title")
        self.assertEqual(song.artist, "Test Artist")
        self.assertEqual(song.album, "Test Album")
        self.assertEqual(song.duration, 240.0)
        self.assertEqual(song.file_path, self.test_mp3_path)
    
    @patch('models.song.MutagenFile')
    def test_from_file_with_missing_metadata(self, mock_mutagen):
        """Test creating Song from file with missing metadata."""
        # Mock mutagen file with no metadata
        mock_audio = MagicMock()
        mock_audio.__getitem__.side_effect = KeyError()
        mock_audio.__contains__.return_value = False
        mock_audio.info.length = 0.0
        mock_mutagen.return_value = mock_audio
        
        song = Song.from_file(self.test_mp3_path)
        
        # Should use filename as title and defaults for missing fields
        self.assertEqual(song.title, "test_song")  # filename without extension
        self.assertEqual(song.artist, "Unknown Artist")
        self.assertEqual(song.album, "Unknown Album")
        self.assertEqual(song.duration, 0.0)
    
    @patch('models.song.MutagenFile')
    def test_from_file_with_corrupted_file(self, mock_mutagen):
        """Test creating Song from corrupted file."""
        # Mock mutagen returning None (corrupted file)
        mock_mutagen.return_value = None
        
        song = Song.from_file(self.test_mp3_path)
        
        # Should use filename as fallback
        self.assertEqual(song.title, "test_song")
        self.assertEqual(song.artist, "Unknown Artist")
        self.assertEqual(song.album, "Unknown Album")
    
    def test_to_dict(self):
        """Test converting Song to dictionary."""
        song = Song(
            file_path=self.test_mp3_path,
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            duration=180.0
        )
        
        expected_dict = {
            'file_path': self.test_mp3_path,
            'title': "Test Song",
            'artist': "Test Artist",
            'album': "Test Album",
            'artwork_path': None,
            'duration': 180.0
        }
        
        self.assertEqual(song.to_dict(), expected_dict)
    
    def test_from_dict(self):
        """Test creating Song from dictionary."""
        song_dict = {
            'file_path': self.test_mp3_path,
            'title': "Test Song",
            'artist': "Test Artist",
            'album': "Test Album",
            'artwork_path': None,
            'duration': 180.0
        }
        
        song = Song.from_dict(song_dict)
        
        self.assertEqual(song.title, "Test Song")
        self.assertEqual(song.artist, "Test Artist")
        self.assertEqual(song.album, "Test Album")
        self.assertEqual(song.duration, 180.0)
        self.assertEqual(song.file_path, self.test_mp3_path)
    
    def test_is_valid_with_existing_file(self):
        """Test is_valid returns True for existing file."""
        song = Song(
            file_path=self.test_mp3_path,
            title="Test Song",
            artist="Test Artist",
            album="Test Album"
        )
        
        self.assertTrue(song.is_valid())
    
    def test_is_valid_with_missing_file(self):
        """Test is_valid returns False for missing file."""
        # Create song with existing file first
        song = Song(
            file_path=self.test_mp3_path,
            title="Test Song",
            artist="Test Artist",
            album="Test Album"
        )
        
        # Remove the test file after creation
        os.remove(self.test_mp3_path)
        
        # Now is_valid should return False
        self.assertFalse(song.is_valid())
    
    def test_get_display_name_with_artist(self):
        """Test get_display_name with artist."""
        song = Song(
            file_path=self.test_mp3_path,
            title="Test Song",
            artist="Test Artist",
            album="Test Album"
        )
        
        self.assertEqual(song.get_display_name(), "Test Artist - Test Song")
    
    def test_get_display_name_without_artist(self):
        """Test get_display_name without artist."""
        song = Song(
            file_path=self.test_mp3_path,
            title="Test Song",
            artist="Unknown Artist",
            album="Test Album"
        )
        
        self.assertEqual(song.get_display_name(), "Test Song")
    
    def test_str_representation(self):
        """Test string representation of Song."""
        song = Song(
            file_path=self.test_mp3_path,
            title="Test Song",
            artist="Test Artist",
            album="Test Album"
        )
        
        self.assertEqual(str(song), "Test Artist - Test Song")
    
    def test_repr_representation(self):
        """Test repr representation of Song."""
        song = Song(
            file_path=self.test_mp3_path,
            title="Test Song",
            artist="Test Artist",
            album="Test Album"
        )
        
        expected_repr = f"Song(title='Test Song', artist='Test Artist', file_path='{self.test_mp3_path}')"
        self.assertEqual(repr(song), expected_repr)
    
    def test_get_tag_value_with_list(self):
        """Test _get_tag_value with list value."""
        mock_audio = {'TIT2': ['Test Title', 'Alternative Title']}
        result = Song._get_tag_value(mock_audio, ['TIT2'])
        self.assertEqual(result, "Test Title")
    
    def test_get_tag_value_with_string(self):
        """Test _get_tag_value with string value."""
        mock_audio = {'TIT2': 'Test Title'}
        result = Song._get_tag_value(mock_audio, ['TIT2'])
        self.assertEqual(result, "Test Title")
    
    def test_get_tag_value_with_multiple_keys(self):
        """Test _get_tag_value trying multiple keys."""
        mock_audio = {'TITLE': 'Test Title'}
        result = Song._get_tag_value(mock_audio, ['TIT2', 'TITLE'])
        self.assertEqual(result, "Test Title")
    
    def test_get_tag_value_not_found(self):
        """Test _get_tag_value when no keys found."""
        mock_audio = {}
        result = Song._get_tag_value(mock_audio, ['TIT2', 'TITLE'])
        self.assertEqual(result, "")


if __name__ == '__main__':
    unittest.main()