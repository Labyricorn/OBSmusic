"""
Unit tests for Playlist model.
"""

import unittest
import tempfile
import os
import json
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.playlist import Playlist
from models.song import Song


class TestPlaylist(unittest.TestCase):
    """Test cases for Playlist model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test MP3 files
        self.test_files = []
        for i in range(3):
            test_file = os.path.join(self.temp_dir, f"test_song_{i}.mp3")
            with open(test_file, 'wb') as f:
                f.write(b'dummy mp3 content')
            self.test_files.append(test_file)
        
        # Create test songs
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
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_empty_playlist_creation(self):
        """Test creating an empty playlist."""
        playlist = Playlist()
        
        self.assertEqual(len(playlist.songs), 0)
        self.assertEqual(playlist.current_index, 0)
        self.assertFalse(playlist.loop_enabled)
        self.assertTrue(playlist.is_empty())
    
    def test_playlist_creation_with_songs(self):
        """Test creating a playlist with songs."""
        playlist = Playlist(
            songs=self.test_songs.copy(),
            current_index=1,
            loop_enabled=True
        )
        
        self.assertEqual(len(playlist.songs), 3)
        self.assertEqual(playlist.current_index, 1)
        self.assertTrue(playlist.loop_enabled)
        self.assertFalse(playlist.is_empty())
    
    def test_playlist_post_init_validation(self):
        """Test playlist validation in __post_init__."""
        # Test negative current_index
        playlist = Playlist(songs=self.test_songs.copy(), current_index=-1)
        self.assertEqual(playlist.current_index, 0)
        
        # Test current_index beyond songs length
        playlist = Playlist(songs=self.test_songs.copy(), current_index=10)
        self.assertEqual(playlist.current_index, 2)  # len(songs) - 1
    
    def test_add_song(self):
        """Test adding a song to the playlist."""
        playlist = Playlist()
        playlist.add_song(self.test_songs[0])
        
        self.assertEqual(len(playlist.songs), 1)
        self.assertEqual(playlist.songs[0], self.test_songs[0])
    
    def test_add_song_invalid_type(self):
        """Test adding invalid type to playlist."""
        playlist = Playlist()
        
        with self.assertRaises(TypeError):
            playlist.add_song("not a song")
    
    def test_remove_song_valid_index(self):
        """Test removing a song with valid index."""
        playlist = Playlist(songs=self.test_songs.copy())
        
        removed_song = playlist.remove_song(1)
        
        self.assertEqual(removed_song, self.test_songs[1])
        self.assertEqual(len(playlist.songs), 2)
        self.assertEqual(playlist.songs[0], self.test_songs[0])
        self.assertEqual(playlist.songs[1], self.test_songs[2])
    
    def test_remove_song_invalid_index(self):
        """Test removing a song with invalid index."""
        playlist = Playlist(songs=self.test_songs.copy())
        
        removed_song = playlist.remove_song(10)
        
        self.assertIsNone(removed_song)
        self.assertEqual(len(playlist.songs), 3)
    
    def test_remove_song_adjust_current_index(self):
        """Test that current_index is adjusted when removing songs."""
        playlist = Playlist(songs=self.test_songs.copy(), current_index=2)
        
        # Remove song before current
        playlist.remove_song(0)
        self.assertEqual(playlist.current_index, 1)
        
        # Remove current song (now at index 1)
        playlist.remove_song(1)
        self.assertEqual(playlist.current_index, 0)
    
    def test_reorder_songs_valid_indices(self):
        """Test reordering songs with valid indices."""
        playlist = Playlist(songs=self.test_songs.copy())
        
        result = playlist.reorder_songs(0, 2)
        
        self.assertTrue(result)
        self.assertEqual(playlist.songs[0], self.test_songs[1])
        self.assertEqual(playlist.songs[1], self.test_songs[2])
        self.assertEqual(playlist.songs[2], self.test_songs[0])
    
    def test_reorder_songs_invalid_indices(self):
        """Test reordering songs with invalid indices."""
        playlist = Playlist(songs=self.test_songs.copy())
        
        result = playlist.reorder_songs(0, 10)
        
        self.assertFalse(result)
        # Songs should remain unchanged
        self.assertEqual(playlist.songs, self.test_songs)
    
    def test_reorder_songs_adjust_current_index(self):
        """Test that current_index is adjusted when reordering songs."""
        playlist = Playlist(songs=self.test_songs.copy(), current_index=0)
        
        # Move current song from 0 to 2
        playlist.reorder_songs(0, 2)
        self.assertEqual(playlist.current_index, 2)
    
    def test_get_current_song(self):
        """Test getting the current song."""
        playlist = Playlist(songs=self.test_songs.copy(), current_index=1)
        
        current_song = playlist.get_current_song()
        
        self.assertEqual(current_song, self.test_songs[1])
    
    def test_get_current_song_empty_playlist(self):
        """Test getting current song from empty playlist."""
        playlist = Playlist()
        
        current_song = playlist.get_current_song()
        
        self.assertIsNone(current_song)
    
    def test_next_song_normal(self):
        """Test advancing to next song normally."""
        playlist = Playlist(songs=self.test_songs.copy(), current_index=0)
        
        next_song = playlist.next_song()
        
        self.assertEqual(next_song, self.test_songs[1])
        self.assertEqual(playlist.current_index, 1)
    
    def test_next_song_at_end_no_loop(self):
        """Test next song at end without loop."""
        playlist = Playlist(songs=self.test_songs.copy(), current_index=2, loop_enabled=False)
        
        next_song = playlist.next_song()
        
        self.assertIsNone(next_song)
        self.assertEqual(playlist.current_index, 2)
    
    def test_next_song_at_end_with_loop(self):
        """Test next song at end with loop enabled."""
        playlist = Playlist(songs=self.test_songs.copy(), current_index=2, loop_enabled=True)
        
        next_song = playlist.next_song()
        
        self.assertEqual(next_song, self.test_songs[0])
        self.assertEqual(playlist.current_index, 0)
    
    def test_previous_song_normal(self):
        """Test going to previous song normally."""
        playlist = Playlist(songs=self.test_songs.copy(), current_index=1)
        
        previous_song = playlist.previous_song()
        
        self.assertEqual(previous_song, self.test_songs[0])
        self.assertEqual(playlist.current_index, 0)
    
    def test_previous_song_at_beginning_no_loop(self):
        """Test previous song at beginning without loop."""
        playlist = Playlist(songs=self.test_songs.copy(), current_index=0, loop_enabled=False)
        
        previous_song = playlist.previous_song()
        
        self.assertIsNone(previous_song)
        self.assertEqual(playlist.current_index, 0)
    
    def test_previous_song_at_beginning_with_loop(self):
        """Test previous song at beginning with loop enabled."""
        playlist = Playlist(songs=self.test_songs.copy(), current_index=0, loop_enabled=True)
        
        previous_song = playlist.previous_song()
        
        self.assertEqual(previous_song, self.test_songs[2])
        self.assertEqual(playlist.current_index, 2)
    
    def test_set_current_song_valid_index(self):
        """Test setting current song with valid index."""
        playlist = Playlist(songs=self.test_songs.copy())
        
        song = playlist.set_current_song(2)
        
        self.assertEqual(song, self.test_songs[2])
        self.assertEqual(playlist.current_index, 2)
    
    def test_set_current_song_invalid_index(self):
        """Test setting current song with invalid index."""
        playlist = Playlist(songs=self.test_songs.copy())
        
        song = playlist.set_current_song(10)
        
        self.assertIsNone(song)
        self.assertEqual(playlist.current_index, 0)  # Should remain unchanged
    
    def test_is_valid_index(self):
        """Test index validation."""
        playlist = Playlist(songs=self.test_songs.copy())
        
        self.assertTrue(playlist.is_valid_index(0))
        self.assertTrue(playlist.is_valid_index(2))
        self.assertFalse(playlist.is_valid_index(-1))
        self.assertFalse(playlist.is_valid_index(3))
    
    def test_clear(self):
        """Test clearing the playlist."""
        playlist = Playlist(songs=self.test_songs.copy(), current_index=1)
        
        playlist.clear()
        
        self.assertEqual(len(playlist.songs), 0)
        self.assertEqual(playlist.current_index, 0)
        self.assertTrue(playlist.is_empty())
    
    def test_get_valid_songs(self):
        """Test getting valid songs."""
        playlist = Playlist(songs=self.test_songs.copy())
        
        valid_songs = playlist.get_valid_songs()
        
        self.assertEqual(len(valid_songs), 3)
        self.assertEqual(valid_songs, self.test_songs)
    
    def test_remove_invalid_songs(self):
        """Test removing invalid songs."""
        playlist = Playlist(songs=self.test_songs.copy())
        
        # Remove one of the test files to make a song invalid
        os.remove(self.test_files[1])
        
        removed_count = playlist.remove_invalid_songs()
        
        self.assertEqual(removed_count, 1)
        self.assertEqual(len(playlist.songs), 2)
    
    def test_to_dict(self):
        """Test converting playlist to dictionary."""
        playlist = Playlist(
            songs=self.test_songs.copy(),
            current_index=1,
            loop_enabled=True
        )
        
        playlist_dict = playlist.to_dict()
        
        self.assertEqual(len(playlist_dict['songs']), 3)
        self.assertEqual(playlist_dict['current_index'], 1)
        self.assertTrue(playlist_dict['loop_enabled'])
    
    def test_from_dict(self):
        """Test creating playlist from dictionary."""
        playlist_data = {
            'songs': [song.to_dict() for song in self.test_songs],
            'current_index': 1,
            'loop_enabled': True
        }
        
        playlist = Playlist.from_dict(playlist_data)
        
        self.assertEqual(len(playlist.songs), 3)
        self.assertEqual(playlist.current_index, 1)
        self.assertTrue(playlist.loop_enabled)
    
    def test_save_to_file(self):
        """Test saving playlist to file."""
        playlist = Playlist(songs=self.test_songs.copy())
        playlist_file = os.path.join(self.temp_dir, "test_playlist.json")
        
        result = playlist.save_to_file(playlist_file)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(playlist_file))
        
        # Verify file content
        with open(playlist_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(len(data['songs']), 3)
    
    def test_load_from_file_existing(self):
        """Test loading playlist from existing file."""
        # Create a playlist file
        playlist_data = {
            'songs': [song.to_dict() for song in self.test_songs],
            'current_index': 1,
            'loop_enabled': True
        }
        
        playlist_file = os.path.join(self.temp_dir, "test_playlist.json")
        with open(playlist_file, 'w') as f:
            json.dump(playlist_data, f)
        
        playlist = Playlist.load_from_file(playlist_file)
        
        self.assertEqual(len(playlist.songs), 3)
        self.assertEqual(playlist.current_index, 1)
        self.assertTrue(playlist.loop_enabled)
    
    def test_load_from_file_nonexistent(self):
        """Test loading playlist from nonexistent file."""
        playlist_file = os.path.join(self.temp_dir, "nonexistent.json")
        
        playlist = Playlist.load_from_file(playlist_file)
        
        self.assertTrue(playlist.is_empty())
        self.assertEqual(playlist.current_index, 0)
        self.assertFalse(playlist.loop_enabled)
    
    def test_load_from_file_corrupted(self):
        """Test loading playlist from corrupted file."""
        playlist_file = os.path.join(self.temp_dir, "corrupted.json")
        with open(playlist_file, 'w') as f:
            f.write("invalid json content")
        
        playlist = Playlist.load_from_file(playlist_file)
        
        self.assertTrue(playlist.is_empty())
    
    def test_get_display_info(self):
        """Test getting display information."""
        playlist = Playlist(songs=self.test_songs.copy(), current_index=1, loop_enabled=True)
        
        info = playlist.get_display_info()
        
        self.assertEqual(info['total_songs'], 3)
        self.assertEqual(info['current_index'], 1)
        self.assertEqual(info['current_song'], "Artist 2 - Song 2")
        self.assertTrue(info['loop_enabled'])
        self.assertFalse(info['is_empty'])
        self.assertTrue(info['has_next'])
        self.assertTrue(info['has_previous'])
    
    def test_len(self):
        """Test __len__ method."""
        playlist = Playlist(songs=self.test_songs.copy())
        
        self.assertEqual(len(playlist), 3)
    
    def test_iter(self):
        """Test __iter__ method."""
        playlist = Playlist(songs=self.test_songs.copy())
        
        songs_list = list(playlist)
        
        self.assertEqual(songs_list, self.test_songs)
    
    def test_getitem(self):
        """Test __getitem__ method."""
        playlist = Playlist(songs=self.test_songs.copy())
        
        self.assertEqual(playlist[1], self.test_songs[1])
    
    def test_str_representation(self):
        """Test string representation."""
        # Empty playlist
        empty_playlist = Playlist()
        self.assertEqual(str(empty_playlist), "Empty Playlist")
        
        # Non-empty playlist
        playlist = Playlist(songs=self.test_songs.copy(), current_index=1)
        expected_str = "Playlist (3 songs, current: Artist 2 - Song 2)"
        self.assertEqual(str(playlist), expected_str)
    
    def test_repr_representation(self):
        """Test repr representation."""
        playlist = Playlist(songs=self.test_songs.copy(), current_index=1, loop_enabled=True)
        
        expected_repr = "Playlist(songs=3, current_index=1, loop_enabled=True)"
        self.assertEqual(repr(playlist), expected_repr)


if __name__ == '__main__':
    unittest.main()