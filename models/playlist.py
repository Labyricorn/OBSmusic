"""
Playlist data model with persistence and navigation capabilities.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path

from .song import Song

logger = logging.getLogger(__name__)


@dataclass
class Playlist:
    """Represents a playlist with songs and playback state."""
    
    songs: List[Song] = field(default_factory=list)
    current_index: int = 0
    loop_enabled: bool = False
    
    def __post_init__(self):
        """Validate playlist data after initialization."""
        if self.current_index < 0:
            self.current_index = 0
        elif self.current_index >= len(self.songs) and self.songs:
            self.current_index = len(self.songs) - 1
    
    def add_song(self, song: Song) -> None:
        """Add a song to the playlist.
        
        Args:
            song: Song instance to add
        """
        if not isinstance(song, Song):
            raise TypeError("Expected Song instance")
        
        self.songs.append(song)
        logger.debug(f"Added song to playlist: {song.get_display_name()}")
    
    def remove_song(self, index: int) -> Optional[Song]:
        """Remove a song from the playlist by index.
        
        Args:
            index: Index of the song to remove
            
        Returns:
            Removed Song instance, or None if index is invalid
        """
        if not self.is_valid_index(index):
            logger.warning(f"Invalid index for song removal: {index}")
            return None
        
        removed_song = self.songs.pop(index)
        
        # Adjust current_index if necessary
        if index < self.current_index:
            self.current_index -= 1
        elif index == self.current_index and self.current_index >= len(self.songs):
            self.current_index = max(0, len(self.songs) - 1)
        
        logger.debug(f"Removed song from playlist: {removed_song.get_display_name()}")
        return removed_song
    
    def reorder_songs(self, old_index: int, new_index: int) -> bool:
        """Reorder songs in the playlist.
        
        Args:
            old_index: Current index of the song to move
            new_index: Target index for the song
            
        Returns:
            True if reordering was successful, False otherwise
        """
        if not self.is_valid_index(old_index) or new_index < 0 or new_index >= len(self.songs):
            logger.warning(f"Invalid indices for reordering: {old_index} -> {new_index}")
            return False
        
        if old_index == new_index:
            return True
        
        # Move the song
        song = self.songs.pop(old_index)
        self.songs.insert(new_index, song)
        
        # Adjust current_index if necessary
        if old_index == self.current_index:
            self.current_index = new_index
        elif old_index < self.current_index <= new_index:
            self.current_index -= 1
        elif new_index <= self.current_index < old_index:
            self.current_index += 1
        
        logger.debug(f"Reordered song from index {old_index} to {new_index}")
        return True
    
    def get_current_song(self) -> Optional[Song]:
        """Get the currently selected song.
        
        Returns:
            Current Song instance, or None if playlist is empty
        """
        if not self.songs or not self.is_valid_index(self.current_index):
            return None
        return self.songs[self.current_index]
    
    def next_song(self) -> Optional[Song]:
        """Advance to the next song in the playlist.
        
        Returns:
            Next Song instance, or None if at end and loop is disabled
        """
        if not self.songs:
            return None
        
        if self.current_index < len(self.songs) - 1:
            self.current_index += 1
        elif self.loop_enabled:
            self.current_index = 0
        else:
            # At end of playlist and loop is disabled
            return None
        
        current_song = self.get_current_song()
        if current_song:
            logger.debug(f"Advanced to next song: {current_song.get_display_name()}")
        return current_song
    
    def previous_song(self) -> Optional[Song]:
        """Go to the previous song in the playlist.
        
        Returns:
            Previous Song instance, or None if at beginning and loop is disabled
        """
        if not self.songs:
            return None
        
        if self.current_index > 0:
            self.current_index -= 1
        elif self.loop_enabled:
            self.current_index = len(self.songs) - 1
        else:
            # At beginning of playlist and loop is disabled
            return None
        
        current_song = self.get_current_song()
        if current_song:
            logger.debug(f"Went to previous song: {current_song.get_display_name()}")
        return current_song
    
    def set_current_song(self, index: int) -> Optional[Song]:
        """Set the current song by index.
        
        Args:
            index: Index of the song to set as current
            
        Returns:
            Song at the specified index, or None if index is invalid
        """
        if not self.is_valid_index(index):
            logger.warning(f"Invalid index for setting current song: {index}")
            return None
        
        self.current_index = index
        current_song = self.get_current_song()
        if current_song:
            logger.debug(f"Set current song to: {current_song.get_display_name()}")
        return current_song
    
    def is_valid_index(self, index: int) -> bool:
        """Check if an index is valid for the current playlist.
        
        Args:
            index: Index to validate
            
        Returns:
            True if index is valid, False otherwise
        """
        return 0 <= index < len(self.songs)
    
    def is_empty(self) -> bool:
        """Check if the playlist is empty.
        
        Returns:
            True if playlist has no songs, False otherwise
        """
        return len(self.songs) == 0
    
    def get_song_count(self) -> int:
        """Get the number of songs in the playlist.
        
        Returns:
            Number of songs in the playlist
        """
        return len(self.songs)
    
    def clear(self) -> None:
        """Remove all songs from the playlist."""
        self.songs.clear()
        self.current_index = 0
        logger.debug("Cleared all songs from playlist")
    
    def get_valid_songs(self) -> List[Song]:
        """Get list of songs that still exist on the filesystem.
        
        Returns:
            List of valid Song instances
        """
        return [song for song in self.songs if song.is_valid()]
    
    def remove_invalid_songs(self) -> int:
        """Remove songs that no longer exist on the filesystem.
        
        Returns:
            Number of songs removed
        """
        initial_count = len(self.songs)
        valid_songs = self.get_valid_songs()
        
        if len(valid_songs) != initial_count:
            # Find the new index for the current song
            current_song = self.get_current_song()
            new_current_index = 0
            
            if current_song and current_song.is_valid():
                try:
                    new_current_index = valid_songs.index(current_song)
                except ValueError:
                    new_current_index = 0
            
            self.songs = valid_songs
            self.current_index = min(new_current_index, max(0, len(self.songs) - 1))
            
            removed_count = initial_count - len(valid_songs)
            logger.info(f"Removed {removed_count} invalid songs from playlist")
            return removed_count
        
        return 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Playlist to dictionary for serialization.
        
        Returns:
            Dictionary representation of the playlist
        """
        return {
            'songs': [song.to_dict() for song in self.songs],
            'current_index': self.current_index,
            'loop_enabled': self.loop_enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Playlist':
        """Create Playlist from dictionary.
        
        Args:
            data: Dictionary containing playlist data
            
        Returns:
            Playlist instance
        """
        songs = [Song.from_dict(song_data) for song_data in data.get('songs', [])]
        
        playlist = cls(
            songs=songs,
            current_index=data.get('current_index', 0),
            loop_enabled=data.get('loop_enabled', False)
        )
        
        return playlist
    
    def save_to_file(self, file_path: str) -> bool:
        """Save playlist to JSON file.
        
        Args:
            file_path: Path to save the playlist file
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Remove invalid songs before saving
            self.remove_invalid_songs()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved playlist to {file_path} ({len(self.songs)} songs)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save playlist to {file_path}: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'Playlist':
        """Load playlist from JSON file.
        
        Args:
            file_path: Path to the playlist file
            
        Returns:
            Playlist instance (empty if file doesn't exist or is corrupted)
        """
        try:
            if not Path(file_path).exists():
                logger.info(f"Playlist file not found: {file_path}, creating empty playlist")
                return cls()
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            playlist = cls.from_dict(data)
            
            # Remove any invalid songs after loading
            removed_count = playlist.remove_invalid_songs()
            if removed_count > 0:
                logger.info(f"Removed {removed_count} invalid songs after loading")
            
            logger.info(f"Loaded playlist from {file_path} ({len(playlist.songs)} songs)")
            return playlist
            
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted playlist file {file_path}: {e}")
            return cls()
        except Exception as e:
            logger.error(f"Failed to load playlist from {file_path}: {e}")
            return cls()
    
    def get_display_info(self) -> Dict[str, Any]:
        """Get playlist information for display purposes.
        
        Returns:
            Dictionary with playlist display information
        """
        current_song = self.get_current_song()
        
        return {
            'total_songs': len(self.songs),
            'current_index': self.current_index,
            'current_song': current_song.get_display_name() if current_song else None,
            'loop_enabled': self.loop_enabled,
            'is_empty': self.is_empty(),
            'has_next': self.current_index < len(self.songs) - 1 or self.loop_enabled,
            'has_previous': self.current_index > 0 or self.loop_enabled
        }
    
    def __len__(self) -> int:
        """Return the number of songs in the playlist."""
        return len(self.songs)
    
    def __iter__(self):
        """Make playlist iterable over songs."""
        return iter(self.songs)
    
    def __getitem__(self, index: int) -> Song:
        """Get song by index."""
        return self.songs[index]
    
    def __str__(self) -> str:
        """String representation of the playlist."""
        if self.is_empty():
            return "Empty Playlist"
        
        current_song = self.get_current_song()
        current_name = current_song.get_display_name() if current_song else "None"
        
        return f"Playlist ({len(self.songs)} songs, current: {current_name})"
    
    def __repr__(self) -> str:
        """Developer representation of the playlist."""
        return f"Playlist(songs={len(self.songs)}, current_index={self.current_index}, loop_enabled={self.loop_enabled})"