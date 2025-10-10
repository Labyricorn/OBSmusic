"""
Unit tests for the modern theme system and component styling.

Tests the ModernTheme dataclass, ThemeManager functionality,
and styling application across GUI components.
"""

import unittest
import tkinter as tk
from tkinter import ttk
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import platform

from gui.theme import ModernTheme, ThemeManager


class TestModernTheme(unittest.TestCase):
    """Test cases for ModernTheme dataclass."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.theme = ModernTheme()
    
    def test_default_color_palette(self):
        """Test that default color palette is properly defined."""
        # Primary colors
        self.assertEqual(self.theme.bg_primary, "#2b2b2b")
        self.assertEqual(self.theme.bg_secondary, "#3c3c3c")
        self.assertEqual(self.theme.bg_tertiary, "#4a4a4a")
        self.assertEqual(self.theme.accent, "#4a9eff")
        
        # Text colors
        self.assertEqual(self.theme.text_primary, "#ffffff")
        self.assertEqual(self.theme.text_secondary, "#b0b0b0")
        
        # Status colors
        self.assertEqual(self.theme.success, "#00d084")
        self.assertEqual(self.theme.warning, "#ff6b35")
        self.assertEqual(self.theme.error, "#ff4757")
    
    def test_typography_settings(self):
        """Test typography configuration."""
        self.assertEqual(self.theme.font_family, "Segoe UI")
        self.assertEqual(self.theme.font_family_fallback, "Arial")
        self.assertEqual(self.theme.font_size_title, 14)
        self.assertEqual(self.theme.font_size_body, 11)
        self.assertEqual(self.theme.font_size_small, 9)
        self.assertEqual(self.theme.font_weight_regular, "normal")
        self.assertEqual(self.theme.font_weight_medium, "bold")
        self.assertEqual(self.theme.font_weight_bold, "bold")
    
    def test_spacing_system(self):
        """Test spacing system based on 8px grid."""
        self.assertEqual(self.theme.spacing_xs, 2)
        self.assertEqual(self.theme.spacing_small, 4)
        self.assertEqual(self.theme.spacing_medium, 8)
        self.assertEqual(self.theme.spacing_large, 16)
        self.assertEqual(self.theme.spacing_xl, 24)
    
    def test_component_dimensions(self):
        """Test component dimension specifications."""
        # Window dimensions
        self.assertEqual(self.theme.window_width, 400)
        self.assertEqual(self.theme.window_height, 300)
        self.assertEqual(self.theme.window_min_width, 350)
        self.assertEqual(self.theme.window_min_height, 250)
        
        # Component heights
        self.assertEqual(self.theme.now_playing_height, 60)
        self.assertEqual(self.theme.controls_height, 30)
        self.assertEqual(self.theme.file_panel_height, 30)
        self.assertEqual(self.theme.playlist_row_height, 24)
        
        # Button dimensions
        self.assertEqual(self.theme.control_button_size, 24)
        self.assertEqual(self.theme.file_button_width, 80)
        self.assertEqual(self.theme.file_button_height, 24)
    
    def test_get_font_method(self):
        """Test font tuple generation for Tkinter."""
        # Default font
        font = self.theme.get_font()
        self.assertEqual(font, ("Segoe UI", 11, "normal"))
        
        # Custom size and weight
        font = self.theme.get_font(size=14, weight="bold")
        self.assertEqual(font, ("Segoe UI", 14, "bold"))
        
        # Partial customization
        font = self.theme.get_font(size=12)
        self.assertEqual(font, ("Segoe UI", 12, "normal"))
        
        font = self.theme.get_font(weight="bold")
        self.assertEqual(font, ("Segoe UI", 11, "bold"))
    
    def test_get_fallback_font_method(self):
        """Test fallback font tuple generation."""
        # Default fallback font
        font = self.theme.get_fallback_font()
        self.assertEqual(font, ("Arial", 11, "normal"))
        
        # Custom fallback font
        font = self.theme.get_fallback_font(size=10, weight="bold")
        self.assertEqual(font, ("Arial", 10, "bold"))


class TestThemeManager(unittest.TestCase):
    """Test cases for ThemeManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests
        self.theme_manager = ThemeManager()
    
    def tearDown(self):
        """Clean up test fixtures."""
        try:
            if self.root and self.root.winfo_exists():
                self.root.destroy()
        except tk.TclError:
            pass
    
    def test_theme_manager_initialization(self):
        """Test ThemeManager initialization."""
        # Default theme
        manager = ThemeManager()
        self.assertIsInstance(manager.theme, ModernTheme)
        self.assertFalse(manager._theme_applied)
        
        # Custom theme
        custom_theme = ModernTheme()
        custom_theme.bg_primary = "#123456"
        manager = ThemeManager(custom_theme)
        self.assertEqual(manager.theme.bg_primary, "#123456")
    
    @patch('platform.system')
    def test_platform_specific_font_adjustment(self, mock_system):
        """Test platform-specific font adjustments."""
        # Test macOS
        mock_system.return_value = "Darwin"
        manager = ThemeManager()
        self.assertEqual(manager.theme.font_family, "SF Pro Display")
        
        # Test Linux
        mock_system.return_value = "Linux"
        manager = ThemeManager()
        self.assertEqual(manager.theme.font_family, "Ubuntu")
        
        # Test Windows (default)
        mock_system.return_value = "Windows"
        manager = ThemeManager()
        self.assertEqual(manager.theme.font_family, "Segoe UI")
    
    def test_apply_theme_success(self):
        """Test successful theme application."""
        result = self.theme_manager.apply_theme(self.root)
        
        self.assertTrue(result)
        self.assertTrue(self.theme_manager._theme_applied)
        self.assertIsNotNone(self.theme_manager._style)
        
        # Check that root window was configured
        self.assertEqual(self.root.cget("bg"), self.theme_manager.theme.bg_primary)
    
    def test_apply_theme_with_errors(self):
        """Test theme application with simulated errors."""
        # Mock root.configure to raise an exception
        original_configure = self.root.configure
        
        def mock_configure(**kwargs):
            if 'bg' in kwargs:
                raise tk.TclError("Simulated error")
            return original_configure(**kwargs)
        
        self.root.configure = mock_configure
        
        # Should still succeed with fallback
        result = self.theme_manager.apply_theme(self.root)
        self.assertTrue(result)  # Should handle errors gracefully
    
    def test_get_listbox_config(self):
        """Test Listbox configuration generation."""
        config = self.theme_manager.get_listbox_config()
        
        expected_keys = ['bg', 'fg', 'selectbackground', 'selectforeground', 
                        'font', 'borderwidth', 'highlightthickness', 'activestyle']
        
        for key in expected_keys:
            self.assertIn(key, config)
        
        self.assertEqual(config['bg'], self.theme_manager.theme.bg_secondary)
        self.assertEqual(config['fg'], self.theme_manager.theme.text_primary)
        self.assertEqual(config['selectbackground'], self.theme_manager.theme.accent)
        self.assertEqual(config['borderwidth'], 0)
        self.assertEqual(config['highlightthickness'], 0)
        self.assertEqual(config['activestyle'], "none")
    
    def test_get_hyperlink_config(self):
        """Test hyperlink configuration generation."""
        config = self.theme_manager.get_hyperlink_config()
        
        expected_keys = ['bg', 'fg', 'font', 'cursor']
        
        for key in expected_keys:
            self.assertIn(key, config)
        
        self.assertEqual(config['bg'], self.theme_manager.theme.bg_primary)
        self.assertEqual(config['fg'], self.theme_manager.theme.accent)
        self.assertEqual(config['cursor'], "hand2")
        self.assertIsInstance(config['font'], tuple)
    
    def test_get_music_note_config(self):
        """Test music note indicator configuration."""
        config = self.theme_manager.get_music_note_config()
        
        expected_keys = ['symbol', 'color', 'font']
        
        for key in expected_keys:
            self.assertIn(key, config)
        
        self.assertEqual(config['symbol'], "♪")
        self.assertEqual(config['color'], self.theme_manager.theme.success)
        self.assertIsInstance(config['font'], tuple)
    
    def test_get_alternating_row_colors(self):
        """Test alternating row color generation."""
        primary, alternate = self.theme_manager.get_alternating_row_colors()
        
        self.assertEqual(primary, self.theme_manager.theme.bg_secondary)
        self.assertEqual(alternate, self.theme_manager.theme.bg_primary)
        self.assertNotEqual(primary, alternate)
    
    def test_create_modern_frame(self):
        """Test modern frame creation."""
        frame = self.theme_manager.create_modern_frame(self.root)
        
        self.assertIsInstance(frame, ttk.Frame)
        # Frame should be created successfully
        self.assertIsNotNone(frame)
    
    def test_create_modern_label(self):
        """Test modern label creation with different styles."""
        # Normal label
        label = self.theme_manager.create_modern_label(self.root, "Test", "normal")
        self.assertIsInstance(label, ttk.Label)
        self.assertEqual(label.cget("text"), "Test")
        
        # Title label
        title_label = self.theme_manager.create_modern_label(self.root, "Title", "title")
        self.assertIsInstance(title_label, ttk.Label)
        
        # Secondary label
        secondary_label = self.theme_manager.create_modern_label(self.root, "Secondary", "secondary")
        self.assertIsInstance(secondary_label, ttk.Label)
        
        # Now playing label
        now_playing_label = self.theme_manager.create_modern_label(self.root, "Now Playing", "now_playing")
        self.assertIsInstance(now_playing_label, ttk.Label)
    
    def test_create_modern_button(self):
        """Test modern button creation."""
        button = self.theme_manager.create_modern_button(self.root, "Test Button")
        
        self.assertIsInstance(button, ttk.Button)
        self.assertEqual(button.cget("text"), "Test Button")
    
    def test_create_modern_control_button(self):
        """Test modern control button creation."""
        button = self.theme_manager.create_modern_control_button(self.root, "▶")
        
        self.assertIsInstance(button, ttk.Button)
        self.assertEqual(button.cget("text"), "▶")
    
    def test_create_modern_file_button(self):
        """Test modern file button creation."""
        button = self.theme_manager.create_modern_file_button(self.root, "Add Songs")
        
        self.assertIsInstance(button, ttk.Button)
        self.assertEqual(button.cget("text"), "Add Songs")
    
    def test_create_modern_checkbutton(self):
        """Test modern checkbutton creation."""
        var = tk.BooleanVar()
        checkbutton = self.theme_manager.create_modern_checkbutton(self.root, "Loop", variable=var)
        
        self.assertIsInstance(checkbutton, ttk.Checkbutton)
        self.assertEqual(checkbutton.cget("text"), "Loop")
    
    def test_fallback_theme_application(self):
        """Test fallback theme application when main theme fails."""
        # Create a new theme manager for this test
        test_theme_manager = ThemeManager()
        
        # Force theme application to fail by providing invalid root
        invalid_root = None
        
        result = test_theme_manager.apply_theme(invalid_root)
        # The method returns True even with failures as it applies fallback gracefully
        # But the theme should not be marked as fully applied
        self.assertTrue(result)  # Method succeeds with fallback
        # However, individual configuration steps should have failed
        self.assertEqual(test_theme_manager._root, invalid_root)
    
    def test_ttk_style_configuration(self):
        """Test TTK style configuration."""
        # Apply theme first
        self.theme_manager.apply_theme(self.root)
        
        # Check that TTK styles were configured
        style = self.theme_manager._style
        self.assertIsNotNone(style)
        
        # Test that specific styles exist
        style_names = [
            "Modern.TFrame",
            "ModernSecondary.TFrame", 
            "Modern.TLabel",
            "ModernTitle.TLabel",
            "ModernSecondary.TLabel",
            "ModernNowPlaying.TLabel",
            "Modern.TButton",
            "ModernControl.TButton",
            "ModernControlActive.TButton",
            "ModernFile.TButton",
            "Modern.TCheckbutton",
            "Modern.Vertical.TScrollbar"
        ]
        
        # Note: We can't easily test if styles were actually configured
        # without accessing internal TTK state, but we can verify the
        # style object exists and no exceptions were raised
        self.assertIsInstance(style, ttk.Style)
    
    def test_text_truncation_utility(self):
        """Test text truncation utility method if available."""
        # This test assumes the theme manager has a text truncation method
        # If not implemented, this test can be skipped or the method added
        if hasattr(self.theme_manager, 'truncate_text'):
            # Test normal text (should not be truncated)
            short_text = "Short text"
            result = self.theme_manager.truncate_text(short_text, 200, ("Arial", 10))
            self.assertEqual(result, short_text)
            
            # Test long text (should be truncated)
            long_text = "This is a very long text that should be truncated"
            result = self.theme_manager.truncate_text(long_text, 50, ("Arial", 10))
            self.assertTrue(len(result) <= len(long_text))
            if result != long_text:
                self.assertTrue(result.endswith("..."))
    
    def test_theme_consistency(self):
        """Test that theme colors and values are consistent."""
        theme = self.theme_manager.theme
        
        # Check that background colors have proper hierarchy
        # (primary should be darker than secondary for dark theme)
        self.assertNotEqual(theme.bg_primary, theme.bg_secondary)
        self.assertNotEqual(theme.bg_secondary, theme.bg_tertiary)
        
        # Check that text colors contrast with backgrounds
        self.assertNotEqual(theme.text_primary, theme.bg_primary)
        self.assertNotEqual(theme.text_secondary, theme.bg_secondary)
        
        # Check that accent color is different from backgrounds
        self.assertNotEqual(theme.accent, theme.bg_primary)
        self.assertNotEqual(theme.accent, theme.bg_secondary)
        
        # Check that spacing values follow 8px grid system
        self.assertEqual(theme.spacing_medium, 8)
        self.assertEqual(theme.spacing_large, theme.spacing_medium * 2)
        self.assertEqual(theme.spacing_small, theme.spacing_medium // 2)
    
    def test_component_size_constraints(self):
        """Test that component sizes meet design requirements."""
        theme = self.theme_manager.theme
        
        # Window size constraints
        self.assertEqual(theme.window_width, 400)
        self.assertEqual(theme.window_height, 300)
        self.assertLess(theme.window_min_width, theme.window_width)
        self.assertLess(theme.window_min_height, theme.window_height)
        
        # Component height constraints
        self.assertEqual(theme.now_playing_height, 60)
        self.assertEqual(theme.controls_height, 30)
        self.assertEqual(theme.file_panel_height, 30)
        self.assertEqual(theme.playlist_row_height, 24)
        
        # Button size constraints
        self.assertEqual(theme.control_button_size, 24)
        self.assertEqual(theme.file_button_width, 80)
        self.assertEqual(theme.file_button_height, 24)
        
        # Verify total height calculation makes sense
        fixed_height = (theme.now_playing_height + 
                       theme.controls_height + 
                       theme.file_panel_height + 
                       30)  # Web links estimated height
        self.assertLess(fixed_height, theme.window_height)


if __name__ == '__main__':
    unittest.main()