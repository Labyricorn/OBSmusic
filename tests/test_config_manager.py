"""
Unit tests for configuration manager.
"""

import unittest
import tempfile
import os
import json
import shutil
from unittest.mock import patch, mock_open

from core.config_manager import ConfigManager, WebDisplayConfig


class TestWebDisplayConfig(unittest.TestCase):
    """Test WebDisplayConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = WebDisplayConfig()
        
        self.assertEqual(config.font_family, "Arial")
        self.assertEqual(config.font_size, 24)
        self.assertEqual(config.font_weight, "normal")
        self.assertEqual(config.background_color, "#000000")
        self.assertEqual(config.text_color, "#ffffff")
        self.assertEqual(config.accent_color, "#ff6b6b")
        self.assertTrue(config.show_artwork)
        self.assertEqual(config.artwork_size, 200)
        self.assertEqual(config.layout, "horizontal")

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = WebDisplayConfig(
            font_family="Helvetica",
            font_size=18,
            background_color="#123456"
        )
        
        result = config.to_dict()
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['font_family'], "Helvetica")
        self.assertEqual(result['font_size'], 18)
        self.assertEqual(result['background_color'], "#123456")

    def test_from_dict_valid_data(self):
        """Test creation from valid dictionary."""
        data = {
            'font_family': 'Times',
            'font_size': 20,
            'font_weight': 'bold',
            'background_color': '#ff0000',
            'text_color': '#00ff00',
            'accent_color': '#0000ff',
            'show_artwork': False,
            'artwork_size': 150,
            'layout': 'vertical'
        }
        
        config = WebDisplayConfig.from_dict(data)
        
        self.assertEqual(config.font_family, 'Times')
        self.assertEqual(config.font_size, 20)
        self.assertEqual(config.font_weight, 'bold')
        self.assertEqual(config.background_color, '#ff0000')
        self.assertEqual(config.text_color, '#00ff00')
        self.assertEqual(config.accent_color, '#0000ff')
        self.assertFalse(config.show_artwork)
        self.assertEqual(config.artwork_size, 150)
        self.assertEqual(config.layout, 'vertical')

    def test_from_dict_invalid_data_uses_defaults(self):
        """Test that invalid data falls back to defaults."""
        data = {
            'font_size': -5,  # Invalid: negative
            'font_weight': 'invalid',  # Invalid: not in allowed values
            'background_color': 'not-a-color',  # Invalid: not hex
            'show_artwork': 'yes',  # Invalid: not boolean
            'artwork_size': 0,  # Invalid: zero
            'layout': 'diagonal'  # Invalid: not in allowed values
        }
        
        config = WebDisplayConfig.from_dict(data)
        
        # Should use defaults for invalid values
        self.assertEqual(config.font_size, 24)
        self.assertEqual(config.font_weight, "normal")
        self.assertEqual(config.background_color, "#000000")
        self.assertTrue(config.show_artwork)
        self.assertEqual(config.artwork_size, 200)
        self.assertEqual(config.layout, "horizontal")

    def test_from_dict_partial_data(self):
        """Test creation from partial dictionary."""
        data = {
            'font_size': 30,
            'text_color': '#cccccc'
        }
        
        config = WebDisplayConfig.from_dict(data)
        
        # Updated values
        self.assertEqual(config.font_size, 30)
        self.assertEqual(config.text_color, '#cccccc')
        
        # Default values for missing fields
        self.assertEqual(config.font_family, "Arial")
        self.assertEqual(config.background_color, "#000000")

    def test_is_valid_color(self):
        """Test color validation."""
        # Valid colors
        self.assertTrue(WebDisplayConfig._is_valid_color('#000000'))
        self.assertTrue(WebDisplayConfig._is_valid_color('#fff'))
        self.assertTrue(WebDisplayConfig._is_valid_color('#123ABC'))
        
        # Invalid colors
        self.assertFalse(WebDisplayConfig._is_valid_color('000000'))  # No #
        self.assertFalse(WebDisplayConfig._is_valid_color('#'))  # Too short
        self.assertFalse(WebDisplayConfig._is_valid_color('#12'))  # Too short
        self.assertFalse(WebDisplayConfig._is_valid_color('#12345'))  # Wrong length
        self.assertFalse(WebDisplayConfig._is_valid_color('#1234567'))  # Too long
        self.assertFalse(WebDisplayConfig._is_valid_color('#gggggg'))  # Invalid hex


class TestConfigManager(unittest.TestCase):
    """Test ConfigManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'test_config.json')
        self.manager = ConfigManager(self.config_file)

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_load_config_no_file_returns_default(self):
        """Test loading config when no file exists returns default."""
        config = self.manager.load_config()
        
        self.assertIsInstance(config, WebDisplayConfig)
        self.assertEqual(config.font_family, "Arial")
        self.assertEqual(config.font_size, 24)

    def test_load_config_valid_file(self):
        """Test loading config from valid file."""
        test_data = {
            'font_family': 'Helvetica',
            'font_size': 18,
            'background_color': '#123456'
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_data, f)
        
        config = self.manager.load_config()
        
        self.assertEqual(config.font_family, 'Helvetica')
        self.assertEqual(config.font_size, 18)
        self.assertEqual(config.background_color, '#123456')

    def test_load_config_invalid_json_returns_default(self):
        """Test loading config from invalid JSON returns default."""
        with open(self.config_file, 'w') as f:
            f.write('invalid json content')
        
        config = self.manager.load_config()
        
        # Should return default config
        self.assertEqual(config.font_family, "Arial")
        self.assertEqual(config.font_size, 24)

    def test_save_config(self):
        """Test saving configuration."""
        config = WebDisplayConfig(
            font_family='Times',
            font_size=20,
            background_color='#ff0000'
        )
        
        result = self.manager.save_config(config)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.config_file))
        
        # Verify saved content
        with open(self.config_file, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data['font_family'], 'Times')
        self.assertEqual(saved_data['font_size'], 20)
        self.assertEqual(saved_data['background_color'], '#ff0000')

    def test_save_config_creates_directory(self):
        """Test that save_config creates directory if it doesn't exist."""
        nested_path = os.path.join(self.temp_dir, 'nested', 'config.json')
        manager = ConfigManager(nested_path)
        
        config = WebDisplayConfig()
        result = manager.save_config(config)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(nested_path))

    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_save_config_io_error(self, mock_file):
        """Test save_config handles IO errors gracefully."""
        config = WebDisplayConfig()
        
        result = self.manager.save_config(config)
        
        self.assertFalse(result)

    def test_update_config(self):
        """Test updating configuration."""
        # First save a config
        initial_config = WebDisplayConfig(font_size=20)
        self.manager.save_config(initial_config)
        
        # Update it
        updated_config = self.manager.update_config(
            font_size=30,
            background_color='#ff0000'
        )
        
        self.assertEqual(updated_config.font_size, 30)
        self.assertEqual(updated_config.background_color, '#ff0000')
        
        # Verify it was saved
        loaded_config = self.manager.load_config()
        self.assertEqual(loaded_config.font_size, 30)
        self.assertEqual(loaded_config.background_color, '#ff0000')

    def test_get_config(self):
        """Test getting current configuration."""
        config = self.manager.get_config()
        
        self.assertIsInstance(config, WebDisplayConfig)

    def test_reset_to_defaults(self):
        """Test resetting configuration to defaults."""
        # First save a modified config
        modified_config = WebDisplayConfig(
            font_size=30,
            background_color='#ff0000'
        )
        self.manager.save_config(modified_config)
        
        # Reset to defaults
        default_config = self.manager.reset_to_defaults()
        
        self.assertEqual(default_config.font_size, 24)
        self.assertEqual(default_config.background_color, '#000000')
        
        # Verify it was saved
        loaded_config = self.manager.load_config()
        self.assertEqual(loaded_config.font_size, 24)
        self.assertEqual(loaded_config.background_color, '#000000')

    def test_config_caching(self):
        """Test that configuration is cached after first load."""
        # Load config first time
        config1 = self.manager.load_config()
        
        # Modify file externally
        test_data = {'font_size': 50}
        with open(self.config_file, 'w') as f:
            json.dump(test_data, f)
        
        # Load again - should return cached version
        config2 = self.manager.load_config()
        
        self.assertEqual(config1.font_size, config2.font_size)
        self.assertEqual(config2.font_size, 24)  # Original default, not 50


if __name__ == '__main__':
    unittest.main()