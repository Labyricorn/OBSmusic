"""
Playlist manager with file operations and CRUD functionality.

This module provides comprehensive playlist management including:
- Adding/removing/reordering songs with metadata extraction
- JSON persistence with error handling for corrupted files
- Validation and cleanup of invalid songs
- Backup and restore functionality

For testing purposes, use the test_song_file.mp3 file in the project root.
"""

import os
import json
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from models.song import Song
from models.playlist import Playlist

logger = logging.getLogger(__name__)


class PlaylistManager:
    """Manages playlist operations including CRUD operations and persistence."""
    
    def __init__(self, playlist_file: str = "data/playlist.json", artwork_dir: str = "data/artwork"):
        """Initialize the playlist manager.
        
        Args:
            playlist_file: Path to the playlist JSON file
            artwork_dir: Directory to store extracted artwork
        """
        self.playlist_file = playlist_file
        self.artwork_dir = artwork_dir
        self.playlist = Playlist()
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Load existing playlist if available
        self.load_playlist()
    
    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        try:
            # Create playlist file directory
            playlist_dir = Path(self.playlist_file).parent
            playlist_dir.mkdir(parents=True, exist_ok=True)
            
            # Create artwork directory
            Path(self.artwork_dir).mkdir(parents=True, exist_ok=True)
            
            logger.debug(f"Ensured directories exist: {playlist_dir}, {self.artwork_dir}")
            
        except Exception as e:
            logger.error(f"Failed to create directories: {e}")
    
    def add_song(self, file_path: str, extract_artwork: bool = True) -> bool:
        """Add a song to the playlist with metadata extraction.
        
        Args:
            file_path: Path to the MP3 file to add
            extract_artwork: Whether to extract and cache artwork
            
        Returns:
            True if song was added successfully, False otherwise
        """
        try:
            # Validate file exists and is readable
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False
            
            if not os.access(file_path, os.R_OK):
                logger.error(f"File not readable: {file_path}")
                return False
            
            # Check if file is already in playlist
            for song in self.playlist.songs:
                if os.path.abspath(song.file_path) == os.path.abspath(file_path):
                    logger.warning(f"Song already in playlist: {file_path}")
                    return False
            
            # Create song with metadata extraction and optional artwork
            artwork_dir = self.artwork_dir if extract_artwork else None
            song = Song.from_file(file_path, artwork_dir)
            
            # Add to playlist
            self.playlist.add_song(song)
            
            logger.info(f"Added song to playlist: {song.get_display_name()}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add song {file_path}: {e}")
            return False
    
    def remove_song(self, index: int) -> bool:
        """Remove a song from the playlist by index.
        
        Args:
            index: Index of the song to remove
            
        Returns:
            True if song was removed successfully, False otherwise
        """
        try:
            removed_song = self.playlist.remove_song(index)
            if removed_song:
                logger.info(f"Removed song from playlist: {removed_song.get_display_name()}")
                return True
            else:
                logger.warning(f"Failed to remove song at index {index}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove song at index {index}: {e}")
            return False
    
    def reorder_songs(self, old_index: int, new_index: int) -> bool:
        """Reorder songs in the playlist.
        
        Args:
            old_index: Current index of the song to move
            new_index: Target index for the song
            
        Returns:
            True if reordering was successful, False otherwise
        """
        try:
            success = self.playlist.reorder_songs(old_index, new_index)
            if success:
                logger.info(f"Reordered song from index {old_index} to {new_index}")
            else:
                logger.warning(f"Failed to reorder song from {old_index} to {new_index}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to reorder songs {old_index} -> {new_index}: {e}")
            return False
    
    def get_current_song(self) -> Optional[Song]:
        """Get the currently selected song.
        
        Returns:
            Current Song instance, or None if playlist is empty
        """
        return self.playlist.get_current_song()
    
    def next_song(self) -> Optional[Song]:
        """Advance to the next song in the playlist.
        
        Returns:
            Next Song instance, or None if at end and loop is disabled
        """
        return self.playlist.next_song()
    
    def previous_song(self) -> Optional[Song]:
        """Go to the previous song in the playlist.
        
        Returns:
            Previous Song instance, or None if at beginning and loop is disabled
        """
        return self.playlist.previous_song()
    
    def set_current_song(self, index: int) -> Optional[Song]:
        """Set the current song by index.
        
        Args:
            index: Index of the song to set as current
            
        Returns:
            Song at the specified index, or None if index is invalid
        """
        return self.playlist.set_current_song(index)
    
    def get_playlist(self) -> Playlist:
        """Get the current playlist.
        
        Returns:
            Current Playlist instance
        """
        return self.playlist
    
    def get_songs(self) -> List[Song]:
        """Get list of all songs in the playlist.
        
        Returns:
            List of Song instances
        """
        return self.playlist.songs.copy()
    
    def get_song_count(self) -> int:
        """Get the number of songs in the playlist.
        
        Returns:
            Number of songs in the playlist
        """
        return self.playlist.get_song_count()
    
    def is_empty(self) -> bool:
        """Check if the playlist is empty.
        
        Returns:
            True if playlist has no songs, False otherwise
        """
        return self.playlist.is_empty()
    
    def clear_playlist(self) -> None:
        """Remove all songs from the playlist."""
        self.playlist.clear()
        logger.info("Cleared all songs from playlist")
    
    def set_loop_enabled(self, enabled: bool) -> None:
        """Set the loop enabled state.
        
        Args:
            enabled: True to enable looping, False to disable
        """
        self.playlist.loop_enabled = enabled
        logger.debug(f"Set loop enabled: {enabled}")
    
    def is_loop_enabled(self) -> bool:
        """Check if looping is enabled.
        
        Returns:
            True if looping is enabled, False otherwise
        """
        return self.playlist.loop_enabled
    
    def save_playlist(self) -> bool:
        """Save the current playlist to file.
        
        Returns:
            True if save was successful, False otherwise
        """
        try:
            success = self.playlist.save_to_file(self.playlist_file)
            if success:
                logger.info(f"Saved playlist to {self.playlist_file}")
            else:
                logger.error(f"Failed to save playlist to {self.playlist_file}")
            return success
            
        except Exception as e:
            logger.error(f"Exception while saving playlist: {e}")
            return False
    
    def load_playlist(self) -> bool:
        """Load playlist from file with error recovery.
        
        Returns:
            True if load was successful, False otherwise
        """
        try:
            self.playlist = Playlist.load_from_file(self.playlist_file)
            
            # Validate loaded playlist
            validation_result = self.validate_playlist()
            if validation_result['invalid_songs'] > 0:
                logger.warning(f"Found {validation_result['invalid_songs']} invalid songs in playlist")
                # Clean up invalid songs automatically
                removed_count = self.cleanup_invalid_songs()
                if removed_count > 0:
                    logger.info(f"Automatically removed {removed_count} invalid songs")
                    # Save the cleaned playlist
                    self.save_playlist()
            
            logger.info(f"Loaded playlist from {self.playlist_file} ({len(self.playlist.songs)} songs)")
            return True
            
        except Exception as e:
            logger.error(f"Exception while loading playlist: {e}")
            # Try to create backup of corrupted playlist
            self._handle_corrupted_playlist()
            # Create empty playlist on error
            self.playlist = Playlist()
            return False
    
    def reload_playlist(self) -> bool:
        """Reload playlist from file, discarding current changes.
        
        Returns:
            True if reload was successful, False otherwise
        """
        logger.info("Reloading playlist from file")
        return self.load_playlist()
    
    def validate_playlist(self) -> Dict[str, Any]:
        """Validate the current playlist and return status information.
        
        Returns:
            Dictionary with validation results
        """
        try:
            total_songs = len(self.playlist.songs)
            valid_songs = self.playlist.get_valid_songs()
            valid_count = len(valid_songs)
            invalid_count = total_songs - valid_count
            
            validation_result = {
                'total_songs': total_songs,
                'valid_songs': valid_count,
                'invalid_songs': invalid_count,
                'is_valid': invalid_count == 0,
                'current_song_valid': False,
                'playlist_file_exists': os.path.exists(self.playlist_file)
            }
            
            # Check if current song is valid
            current_song = self.playlist.get_current_song()
            if current_song:
                validation_result['current_song_valid'] = current_song.is_valid()
            
            logger.debug(f"Playlist validation: {validation_result}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Error during playlist validation: {e}")
            return {
                'total_songs': 0,
                'valid_songs': 0,
                'invalid_songs': 0,
                'is_valid': False,
                'current_song_valid': False,
                'playlist_file_exists': False,
                'error': str(e)
            }
    
    def cleanup_invalid_songs(self) -> int:
        """Remove songs that no longer exist on the filesystem.
        
        Returns:
            Number of songs removed
        """
        try:
            removed_count = self.playlist.remove_invalid_songs()
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} invalid songs from playlist")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error during playlist cleanup: {e}")
            return 0
    
    def get_playlist_info(self) -> Dict[str, Any]:
        """Get comprehensive playlist information.
        
        Returns:
            Dictionary with playlist information
        """
        try:
            info = self.playlist.get_display_info()
            validation = self.validate_playlist()
            
            # Combine information
            playlist_info = {
                **info,
                'playlist_file': self.playlist_file,
                'artwork_dir': self.artwork_dir,
                'validation': validation
            }
            
            return playlist_info
            
        except Exception as e:
            logger.error(f"Error getting playlist info: {e}")
            return {
                'total_songs': 0,
                'current_index': 0,
                'current_song': None,
                'loop_enabled': False,
                'is_empty': True,
                'has_next': False,
                'has_previous': False,
                'playlist_file': self.playlist_file,
                'artwork_dir': self.artwork_dir,
                'error': str(e)
            }
    
    def backup_playlist(self, backup_path: Optional[str] = None) -> bool:
        """Create a backup of the current playlist.
        
        Args:
            backup_path: Optional custom backup path
            
        Returns:
            True if backup was successful, False otherwise
        """
        try:
            if backup_path is None:
                # Generate backup filename with timestamp
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"playlist_backup_{timestamp}.json"
                backup_path = os.path.join(Path(self.playlist_file).parent, backup_filename)
            
            # Save to backup location
            success = self.playlist.save_to_file(backup_path)
            if success:
                logger.info(f"Created playlist backup: {backup_path}")
            else:
                logger.error(f"Failed to create playlist backup: {backup_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Exception while creating playlist backup: {e}")
            return False
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """Restore playlist from a backup file.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            True if restore was successful, False otherwise
        """
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Load playlist from backup
            backup_playlist = Playlist.load_from_file(backup_path)
            
            # Replace current playlist
            self.playlist = backup_playlist
            
            logger.info(f"Restored playlist from backup: {backup_path} ({len(self.playlist.songs)} songs)")
            return True
            
        except Exception as e:
            logger.error(f"Exception while restoring from backup: {e}")
            return False
    
    def add_songs_from_directory(self, directory_path: str, recursive: bool = False, extract_artwork: bool = True) -> Dict[str, Any]:
        """Add all MP3 files from a directory to the playlist.
        
        Args:
            directory_path: Path to the directory containing MP3 files
            recursive: Whether to search subdirectories recursively
            extract_artwork: Whether to extract and cache artwork for each song
            
        Returns:
            Dictionary with operation results
        """
        try:
            if not os.path.exists(directory_path):
                logger.error(f"Directory not found: {directory_path}")
                return {'success': False, 'added': 0, 'failed': 0, 'errors': ['Directory not found']}
            
            if not os.path.isdir(directory_path):
                logger.error(f"Path is not a directory: {directory_path}")
                return {'success': False, 'added': 0, 'failed': 0, 'errors': ['Path is not a directory']}
            
            added_count = 0
            failed_count = 0
            errors = []
            
            # Get MP3 files
            pattern = "**/*.mp3" if recursive else "*.mp3"
            mp3_files = list(Path(directory_path).glob(pattern))
            
            logger.info(f"Found {len(mp3_files)} MP3 files in {directory_path}")
            
            for mp3_file in mp3_files:
                try:
                    if self.add_song(str(mp3_file), extract_artwork):
                        added_count += 1
                    else:
                        failed_count += 1
                        errors.append(f"Failed to add: {mp3_file}")
                except Exception as e:
                    failed_count += 1
                    errors.append(f"Error adding {mp3_file}: {str(e)}")
            
            logger.info(f"Added {added_count} songs from directory, {failed_count} failed")
            
            return {
                'success': True,
                'added': added_count,
                'failed': failed_count,
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Exception while adding songs from directory: {e}")
            return {'success': False, 'added': 0, 'failed': 0, 'errors': [str(e)]}
    
    def refresh_metadata(self, song_index: int = None) -> Dict[str, Any]:
        """Refresh metadata for songs in the playlist.
        
        Args:
            song_index: Optional index of specific song to refresh, None for all songs
            
        Returns:
            Dictionary with refresh results
        """
        try:
            if song_index is not None:
                # Refresh specific song
                if not self.playlist.is_valid_index(song_index):
                    return {'success': False, 'refreshed': 0, 'errors': ['Invalid song index']}
                
                song = self.playlist.songs[song_index]
                if not song.is_valid():
                    return {'success': False, 'refreshed': 0, 'errors': ['Song file no longer exists']}
                
                try:
                    # Create new song with fresh metadata
                    refreshed_song = Song.from_file(song.file_path, self.artwork_dir)
                    self.playlist.songs[song_index] = refreshed_song
                    
                    logger.info(f"Refreshed metadata for song: {refreshed_song.get_display_name()}")
                    return {'success': True, 'refreshed': 1, 'errors': []}
                    
                except Exception as e:
                    error_msg = f"Failed to refresh metadata for {song.file_path}: {str(e)}"
                    logger.error(error_msg)
                    return {'success': False, 'refreshed': 0, 'errors': [error_msg]}
            
            else:
                # Refresh all songs
                refreshed_count = 0
                errors = []
                
                for i, song in enumerate(self.playlist.songs):
                    if song.is_valid():
                        try:
                            refreshed_song = Song.from_file(song.file_path, self.artwork_dir)
                            self.playlist.songs[i] = refreshed_song
                            refreshed_count += 1
                        except Exception as e:
                            error_msg = f"Failed to refresh {song.file_path}: {str(e)}"
                            errors.append(error_msg)
                            logger.error(error_msg)
                    else:
                        errors.append(f"Song file no longer exists: {song.file_path}")
                
                logger.info(f"Refreshed metadata for {refreshed_count} songs")
                return {'success': True, 'refreshed': refreshed_count, 'errors': errors}
                
        except Exception as e:
            logger.error(f"Exception while refreshing metadata: {e}")
            return {'success': False, 'refreshed': 0, 'errors': [str(e)]}
    
    def get_artwork_cache_info(self) -> Dict[str, Any]:
        """Get information about the artwork cache.
        
        Returns:
            Dictionary with artwork cache information
        """
        try:
            if not os.path.exists(self.artwork_dir):
                return {
                    'cache_exists': False,
                    'cached_files': 0,
                    'cache_size_bytes': 0,
                    'cache_size_mb': 0.0
                }
            
            artwork_files = list(Path(self.artwork_dir).glob("*.jpg"))
            total_size = sum(f.stat().st_size for f in artwork_files if f.is_file())
            
            return {
                'cache_exists': True,
                'cached_files': len(artwork_files),
                'cache_size_bytes': total_size,
                'cache_size_mb': round(total_size / (1024 * 1024), 2),
                'cache_directory': self.artwork_dir
            }
            
        except Exception as e:
            logger.error(f"Error getting artwork cache info: {e}")
            return {
                'cache_exists': False,
                'cached_files': 0,
                'cache_size_bytes': 0,
                'cache_size_mb': 0.0,
                'error': str(e)
            }
    
    def clear_artwork_cache(self) -> bool:
        """Clear all cached artwork files.
        
        Returns:
            True if cache was cleared successfully, False otherwise
        """
        try:
            if not os.path.exists(self.artwork_dir):
                logger.info("Artwork cache directory does not exist")
                return True
            
            artwork_files = list(Path(self.artwork_dir).glob("*.jpg"))
            removed_count = 0
            
            for artwork_file in artwork_files:
                try:
                    artwork_file.unlink()
                    removed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to remove artwork file {artwork_file}: {e}")
            
            logger.info(f"Cleared {removed_count} artwork files from cache")
            return True
            
        except Exception as e:
            logger.error(f"Exception while clearing artwork cache: {e}")
            return False
    
    def extract_missing_artwork(self) -> Dict[str, Any]:
        """Extract artwork for songs that don't have cached artwork.
        
        Returns:
            Dictionary with extraction results
        """
        try:
            extracted_count = 0
            failed_count = 0
            errors = []
            
            for song in self.playlist.songs:
                if song.is_valid() and not song.artwork_path:
                    try:
                        # Re-extract metadata with artwork
                        updated_song = Song.from_file(song.file_path, self.artwork_dir)
                        
                        # Update the song in place
                        song.artwork_path = updated_song.artwork_path
                        
                        if song.artwork_path:
                            extracted_count += 1
                            logger.debug(f"Extracted artwork for: {song.get_display_name()}")
                        
                    except Exception as e:
                        failed_count += 1
                        error_msg = f"Failed to extract artwork for {song.file_path}: {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)
            
            logger.info(f"Extracted artwork for {extracted_count} songs, {failed_count} failed")
            
            return {
                'success': True,
                'extracted': extracted_count,
                'failed': failed_count,
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Exception while extracting missing artwork: {e}")
            return {'success': False, 'extracted': 0, 'failed': 0, 'errors': [str(e)]}
    
    def get_metadata_summary(self) -> Dict[str, Any]:
        """Get summary of metadata across all songs in the playlist.
        
        Returns:
            Dictionary with metadata summary
        """
        try:
            if not self.playlist.songs:
                return {
                    'total_songs': 0,
                    'songs_with_artwork': 0,
                    'unique_artists': 0,
                    'unique_albums': 0,
                    'total_duration': 0.0,
                    'average_duration': 0.0
                }
            
            artists = set()
            albums = set()
            total_duration = 0.0
            songs_with_artwork = 0
            
            for song in self.playlist.songs:
                if song.artist and song.artist != "Unknown Artist":
                    artists.add(song.artist)
                if song.album and song.album != "Unknown Album":
                    albums.add(song.album)
                if song.artwork_path:
                    songs_with_artwork += 1
                total_duration += song.duration
            
            average_duration = total_duration / len(self.playlist.songs) if self.playlist.songs else 0.0
            
            return {
                'total_songs': len(self.playlist.songs),
                'songs_with_artwork': songs_with_artwork,
                'unique_artists': len(artists),
                'unique_albums': len(albums),
                'total_duration': round(total_duration, 2),
                'average_duration': round(average_duration, 2),
                'total_duration_formatted': self._format_duration(total_duration),
                'average_duration_formatted': self._format_duration(average_duration)
            }
            
        except Exception as e:
            logger.error(f"Error getting metadata summary: {e}")
            return {
                'total_songs': 0,
                'songs_with_artwork': 0,
                'unique_artists': 0,
                'unique_albums': 0,
                'total_duration': 0.0,
                'average_duration': 0.0,
                'error': str(e)
            }
    
    def _handle_corrupted_playlist(self) -> None:
        """Handle corrupted playlist file by creating backup and cleaning up."""
        try:
            if os.path.exists(self.playlist_file):
                # Create backup with timestamp
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"playlist_corrupted_{timestamp}.json"
                backup_path = os.path.join(Path(self.playlist_file).parent, backup_filename)
                
                # Copy corrupted file to backup
                import shutil
                shutil.copy2(self.playlist_file, backup_path)
                logger.info(f"Created backup of corrupted playlist: {backup_path}")
                
                # Remove corrupted file
                os.remove(self.playlist_file)
                logger.info(f"Removed corrupted playlist file: {self.playlist_file}")
                
        except Exception as e:
            logger.error(f"Failed to handle corrupted playlist: {e}")

    def get_playlist_status(self) -> Dict[str, Any]:
        """Get playlist file status and health information.
        
        Returns:
            Dict containing playlist status information
        """
        try:
            status = {
                'playlist_file_exists': os.path.exists(self.playlist_file),
                'playlist_file_path': self.playlist_file,
                'is_valid': True,
                'error_message': None,
                'backup_files': [],
                'validation': self.validate_playlist()
            }
            
            if status['playlist_file_exists']:
                try:
                    # Try to load and validate
                    test_playlist = Playlist.load_from_file(self.playlist_file)
                    status['is_valid'] = True
                        
                except json.JSONDecodeError as e:
                    status['is_valid'] = False
                    status['error_message'] = f"JSON decode error: {str(e)}"
                except Exception as e:
                    status['is_valid'] = False
                    status['error_message'] = f"Load error: {str(e)}"
            
            # Find backup files
            playlist_dir = Path(self.playlist_file).parent
            if playlist_dir.exists():
                playlist_name = Path(self.playlist_file).stem
                backup_patterns = [f"{playlist_name}_backup_", f"{playlist_name}_corrupted_"]
                
                for file in playlist_dir.iterdir():
                    if file.is_file() and any(file.name.startswith(pattern) for pattern in backup_patterns):
                        status['backup_files'].append(str(file))
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting playlist status: {e}")
            return {
                'playlist_file_exists': False,
                'playlist_file_path': self.playlist_file,
                'is_valid': False,
                'error_message': f"Status check failed: {str(e)}",
                'backup_files': [],
                'validation': {'error': str(e)}
            }

    def _format_duration(self, duration_seconds: float) -> str:
        """Format duration in seconds to MM:SS or HH:MM:SS format.
        
        Args:
            duration_seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        if duration_seconds <= 0:
            return "0:00"
        
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def __str__(self) -> str:
        """String representation of the playlist manager."""
        return f"PlaylistManager(file='{self.playlist_file}', songs={len(self.playlist.songs)})"
    
    def __repr__(self) -> str:
        """Developer representation of the playlist manager."""
        return f"PlaylistManager(playlist_file='{self.playlist_file}', artwork_dir='{self.artwork_dir}', songs={len(self.playlist.songs)})"