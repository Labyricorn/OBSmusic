"""
Test configuration for GUI modernization tests.

Contains shared test utilities, fixtures, and configuration
for all GUI modernization test modules.
"""

import os
import tempfile
import shutil
import tkinter as tk
from unittest.mock import Mock, patch
from pathlib import Path

from models.song import Song


class TestConfig:
    """Configuration and utilities for GUI modernization tests."""
    
    # Test data constants
    DEFAULT_WINDOW_WIDTH = 400
    DEFAULT_WINDOW_HEIGHT = 300
    MIN_WINDOW_WIDTH = 350
    MIN_WINDOW_HEIGHT = 250
    
    # Component height constants
    NOW_PLAYING_HEIGHT = 60
    CONTROLS_HEIGHT = 30
    FILE_PANEL_HEIGHT = 30
    PLAYLIST_ROW_HEIGHT = 24
    
    # Color constants
    PRIMARY_BG = "#2b2b2b"
    SECONDARY_BG = "#3c3c3c"
    ACCENT_COLOR = "#4a9eff"
    SUCCESS_COLOR = "#00d084"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#b0b0b0"
    
    # Font constants
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_BODY = 11
    FONT_SIZE_SMALL = 9
    FONT_SIZE_TITLE = 14
    
    # Spacing constants
    SPACING_SMALL = 4
    SPACING_MEDIUM = 8
    SPACING_LARGE = 16
    
    @staticmethod
    def create_temp_directory():
        """Create temporary directory for test files.
        
        Returns:
            str: Path to temporary directory
        """
        return tempfile.mkdtemp()
    
    @staticmethod
    def cleanup_temp_directory(temp_dir):
        """Clean up temporary directory.
        
        Args:
            temp_dir: Path to temporary directory to clean up
        """
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @staticmethod
    def create_mock_song(title="Test Song", artist="Test Artist", index=0, file_path=None):
        """Create a mock Song object for testing.
        
        Args:
            title: Song title
            artist: Song artist
            index: Song index (for unique file paths)
            file_path: Custom file path (optional)
            
        Returns:
            Mock Song object
        """
        if file_path is None:
            file_path = f"/tmp/test_song_{index}.mp3"
        
        song = Mock(spec=Song)
        song.file_path = file_path
        song.title = title
        song.artist = artist
        song.album = "Test Album"
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
    
    @staticmethod
    def create_test_songs(count=3, prefix="Song"):
        """Create multiple test songs.
        
        Args:
            count: Number of songs to create
            prefix: Prefix for song titles
            
        Returns:
            List of mock Song objects
        """
        songs = []
        for i in range(count):
            song = TestConfig.create_mock_song(
                title=f"{prefix} {i}",
                artist=f"Artist {i}",
                index=i
            )
            songs.append(song)
        return songs
    
    @staticmethod
    def setup_pygame_mock():
        """Set up pygame mock for tests.
        
        Returns:
            Mock object and patcher
        """
        patcher = patch('core.player_engine.pygame')
        mock_pygame = patcher.start()
        mock_pygame.mixer.music.get_busy.return_value = False
        return mock_pygame, patcher
    
    @staticmethod
    def create_test_window():
        """Create a test Tkinter window.
        
        Returns:
            tk.Tk: Test window (withdrawn/hidden)
        """
        root = tk.Tk()
        root.withdraw()  # Hide window during tests
        return root
    
    @staticmethod
    def destroy_test_window(root):
        """Safely destroy test window.
        
        Args:
            root: Tkinter root window to destroy
        """
        try:
            if root and root.winfo_exists():
                root.destroy()
        except tk.TclError:
            pass
    
    @staticmethod
    def assert_color_format(color_string):
        """Assert that a color string is in valid hex format.
        
        Args:
            color_string: Color string to validate
            
        Returns:
            bool: True if valid hex color format
        """
        if not isinstance(color_string, str):
            return False
        
        if not color_string.startswith('#'):
            return False
        
        if len(color_string) != 7:
            return False
        
        try:
            int(color_string[1:], 16)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def assert_font_tuple(font_tuple):
        """Assert that a font tuple is valid for Tkinter.
        
        Args:
            font_tuple: Font tuple to validate
            
        Returns:
            bool: True if valid font tuple
        """
        if not isinstance(font_tuple, tuple):
            return False
        
        if len(font_tuple) < 2 or len(font_tuple) > 3:
            return False
        
        # First element should be font family (string)
        if not isinstance(font_tuple[0], str):
            return False
        
        # Second element should be font size (int)
        if not isinstance(font_tuple[1], int):
            return False
        
        # Third element (if present) should be font weight (string)
        if len(font_tuple) == 3 and not isinstance(font_tuple[2], str):
            return False
        
        return True
    
    @staticmethod
    def get_test_urls():
        """Get test URLs for hyperlink testing.
        
        Returns:
            dict: Dictionary of test URLs
        """
        return {
            'display': 'http://localhost:8080/display',
            'controls': 'http://localhost:8080/controls'
        }
    
    @staticmethod
    def create_mock_event(x=100, y=100, x_root=100, y_root=100):
        """Create a mock Tkinter event for testing.
        
        Args:
            x: Local x coordinate
            y: Local y coordinate
            x_root: Root x coordinate
            y_root: Root y coordinate
            
        Returns:
            Mock event object
        """
        event = Mock()
        event.x = x
        event.y = y
        event.x_root = x_root
        event.y_root = y_root
        return event


class TestFixtures:
    """Common test fixtures for GUI modernization tests."""
    
    @staticmethod
    def setup_basic_test_environment():
        """Set up basic test environment with temp directory and mocks.
        
        Returns:
            dict: Dictionary containing test environment components
        """
        temp_dir = TestConfig.create_temp_directory()
        playlist_file = os.path.join(temp_dir, "test_playlist.json")
        artwork_dir = os.path.join(temp_dir, "artwork")
        
        mock_pygame, pygame_patcher = TestConfig.setup_pygame_mock()
        
        return {
            'temp_dir': temp_dir,
            'playlist_file': playlist_file,
            'artwork_dir': artwork_dir,
            'mock_pygame': mock_pygame,
            'pygame_patcher': pygame_patcher
        }
    
    @staticmethod
    def cleanup_test_environment(env):
        """Clean up test environment.
        
        Args:
            env: Environment dictionary from setup_basic_test_environment
        """
        if 'pygame_patcher' in env:
            env['pygame_patcher'].stop()
        
        if 'temp_dir' in env:
            TestConfig.cleanup_temp_directory(env['temp_dir'])


# Test data for various scenarios
TEST_SCENARIOS = {
    'empty_playlist': {
        'songs': [],
        'current_index': None,
        'description': 'Empty playlist scenario'
    },
    'single_song': {
        'songs': TestConfig.create_test_songs(1),
        'current_index': 0,
        'description': 'Single song playlist'
    },
    'multiple_songs': {
        'songs': TestConfig.create_test_songs(5),
        'current_index': 2,
        'description': 'Multiple songs with middle song current'
    },
    'long_titles': {
        'songs': [
            TestConfig.create_mock_song(
                "This is a Very Long Song Title That Should Be Truncated",
                "Artist with a Very Long Name That Should Also Be Truncated",
                0
            )
        ],
        'current_index': 0,
        'description': 'Songs with long titles for truncation testing'
    }
}

# Window size test scenarios
WINDOW_SIZE_SCENARIOS = [
    {'width': 350, 'height': 250, 'description': 'Minimum size'},
    {'width': 400, 'height': 300, 'description': 'Default size'},
    {'width': 500, 'height': 400, 'description': 'Medium size'},
    {'width': 600, 'height': 500, 'description': 'Large size'},
    {'width': 800, 'height': 600, 'description': 'Extra large size'},
]