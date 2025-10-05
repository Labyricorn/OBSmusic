"""
Song data model with metadata extraction capabilities.
"""

import os
import logging
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3NoHeaderError
    from mutagen.mp3 import MP3
    from PIL import Image
    import io
except ImportError as e:
    logging.error(f"Required dependency missing: {e}")
    raise

logger = logging.getLogger(__name__)


@dataclass
class Song:
    """Represents a song with metadata and file information."""
    
    file_path: str
    title: str
    artist: str
    album: str
    artwork_path: Optional[str] = None
    duration: float = 0.0
    
    def __post_init__(self):
        """Validate song data after initialization."""
        if not self.file_path:
            raise ValueError("file_path cannot be empty")
        
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Song file not found: {self.file_path}")
    
    @classmethod
    def from_file(cls, file_path: str, artwork_dir: Optional[str] = None) -> 'Song':
        """Create a Song instance from an MP3 file with metadata extraction.
        
        Args:
            file_path: Path to the MP3 file
            artwork_dir: Optional directory to save extracted artwork
            
        Returns:
            Song instance with extracted metadata
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a valid MP3
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract metadata
        metadata = cls._extract_metadata(file_path)
        
        # Extract and save artwork if directory provided
        artwork_path = None
        if artwork_dir:
            artwork_path = cls._extract_artwork(file_path, artwork_dir, metadata)
        
        return cls(
            file_path=file_path,
            title=metadata['title'],
            artist=metadata['artist'],
            album=metadata['album'],
            artwork_path=artwork_path,
            duration=metadata['duration']
        )
    
    @staticmethod
    def _extract_metadata(file_path: str) -> dict:
        """Extract metadata from MP3 file.
        
        Args:
            file_path: Path to the MP3 file
            
        Returns:
            Dictionary containing extracted metadata
        """
        metadata = {
            'title': '',
            'artist': '',
            'album': '',
            'duration': 0.0
        }
        
        try:
            # Load the audio file
            audio_file = MutagenFile(file_path)
            
            if audio_file is None:
                logger.warning(f"Could not read metadata from {file_path}")
                metadata['title'] = Path(file_path).stem  # Use filename as fallback
                metadata['artist'] = "Unknown Artist"
                metadata['album'] = "Unknown Album"
                return metadata
            
            # Extract basic metadata
            metadata['title'] = Song._get_tag_value(audio_file, ['TIT2', 'TITLE', '\xa9nam'])
            metadata['artist'] = Song._get_tag_value(audio_file, ['TPE1', 'ARTIST', '\xa9ART'])
            metadata['album'] = Song._get_tag_value(audio_file, ['TALB', 'ALBUM', '\xa9alb'])
            
            # Get duration
            if hasattr(audio_file, 'info') and audio_file.info:
                metadata['duration'] = getattr(audio_file.info, 'length', 0.0)
            
            # Use filename as title fallback if no title found
            if not metadata['title']:
                metadata['title'] = Path(file_path).stem
                
            # Use "Unknown" as fallback for missing artist/album
            if not metadata['artist']:
                metadata['artist'] = "Unknown Artist"
            if not metadata['album']:
                metadata['album'] = "Unknown Album"
                
            logger.debug(f"Extracted metadata from {file_path}: {metadata}")
            
        except ID3NoHeaderError:
            logger.warning(f"No ID3 header found in {file_path}, using filename")
            metadata['title'] = Path(file_path).stem
            metadata['artist'] = "Unknown Artist"
            metadata['album'] = "Unknown Album"
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {e}")
            metadata['title'] = Path(file_path).stem
            metadata['artist'] = "Unknown Artist"
            metadata['album'] = "Unknown Album"
        
        return metadata
    
    @staticmethod
    def _get_tag_value(audio_file, tag_keys: list) -> str:
        """Get tag value from audio file, trying multiple possible tag keys.
        
        Args:
            audio_file: Mutagen audio file object
            tag_keys: List of possible tag keys to try
            
        Returns:
            Tag value as string, or empty string if not found
        """
        for key in tag_keys:
            if key in audio_file:
                value = audio_file[key]
                if isinstance(value, list) and value:
                    return str(value[0])
                elif value:
                    return str(value)
        return ""
    
    @staticmethod
    def _extract_artwork(file_path: str, artwork_dir: str, metadata: dict) -> Optional[str]:
        """Extract and save album artwork from MP3 file.
        
        Args:
            file_path: Path to the MP3 file
            artwork_dir: Directory to save artwork
            metadata: Song metadata dictionary
            
        Returns:
            Path to saved artwork file, or None if no artwork found
        """
        try:
            audio_file = MutagenFile(file_path)
            if not audio_file:
                return None
            
            # Try to find artwork in various tag formats
            artwork_data = None
            
            # ID3v2 APIC frame (most common)
            if 'APIC:' in audio_file:
                artwork_data = audio_file['APIC:'].data
            elif hasattr(audio_file, 'tags') and audio_file.tags:
                # Try other common artwork tags
                for key in audio_file.tags.keys():
                    if key.startswith('APIC'):
                        artwork_data = audio_file.tags[key].data
                        break
            
            if not artwork_data:
                logger.debug(f"No artwork found in {file_path}")
                return None
            
            # Create artwork directory if it doesn't exist
            os.makedirs(artwork_dir, exist_ok=True)
            
            # Generate filename based on song metadata
            safe_title = "".join(c for c in metadata['title'] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_artist = "".join(c for c in metadata['artist'] if c.isalnum() or c in (' ', '-', '_')).strip()
            artwork_filename = f"{safe_artist}_{safe_title}.jpg"
            artwork_path = os.path.join(artwork_dir, artwork_filename)
            
            # Save artwork as JPEG
            try:
                image = Image.open(io.BytesIO(artwork_data))
                # Convert to RGB if necessary (for PNG with transparency)
                if image.mode in ('RGBA', 'LA', 'P'):
                    image = image.convert('RGB')
                image.save(artwork_path, 'JPEG', quality=85)
                logger.debug(f"Saved artwork to {artwork_path}")
                return artwork_path
                
            except Exception as e:
                logger.warning(f"Could not process artwork from {file_path}: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting artwork from {file_path}: {e}")
            return None
    
    def to_dict(self) -> dict:
        """Convert Song to dictionary for serialization.
        
        Returns:
            Dictionary representation of the song
        """
        return {
            'file_path': self.file_path,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'artwork_path': self.artwork_path,
            'duration': self.duration
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Song':
        """Create Song from dictionary.
        
        Args:
            data: Dictionary containing song data
            
        Returns:
            Song instance
        """
        return cls(
            file_path=data['file_path'],
            title=data['title'],
            artist=data['artist'],
            album=data['album'],
            artwork_path=data.get('artwork_path'),
            duration=data.get('duration', 0.0)
        )
    
    def is_valid(self) -> bool:
        """Check if the song file still exists and is accessible.
        
        Returns:
            True if song file exists and is readable
        """
        try:
            return os.path.exists(self.file_path) and os.access(self.file_path, os.R_OK)
        except Exception:
            return False
    
    def get_display_name(self) -> str:
        """Get formatted display name for the song.
        
        Returns:
            Formatted string like "Artist - Title"
        """
        if self.artist and self.artist != "Unknown Artist":
            return f"{self.artist} - {self.title}"
        return self.title
    
    def __str__(self) -> str:
        """String representation of the song."""
        return self.get_display_name()
    
    def __repr__(self) -> str:
        """Developer representation of the song."""
        return f"Song(title='{self.title}', artist='{self.artist}', file_path='{self.file_path}')"