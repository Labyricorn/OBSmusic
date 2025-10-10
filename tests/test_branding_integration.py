"""
Tests for icon loading and branding integration functionality.

Tests the BrandingConfig and BrandingManager classes for proper
icon loading, window branding, and error handling as specified in requirements.
"""

import unittest
import tempfile
import shutil
import os
import tkinter as tk
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open

from gui.branding_config import BrandingConfig, BrandingManager, get_branding_manager, apply_window_branding


class TestBrandingConfig(unittest.TestCase):
    """Test cases for BrandingConfig class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_icon_path = os.path.join(self.temp_dir, "test_icon.ico")
        
        # Create a dummy icon file
        with open(self.test_icon_path, 'wb') as f:
            f.write(b'\x00\x00\x01\x00')  # Minimal ICO header
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_configuration(self):
        """Test default configuration values."""
        config = BrandingConfig()
        
        self.assertEqual(config.app_title, "OBSmusic")
        self.assertEqual(config.icon_path, "OBSmusic.ico")
        self.assertEqual(config.window_icon_size, (32, 32))
        self.assertEqual(config.favicon_size, (16, 16))
    
    def test_custom_configuration(self):
        """Test custom configuration values."""
        config = BrandingConfig(
            app_title="Custom App",
            icon_path="custom_icon.ico",
            window_icon_size=(48, 48),
            favicon_size=(32, 32)
        )
        
        self.assertEqual(config.app_title, "Custom App")
        self.assertEqual(config.icon_path, "custom_icon.ico")
        self.assertEqual(config.window_icon_size, (48, 48))
        self.assertEqual(config.favicon_size, (32, 32))
    
    def test_get_icon_path(self):
        """Test getting absolute icon path."""
        config = BrandingConfig(icon_path=self.test_icon_path)
        icon_path = config.get_icon_path()
        
        self.assertIsInstance(icon_path, Path)
        self.assertTrue(icon_path.is_absolute())
        self.assertEqual(str(icon_path), str(Path(self.test_icon_path).resolve()))
    
    def test_icon_exists_true(self):
        """Test icon_exists returns True when file exists."""
        config = BrandingConfig(icon_path=self.test_icon_path)
        self.assertTrue(config.icon_exists())
    
    def test_icon_exists_false(self):
        """Test icon_exists returns False when file doesn't exist."""
        non_existent_path = os.path.join(self.temp_dir, "non_existent.ico")
        config = BrandingConfig(icon_path=non_existent_path)
        self.assertFalse(config.icon_exists())
    
    def test_get_icon_path_str(self):
        """Test getting icon path as string."""
        config = BrandingConfig(icon_path=self.test_icon_path)
        icon_path_str = config.get_icon_path_str()
        
        self.assertIsInstance(icon_path_str, str)
        self.assertEqual(icon_path_str, str(Path(self.test_icon_path).resolve()))


class TestBrandingManager(unittest.TestCase):
    """Test cases for BrandingManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_icon_path = os.path.join(self.temp_dir, "test_icon.ico")
        
        # Create a dummy icon file
        with open(self.test_icon_path, 'wb') as f:
            f.write(b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00h\x05\x00\x00\x16\x00\x00\x00')
        
        self.config = BrandingConfig(
            app_title="Test App",
            icon_path=self.test_icon_path
        )
        self.manager = BrandingManager(self.config)
        
        # Create a test Tkinter window
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests
    
    def tearDown(self):
        """Clean up test environment."""
        try:
            if self.root and self.root.winfo_exists():
                self.root.destroy()
        except tk.TclError:
            pass
        
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization_with_config(self):
        """Test manager initialization with provided config."""
        self.assertEqual(self.manager.config, self.config)
    
    def test_initialization_without_config(self):
        """Test manager initialization without provided config."""
        manager = BrandingManager()
        
        self.assertIsInstance(manager.config, BrandingConfig)
        self.assertEqual(manager.config.app_title, "OBSmusic")
    
    def test_apply_window_branding_success(self):
        """Test successful window branding application."""
        result = self.manager.apply_window_branding(self.root)
        
        self.assertTrue(result)
        self.assertEqual(self.root.title(), "Test App")
    
    def test_apply_window_branding_with_title_error(self):
        """Test window branding with title setting error."""
        # Mock window.title to raise exception
        with patch.object(self.root, 'title', side_effect=Exception("Title error")):
            result = self.manager.apply_window_branding(self.root)
            
            self.assertFalse(result)
    
    def test_apply_window_branding_with_missing_icon(self):
        """Test window branding with missing icon file."""
        # Use config with non-existent icon
        config = BrandingConfig(
            app_title="Test App",
            icon_path="non_existent.ico"
        )
        manager = BrandingManager(config)
        
        result = manager.apply_window_branding(self.root)
        
        # Should still succeed with title but fail overall due to missing icon
        self.assertFalse(result)
        self.assertEqual(self.root.title(), "Test App")
    
    def test_set_window_icon_success(self):
        """Test successful window icon setting."""
        result = self.manager._set_window_icon(self.root)
        
        # Result depends on whether the system supports iconbitmap
        # We'll just verify it doesn't crash
        self.assertIsInstance(result, bool)
    
    def test_set_window_icon_with_missing_file(self):
        """Test window icon setting with missing file."""
        config = BrandingConfig(icon_path="non_existent.ico")
        manager = BrandingManager(config)
        
        result = manager._set_window_icon(self.root)
        
        self.assertFalse(result)
    
    @patch('tkinter.Tk.iconbitmap')
    def test_set_window_icon_with_iconbitmap_error(self, mock_iconbitmap):
        """Test window icon setting with iconbitmap error."""
        mock_iconbitmap.side_effect = Exception("Icon error")
        
        # Mock PhotoImage as fallback
        with patch('tkinter.PhotoImage') as mock_photo:
            mock_photo_instance = Mock()
            mock_photo.return_value = mock_photo_instance
            
            with patch.object(self.root, 'iconphoto') as mock_iconphoto:
                result = self.manager._set_window_icon(self.root)
                
                # Should try fallback method
                mock_photo.assert_called_once()
                mock_iconphoto.assert_called_once_with(True, mock_photo_instance)
                self.assertTrue(result)
    
    @patch('tkinter.Tk.iconbitmap')
    @patch('tkinter.PhotoImage')
    def test_set_window_icon_with_all_methods_failing(self, mock_photo, mock_iconbitmap):
        """Test window icon setting when all methods fail."""
        mock_iconbitmap.side_effect = Exception("Icon error")
        mock_photo.side_effect = Exception("PhotoImage error")
        
        result = self.manager._set_window_icon(self.root)
        
        self.assertFalse(result)
    
    def test_get_favicon_data_success(self):
        """Test successful favicon data retrieval."""
        favicon_data = self.manager.get_favicon_data()
        
        self.assertIsNotNone(favicon_data)
        self.assertIsInstance(favicon_data, bytes)
        self.assertGreater(len(favicon_data), 0)
    
    def test_get_favicon_data_with_missing_file(self):
        """Test favicon data retrieval with missing file."""
        config = BrandingConfig(icon_path="non_existent.ico")
        manager = BrandingManager(config)
        
        favicon_data = manager.get_favicon_data()
        
        self.assertIsNone(favicon_data)
    
    @patch('builtins.open', side_effect=IOError("File read error"))
    def test_get_favicon_data_with_read_error(self, mock_open):
        """Test favicon data retrieval with file read error."""
        favicon_data = self.manager.get_favicon_data()
        
        self.assertIsNone(favicon_data)
    
    def test_get_favicon_path_success(self):
        """Test successful favicon path retrieval."""
        favicon_path = self.manager.get_favicon_path()
        
        self.assertIsNotNone(favicon_path)
        self.assertIsInstance(favicon_path, str)
        self.assertEqual(favicon_path, str(Path(self.test_icon_path).resolve()))
    
    def test_get_favicon_path_with_missing_file(self):
        """Test favicon path retrieval with missing file."""
        config = BrandingConfig(icon_path="non_existent.ico")
        manager = BrandingManager(config)
        
        favicon_path = manager.get_favicon_path()
        
        self.assertIsNone(favicon_path)


class TestBrandingGlobalFunctions(unittest.TestCase):
    """Test cases for global branding functions."""
    
    def setUp(self):
        """Set up test environment."""
        # Reset global branding manager
        import gui.branding_config
        gui.branding_config._branding_manager = None
        
        # Create test window
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """Clean up test environment."""
        try:
            if self.root and self.root.winfo_exists():
                self.root.destroy()
        except tk.TclError:
            pass
    
    def test_get_branding_manager_singleton(self):
        """Test that get_branding_manager returns singleton instance."""
        manager1 = get_branding_manager()
        manager2 = get_branding_manager()
        
        self.assertIs(manager1, manager2)
        self.assertIsInstance(manager1, BrandingManager)
    
    def test_apply_window_branding_function(self):
        """Test global apply_window_branding function."""
        result = apply_window_branding(self.root)
        
        self.assertIsInstance(result, bool)
        # Should set title to default "OBSmusic"
        self.assertEqual(self.root.title(), "OBSmusic")


class TestBrandingIntegrationScenarios(unittest.TestCase):
    """Test cases for various branding integration scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """Clean up test environment."""
        try:
            if self.root and self.root.winfo_exists():
                self.root.destroy()
        except tk.TclError:
            pass
        
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_branding_with_obsmusic_ico_file(self):
        """Test branding with actual OBSmusic.ico file."""
        # Create a mock OBSmusic.ico file
        obsmusic_ico_path = os.path.join(self.temp_dir, "OBSmusic.ico")
        with open(obsmusic_ico_path, 'wb') as f:
            # Write a minimal valid ICO file header
            f.write(b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00h\x05\x00\x00\x16\x00\x00\x00')
        
        config = BrandingConfig(icon_path=obsmusic_ico_path)
        manager = BrandingManager(config)
        
        result = manager.apply_window_branding(self.root)
        
        # Should succeed with title
        self.assertEqual(self.root.title(), "OBSmusic")
        # Icon setting result depends on system capabilities
        self.assertIsInstance(result, bool)
    
    def test_branding_with_corrupted_icon_file(self):
        """Test branding with corrupted icon file."""
        # Create a corrupted icon file
        corrupted_ico_path = os.path.join(self.temp_dir, "corrupted.ico")
        with open(corrupted_ico_path, 'wb') as f:
            f.write(b'corrupted data')
        
        config = BrandingConfig(icon_path=corrupted_ico_path)
        manager = BrandingManager(config)
        
        # Should handle corrupted file gracefully
        result = manager.apply_window_branding(self.root)
        
        # Title should still be set
        self.assertEqual(self.root.title(), "OBSmusic")
    
    def test_branding_with_empty_icon_file(self):
        """Test branding with empty icon file."""
        # Create an empty icon file
        empty_ico_path = os.path.join(self.temp_dir, "empty.ico")
        with open(empty_ico_path, 'wb') as f:
            pass  # Create empty file
        
        config = BrandingConfig(icon_path=empty_ico_path)
        manager = BrandingManager(config)
        
        # Should handle empty file gracefully
        result = manager.apply_window_branding(self.root)
        
        # Title should still be set
        self.assertEqual(self.root.title(), "OBSmusic")
    
    def test_branding_with_permission_denied_icon(self):
        """Test branding with permission denied on icon file."""
        # Create icon file
        restricted_ico_path = os.path.join(self.temp_dir, "restricted.ico")
        with open(restricted_ico_path, 'wb') as f:
            f.write(b'\x00\x00\x01\x00')
        
        config = BrandingConfig(icon_path=restricted_ico_path)
        manager = BrandingManager(config)
        
        # Mock file operations to raise PermissionError
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            favicon_data = manager.get_favicon_data()
            
            self.assertIsNone(favicon_data)
    
    def test_branding_with_network_path_icon(self):
        """Test branding with network path icon (should handle gracefully)."""
        # Use a network-style path that doesn't exist
        network_path = "//network/share/icon.ico"
        config = BrandingConfig(icon_path=network_path)
        manager = BrandingManager(config)
        
        # Should handle non-existent network path gracefully
        result = manager.apply_window_branding(self.root)
        
        # Title should still be set
        self.assertEqual(self.root.title(), "OBSmusic")
    
    def test_multiple_window_branding(self):
        """Test branding multiple windows."""
        config = BrandingConfig(app_title="Multi Window Test")
        manager = BrandingManager(config)
        
        # Create multiple windows
        window1 = tk.Toplevel(self.root)
        window2 = tk.Toplevel(self.root)
        
        try:
            # Apply branding to both windows
            result1 = manager.apply_window_branding(window1)
            result2 = manager.apply_window_branding(window2)
            
            # Both should have the same title
            self.assertEqual(window1.title(), "Multi Window Test")
            self.assertEqual(window2.title(), "Multi Window Test")
            
        finally:
            window1.destroy()
            window2.destroy()
    
    def test_branding_with_unicode_title(self):
        """Test branding with Unicode characters in title."""
        config = BrandingConfig(app_title="OBSmusic 🎵")
        manager = BrandingManager(config)
        
        result = manager.apply_window_branding(self.root)
        
        # Should handle Unicode characters
        self.assertEqual(self.root.title(), "OBSmusic 🎵")
    
    def test_branding_config_immutability(self):
        """Test that branding config maintains data integrity."""
        config = BrandingConfig()
        original_title = config.app_title
        original_icon_path = config.icon_path
        
        # Create manager
        manager = BrandingManager(config)
        
        # Modify config after manager creation
        config.app_title = "Modified Title"
        
        # Manager should use the modified config
        result = manager.apply_window_branding(self.root)
        self.assertEqual(self.root.title(), "Modified Title")
    
    def test_favicon_data_consistency(self):
        """Test that favicon data is consistent across multiple calls."""
        # Create icon file with specific content
        icon_content = b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00h\x05\x00\x00\x16\x00\x00\x00'
        icon_path = os.path.join(self.temp_dir, "consistent.ico")
        with open(icon_path, 'wb') as f:
            f.write(icon_content)
        
        config = BrandingConfig(icon_path=icon_path)
        manager = BrandingManager(config)
        
        # Get favicon data multiple times
        data1 = manager.get_favicon_data()
        data2 = manager.get_favicon_data()
        data3 = manager.get_favicon_data()
        
        # All should be identical
        self.assertEqual(data1, data2)
        self.assertEqual(data2, data3)
        self.assertEqual(data1, icon_content)
    
    def test_branding_with_relative_icon_path(self):
        """Test branding with relative icon path."""
        # Create icon in temp directory
        icon_name = "relative_icon.ico"
        icon_path = os.path.join(self.temp_dir, icon_name)
        with open(icon_path, 'wb') as f:
            f.write(b'\x00\x00\x01\x00')
        
        # Change to temp directory and use relative path
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            config = BrandingConfig(icon_path=icon_name)
            manager = BrandingManager(config)
            
            # Should resolve relative path correctly
            self.assertTrue(config.icon_exists())
            
            # Should be able to get favicon data
            favicon_data = manager.get_favicon_data()
            self.assertIsNotNone(favicon_data)
            
        finally:
            os.chdir(original_cwd)


if __name__ == '__main__':
    unittest.main()