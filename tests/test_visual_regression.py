"""
Visual regression tests for layout consistency.

Tests that verify the GUI layout remains consistent and meets design
specifications across different window sizes and component states.
"""

import unittest
import tkinter as tk
import tempfile
import shutil
import os
from unittest.mock import Mock, patch
from pathlib import Path

from gui.main_window import MainWindow
from gui.theme import ThemeManager
from core.playlist_manager import PlaylistManager
from core.player_engine import PlayerEngine
from models.song import Song


class TestVisualRegression(unittest.TestCase):
    """Test cases for visual regression and layout consistency."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.playlist_file = os.path.join(self.temp_dir, "test_playlist.json")
        self.artwork_dir = os.path.join(self.temp_dir, "artwork")
        
        # Create test components
        self.playlist_manager = PlaylistManager(self.playlist_file, self.artwork_dir)
        self.player_engine = PlayerEngine()
        
        # Mock pygame to avoid audio initialization
        self.pygame_patcher = patch('core.player_engine.pygame')
        self.mock_pygame = self.pygame_patcher.start()
        self.mock_pygame.mixer.music.get_busy.return_value = False
        
        # Create main window
        self.main_window = MainWindow(self.playlist_manager, self.player_engine)
        self.main_window.root.withdraw()  # Hide window during tests
        
        # Force window to be displayed for geometry calculations
        self.main_window.root.deiconify()
        self.main_window.root.update()
    
    def tearDown(self):
        """Clean up test environment."""
        self.pygame_patcher.stop()
        
        # Destroy GUI components
        try:
            if self.main_window.root and self.main_window.root.winfo_exists():
                self.main_window.root.destroy()
        except tk.TclError:
            pass
        
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_songs(self, count=5):
        """Create test songs for layout testing.
        
        Args:
            count: Number of test songs to create
            
        Returns:
            List of mock Song objects
        """
        songs = []
        for i in range(count):
            song = Mock(spec=Song)
            song.file_path = os.path.join(self.temp_dir, f"song{i}.mp3")
            song.title = f"Test Song {i} with a Long Title"
            song.artist = f"Test Artist {i}"
            song.album = "Test Album"
            song.artwork_path = None
            song.duration = 180.0
            song.get_display_name.return_value = f"Test Artist {i} - Test Song {i} with a Long Title"
            song.is_valid.return_value = True
            songs.append(song)
        return songs
    
    def test_default_window_size_compliance(self):
        """Test that window opens with correct default size."""
        # Get theme specifications
        theme = self.main_window.theme_manager.theme
        
        # Check window geometry
        self.main_window.root.update()
        
        # Get actual window size
        actual_width = self.main_window.root.winfo_width()
        actual_height = self.main_window.root.winfo_height()
        
        # Allow some tolerance for window manager differences
        width_tolerance = 10
        height_tolerance = 10
        
        self.assertAlmostEqual(actual_width, theme.window_width, delta=width_tolerance,
                              msg=f"Window width {actual_width} should be close to {theme.window_width}")
        self.assertAlmostEqual(actual_height, theme.window_height, delta=height_tolerance,
                              msg=f"Window height {actual_height} should be close to {theme.window_height}")
    
    def test_minimum_window_size_constraints(self):
        """Test that window respects minimum size constraints."""
        theme = self.main_window.theme_manager.theme
        
        # Try to resize below minimum
        self.main_window.root.geometry(f"{theme.window_min_width - 50}x{theme.window_min_height - 50}")
        self.main_window.root.update()
        
        # Window should enforce minimum size
        actual_width = self.main_window.root.winfo_width()
        actual_height = self.main_window.root.winfo_height()
        
        self.assertGreaterEqual(actual_width, theme.window_min_width,
                               "Window width should not go below minimum")
        self.assertGreaterEqual(actual_height, theme.window_min_height,
                               "Window height should not go below minimum")
    
    def test_component_height_specifications(self):
        """Test that components maintain specified heights."""
        theme = self.main_window.theme_manager.theme
        
        # Update window to ensure components are rendered
        self.main_window.root.update()
        
        # Test Now Playing component height
        now_playing_height = self.main_window.now_playing_frame.winfo_height()
        self.assertEqual(now_playing_height, theme.now_playing_height,
                        f"Now Playing height should be {theme.now_playing_height}px")
        
        # Test control panel height (if accessible)
        if hasattr(self.main_window, 'controls_frame'):
            controls_height = self.main_window.controls_frame.winfo_height()
            self.assertEqual(controls_height, theme.controls_height,
                           f"Controls height should be {theme.controls_height}px")
    
    def test_playlist_row_height_consistency(self):
        """Test that playlist rows maintain consistent 24px height."""
        # Add test songs to playlist
        songs = self.create_test_songs(5)
        for song in songs:
            self.playlist_manager.get_playlist().songs.append(song)
        
        # Update playlist display
        self.main_window._update_playlist_display()
        self.main_window.root.update()
        
        # Check playlist widget row heights
        playlist_widget = self.main_window.playlist_widget
        theme = self.main_window.theme_manager.theme
        
        # Verify each row has correct height
        for i, row_data in enumerate(playlist_widget._row_widgets):
            if 'frame' in row_data:
                row_frame = row_data['frame']
                # Force widget update to ensure accurate measurements
                row_frame.update_idletasks()
                row_height = row_frame.winfo_height()
                # Allow 1px tolerance for rendering differences
                self.assertAlmostEqual(row_height, theme.playlist_row_height, delta=1,
                                     msg=f"Row {i} height should be {theme.playlist_row_height}px (±1px), got {row_height}px")
    
    def test_responsive_layout_at_different_sizes(self):
        """Test layout responsiveness at different window sizes."""
        test_sizes = [
            (350, 250),  # Minimum size
            (400, 300),  # Default size
            (500, 400),  # Larger size
            (600, 500),  # Even larger size
        ]
        
        for width, height in test_sizes:
            with self.subTest(size=f"{width}x{height}"):
                # Resize window
                self.main_window.root.geometry(f"{width}x{height}")
                self.main_window.root.update()
                
                # Verify window accepted the size (within tolerance)
                actual_width = self.main_window.root.winfo_width()
                actual_height = self.main_window.root.winfo_height()
                
                # Should be close to requested size (allowing for minimum constraints)
                expected_width = max(width, self.main_window.theme_manager.theme.window_min_width)
                expected_height = max(height, self.main_window.theme_manager.theme.window_min_height)
                
                self.assertAlmostEqual(actual_width, expected_width, delta=20,
                                     msg=f"Width should be close to {expected_width}")
                self.assertAlmostEqual(actual_height, expected_height, delta=20,
                                     msg=f"Height should be close to {expected_height}")
                
                # Verify components are still visible and properly arranged
                self._verify_component_visibility()
    
    def _verify_component_visibility(self):
        """Helper method to verify all components are visible and properly arranged."""
        # Update to ensure geometry is calculated
        self.main_window.root.update()
        
        # Check that key components exist and are visible
        components_to_check = [
            ('now_playing_frame', 'Now Playing frame'),
            ('playlist_widget', 'Playlist widget'),
            ('play_button', 'Play button'),
            ('web_display_link', 'Web display link'),
            ('web_controls_link', 'Web controls link'),
        ]
        
        for attr_name, component_name in components_to_check:
            if hasattr(self.main_window, attr_name):
                component = getattr(self.main_window, attr_name)
                
                # Check that component exists
                self.assertIsNotNone(component, f"{component_name} should exist")
                
                # Check that component is visible (has non-zero dimensions)
                try:
                    width = component.winfo_width()
                    height = component.winfo_height()
                    self.assertGreater(width, 0, f"{component_name} should have positive width")
                    self.assertGreater(height, 0, f"{component_name} should have positive height")
                except tk.TclError:
                    # Some components might not be mapped yet
                    pass
    
    def test_text_truncation_at_small_sizes(self):
        """Test that text truncation works properly at small window sizes."""
        # Add a song with a very long title
        long_song = Mock(spec=Song)
        long_song.file_path = os.path.join(self.temp_dir, "long_song.mp3")
        long_song.title = "This is a Very Long Song Title That Should Be Truncated"
        long_song.artist = "Artist with a Very Long Name"
        long_song.album = "Album with a Very Long Name"
        long_song.get_display_name.return_value = f"{long_song.artist} - {long_song.title}"
        long_song.is_valid.return_value = True
        
        # Add to playlist and set as current
        self.playlist_manager.get_playlist().songs.append(long_song)
        self.playlist_manager.set_current_song(0)
        
        # Update display
        self.main_window._update_current_song_display()
        self.main_window._update_playlist_display()
        
        # Resize to minimum width
        theme = self.main_window.theme_manager.theme
        self.main_window.root.geometry(f"{theme.window_min_width}x{theme.window_height}")
        self.main_window.root.update()
        
        # Check that Now Playing text fits within the component
        now_playing_text = self.main_window.current_song_label.cget('text')
        
        # Text should not be empty (should show something)
        self.assertNotEqual(now_playing_text, "")
        
        # If text was truncated, it should end with ellipsis
        if len(now_playing_text) < len(long_song.get_display_name()):
            self.assertTrue(now_playing_text.endswith("...") or "..." in now_playing_text,
                           "Truncated text should contain ellipsis")
    
    def test_control_button_sizing_and_spacing(self):
        """Test that control buttons maintain proper size and spacing."""
        theme = self.main_window.theme_manager.theme
        
        # Update to ensure buttons are rendered
        self.main_window.root.update()
        
        # Check control buttons
        control_buttons = [
            self.main_window.previous_button,
            self.main_window.play_button,
            self.main_window.pause_button,
            self.main_window.stop_button,
            self.main_window.next_button,
        ]
        
        for button in control_buttons:
            # Check button dimensions
            button_width = button.winfo_width()
            button_height = button.winfo_height()
            
            # Control buttons should be approximately square and compact
            # Allow some tolerance for different platforms
            expected_size = theme.control_button_size
            tolerance = 10
            
            self.assertAlmostEqual(button_width, expected_size, delta=tolerance,
                                 msg=f"Control button width should be close to {expected_size}px")
            self.assertAlmostEqual(button_height, expected_size, delta=tolerance,
                                 msg=f"Control button height should be close to {expected_size}px")
    
    def test_file_management_button_sizing(self):
        """Test that file management buttons maintain proper compact sizing."""
        theme = self.main_window.theme_manager.theme
        
        # Update to ensure buttons are rendered
        self.main_window.root.update()
        
        # Find file management buttons (they should be in the main window)
        # This test assumes file management buttons are accessible
        # The exact implementation may vary
        
        # Check that file management area maintains proper height
        # (This is a general layout test since specific button access may vary)
        window_height = self.main_window.root.winfo_height()
        
        # Total fixed height should leave room for playlist
        fixed_components_height = (
            theme.now_playing_height +
            theme.controls_height +
            theme.file_panel_height +
            30  # Web links area
        )
        
        remaining_height = window_height - fixed_components_height
        self.assertGreater(remaining_height, 50, 
                          "Should leave adequate space for playlist after fixed components")
    
    def test_hyperlink_positioning_and_alignment(self):
        """Test that hyperlinks are properly positioned and aligned."""
        # Update to ensure hyperlinks are rendered
        self.main_window.root.update()
        
        # Check that both hyperlinks exist
        self.assertIsNotNone(self.main_window.web_display_link)
        self.assertIsNotNone(self.main_window.web_controls_link)
        
        # Check hyperlink positioning
        display_link = self.main_window.web_display_link
        controls_link = self.main_window.web_controls_link
        
        # Both should be visible
        display_width = display_link.winfo_width()
        display_height = display_link.winfo_height()
        controls_width = controls_link.winfo_width()
        controls_height = controls_link.winfo_height()
        
        self.assertGreater(display_width, 0, "Display link should be visible")
        self.assertGreater(display_height, 0, "Display link should be visible")
        self.assertGreater(controls_width, 0, "Controls link should be visible")
        self.assertGreater(controls_height, 0, "Controls link should be visible")
        
        # Links should be approximately the same height (same row)
        height_tolerance = 5
        self.assertAlmostEqual(display_height, controls_height, delta=height_tolerance,
                              msg="Hyperlinks should have similar heights")
    
    def test_color_consistency_across_components(self):
        """Test that colors are consistently applied across components."""
        theme = self.main_window.theme_manager.theme
        
        # Update to ensure components are styled
        self.main_window.root.update()
        
        # Check root window background
        root_bg = self.main_window.root.cget('bg')
        self.assertEqual(root_bg, theme.bg_primary, 
                        "Root window should have primary background color")
        
        # Check hyperlink colors
        display_link_fg = self.main_window.web_display_link.cget('fg')
        controls_link_fg = self.main_window.web_controls_link.cget('fg')
        
        self.assertEqual(display_link_fg, theme.accent,
                        "Display link should use accent color")
        self.assertEqual(controls_link_fg, theme.accent,
                        "Controls link should use accent color")
        
        # Both hyperlinks should have the same color
        self.assertEqual(display_link_fg, controls_link_fg,
                        "Both hyperlinks should have the same color")
    
    def test_layout_stability_with_content_changes(self):
        """Test that layout remains stable when content changes."""
        # Record initial component positions
        self.main_window.root.update()
        
        initial_positions = {}
        components = [
            ('now_playing_frame', self.main_window.now_playing_frame),
            ('web_display_link', self.main_window.web_display_link),
            ('web_controls_link', self.main_window.web_controls_link),
        ]
        
        for name, component in components:
            initial_positions[name] = {
                'x': component.winfo_x(),
                'y': component.winfo_y(),
                'width': component.winfo_width(),
                'height': component.winfo_height(),
            }
        
        # Add songs to playlist (content change)
        songs = self.create_test_songs(10)
        for song in songs:
            self.playlist_manager.get_playlist().songs.append(song)
        
        # Update display
        self.main_window._update_playlist_display()
        self.main_window.root.update()
        
        # Check that fixed components maintained their positions
        for name, component in components:
            if name != 'playlist_widget':  # Playlist content is expected to change
                current_pos = {
                    'x': component.winfo_x(),
                    'y': component.winfo_y(),
                    'width': component.winfo_width(),
                    'height': component.winfo_height(),
                }
                
                initial_pos = initial_positions[name]
                
                # Positions should be stable (allowing small tolerance)
                tolerance = 5
                self.assertAlmostEqual(current_pos['x'], initial_pos['x'], delta=tolerance,
                                     msg=f"{name} x position should be stable")
                self.assertAlmostEqual(current_pos['y'], initial_pos['y'], delta=tolerance,
                                     msg=f"{name} y position should be stable")
                
                # Fixed height components should maintain height
                if name == 'now_playing_frame':
                    self.assertEqual(current_pos['height'], initial_pos['height'],
                                   f"{name} height should remain fixed")
    
    def test_grid_layout_consistency(self):
        """Test that grid layout is consistent and properly configured."""
        # Update to ensure layout is applied
        self.main_window.root.update()
        
        # Check that root window has proper grid configuration
        # Row 1 (playlist) should have weight=1 for expansion
        root_grid_info = self.main_window.root.grid_slaves()
        
        # Should have multiple components in grid
        self.assertGreater(len(root_grid_info), 0, "Root should have grid components")
        
        # Check that components are in expected grid positions
        # This is a basic layout sanity check
        for widget in root_grid_info:
            grid_info = widget.grid_info()
            
            # All widgets should have valid grid positions
            self.assertIsNotNone(grid_info.get('row'), "Widget should have row position")
            self.assertIsNotNone(grid_info.get('column'), "Widget should have column position")
            
            # Row and column should be non-negative
            self.assertGreaterEqual(int(grid_info['row']), 0, "Row should be non-negative")
            self.assertGreaterEqual(int(grid_info['column']), 0, "Column should be non-negative")


if __name__ == '__main__':
    unittest.main()