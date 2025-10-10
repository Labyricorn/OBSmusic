"""
Tests for comprehensive error handling in new features.

Tests error handling for missing icons, server communication failures,
and various edge cases in the dynamic URL and branding systems.
"""

import unittest
import tempfile
import shutil
import os
import tkinter as tk
import socket
from unittest.mock import Mock, patch, MagicMock, mock_open, PropertyMock
from pathlib import Path

from gui.hyperlink_config import HyperlinkConfig, DynamicHyperlinkManager
from gui.branding_config import BrandingConfig, BrandingManager
from gui.main_window import MainWindow
from core.playlist_manager import PlaylistManager
from core.player_engine import PlayerEngine


class TestIconErrorHandling(unittest.TestCase):
    """Test cases for icon-related error handling."""
    
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
    
    def test_missing_icon_file_handling(self):
        """Test handling of missing icon file."""
        # Create config with non-existent icon
        config = BrandingConfig(icon_path="non_existent_icon.ico")
        manager = BrandingManager(config)
        
        # Should handle missing file gracefully
        self.assertFalse(config.icon_exists())
        
        # Window branding should still work (title only)
        result = manager.apply_window_branding(self.root)
        self.assertFalse(result)  # False because icon failed
        self.assertEqual(self.root.title(), "OBSmusic")
        
        # Favicon data should return None
        favicon_data = manager.get_favicon_data()
        self.assertIsNone(favicon_data)
        
        # Favicon path should return None
        favicon_path = manager.get_favicon_path()
        self.assertIsNone(favicon_path)
    
    def test_corrupted_icon_file_handling(self):
        """Test handling of corrupted icon file."""
        # Create corrupted icon file
        corrupted_icon_path = os.path.join(self.temp_dir, "corrupted.ico")
        with open(corrupted_icon_path, 'wb') as f:
            f.write(b'not a valid icon file')
        
        config = BrandingConfig(icon_path=corrupted_icon_path)
        manager = BrandingManager(config)
        
        # File exists but is corrupted
        self.assertTrue(config.icon_exists())
        
        # Should handle corrupted file gracefully
        result = manager.apply_window_branding(self.root)
        # Title should still be set
        self.assertEqual(self.root.title(), "OBSmusic")
        
        # Favicon data should still be returned (even if corrupted)
        favicon_data = manager.get_favicon_data()
        self.assertIsNotNone(favicon_data)
        self.assertEqual(favicon_data, b'not a valid icon file')
    
    def test_icon_file_permission_denied(self):
        """Test handling of icon file permission errors."""
        # Create icon file
        icon_path = os.path.join(self.temp_dir, "restricted.ico")
        with open(icon_path, 'wb') as f:
            f.write(b'\x00\x00\x01\x00')
        
        config = BrandingConfig(icon_path=icon_path)
        manager = BrandingManager(config)
        
        # Mock file operations to raise PermissionError
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            # Should handle permission error gracefully
            favicon_data = manager.get_favicon_data()
            self.assertIsNone(favicon_data)
    
    def test_icon_file_io_error(self):
        """Test handling of icon file I/O errors."""
        # Create icon file
        icon_path = os.path.join(self.temp_dir, "io_error.ico")
        with open(icon_path, 'wb') as f:
            f.write(b'\x00\x00\x01\x00')
        
        config = BrandingConfig(icon_path=icon_path)
        manager = BrandingManager(config)
        
        # Mock file operations to raise IOError
        with patch('builtins.open', side_effect=IOError("I/O error")):
            # Should handle I/O error gracefully
            favicon_data = manager.get_favicon_data()
            self.assertIsNone(favicon_data)
    
    def test_icon_path_resolution_error(self):
        """Test handling of icon path resolution errors."""
        # Use invalid path characters (platform-specific)
        if os.name == 'nt':  # Windows
            invalid_path = "C:\\invalid<>path\\icon.ico"
        else:  # Unix-like
            invalid_path = "/invalid\x00path/icon.ico"
        
        config = BrandingConfig(icon_path=invalid_path)
        
        # Should handle path resolution gracefully
        try:
            icon_path = config.get_icon_path()
            # If no exception, check that it's a Path object
            self.assertIsInstance(icon_path, Path)
        except (OSError, ValueError):
            # Some systems may raise exceptions for invalid paths
            pass
    
    @patch('tkinter.Tk.iconbitmap')
    def test_window_icon_setting_error(self, mock_iconbitmap):
        """Test handling of window icon setting errors."""
        # Create valid icon file
        icon_path = os.path.join(self.temp_dir, "valid.ico")
        with open(icon_path, 'wb') as f:
            f.write(b'\x00\x00\x01\x00')
        
        config = BrandingConfig(icon_path=icon_path)
        manager = BrandingManager(config)
        
        # Mock iconbitmap to raise exception
        mock_iconbitmap.side_effect = tk.TclError("Icon error")
        
        # Should handle icon setting error gracefully
        result = manager._set_window_icon(self.root)
        self.assertFalse(result)
    
    @patch('tkinter.Tk.iconbitmap')
    @patch('tkinter.PhotoImage')
    def test_fallback_icon_method_error(self, mock_photo, mock_iconbitmap):
        """Test handling of fallback icon method errors."""
        # Create valid icon file
        icon_path = os.path.join(self.temp_dir, "valid.ico")
        with open(icon_path, 'wb') as f:
            f.write(b'\x00\x00\x01\x00')
        
        config = BrandingConfig(icon_path=icon_path)
        manager = BrandingManager(config)
        
        # Mock both methods to fail
        mock_iconbitmap.side_effect = tk.TclError("Icon error")
        mock_photo.side_effect = tk.TclError("PhotoImage error")
        
        # Should handle all icon methods failing
        result = manager._set_window_icon(self.root)
        self.assertFalse(result)
    
    def test_window_title_setting_error(self):
        """Test handling of window title setting errors."""
        config = BrandingConfig(app_title="Test Title")
        manager = BrandingManager(config)
        
        # Mock window.title to raise exception
        with patch.object(self.root, 'title', side_effect=tk.TclError("Title error")):
            result = manager.apply_window_branding(self.root)
            self.assertFalse(result)


class TestServerCommunicationErrorHandling(unittest.TestCase):
    """Test cases for server communication error handling."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = HyperlinkConfig()
        self.manager = DynamicHyperlinkManager(self.config)
    
    def test_server_port_attribute_error(self):
        """Test handling of server port attribute errors."""
        # Create mock server without port attribute
        mock_web_server = Mock(spec=[])  # No attributes
        mock_controls_server = Mock(spec=[])
        
        # Should handle missing port attribute gracefully
        web_port, controls_port = self.manager.detect_server_ports(
            mock_web_server, mock_controls_server
        )
        
        # Should fall back to defaults
        self.assertEqual(web_port, 8080)
        self.assertEqual(controls_port, 8081)
    
    def test_server_port_access_exception(self):
        """Test handling of server port access exceptions."""
        # Create mock servers that raise exceptions when accessing port
        mock_web_server = Mock()
        type(mock_web_server).port = PropertyMock(side_effect=Exception("Port access error"))
        
        mock_controls_server = Mock()
        type(mock_controls_server).port = PropertyMock(side_effect=Exception("Port access error"))
        
        # Should handle port access exceptions gracefully
        web_port, controls_port = self.manager.detect_server_ports(
            mock_web_server, mock_controls_server
        )
        
        # Should fall back to defaults
        self.assertEqual(web_port, 8080)
        self.assertEqual(controls_port, 8081)
    
    def test_server_is_running_attribute_error(self):
        """Test handling of server is_running attribute errors."""
        # Create mock server with port but no is_running attribute
        mock_web_server = Mock()
        mock_web_server.port = 9000
        # Don't set is_running attribute
        
        mock_controls_server = Mock()
        mock_controls_server.port = 9001
        # Don't set is_running attribute
        
        # Should handle missing is_running attribute gracefully
        web_port, controls_port = self.manager.detect_server_ports(
            mock_web_server, mock_controls_server
        )
        
        # Should use the port values (assuming running)
        self.assertEqual(web_port, 9000)
        self.assertEqual(controls_port, 9001)
    
    def test_server_get_current_port_exception(self):
        """Test handling of get_current_port method exceptions."""
        # Create mock servers with get_current_port that raises exception but no port attribute
        mock_web_server = Mock(spec=['get_current_port'])
        mock_web_server.get_current_port.side_effect = Exception("Port query error")
        
        mock_controls_server = Mock(spec=['get_current_port'])
        mock_controls_server.get_current_port.side_effect = Exception("Port query error")
        
        # Should handle get_current_port exceptions gracefully
        web_port, controls_port = self.manager.detect_server_ports(
            mock_web_server, mock_controls_server
        )
        
        # Should fall back to defaults
        self.assertEqual(web_port, 8080)
        self.assertEqual(controls_port, 8081)
    
    def test_server_none_handling(self):
        """Test handling of None server objects."""
        # Should handle None servers gracefully
        web_port, controls_port = self.manager.detect_server_ports(None, None)
        
        # Should use defaults
        self.assertEqual(web_port, 8080)
        self.assertEqual(controls_port, 8081)
    
    def test_mixed_server_error_scenarios(self):
        """Test handling of mixed server error scenarios."""
        # First establish a baseline with different ports to set last known ports
        mock_baseline_web = Mock()
        mock_baseline_web.port = 9000
        mock_baseline_web.is_running = True
        
        mock_baseline_controls = Mock()
        mock_baseline_controls.port = 9001
        mock_baseline_controls.is_running = True
        
        # Set baseline to establish last known ports
        self.manager.detect_server_ports(mock_baseline_web, mock_baseline_controls)
        
        # Now create servers where one works and one fails
        mock_web_server = Mock()
        mock_web_server.port = 9000
        mock_web_server.is_running = True
        
        mock_controls_server = Mock()
        type(mock_controls_server).port = PropertyMock(side_effect=Exception("Controls error"))
        
        # Should handle mixed scenarios gracefully
        web_port, controls_port = self.manager.detect_server_ports(
            mock_web_server, mock_controls_server
        )
        
        # Web server should work, controls should fall back to last known
        self.assertEqual(web_port, 9000)
        self.assertEqual(controls_port, 9001)  # Last known port
    
    def test_update_from_servers_exception_handling(self):
        """Test update_from_servers exception handling."""
        # Create servers that cause exceptions during update
        mock_web_server = Mock()
        type(mock_web_server).port = PropertyMock(side_effect=Exception("Update error"))
        
        mock_controls_server = Mock()
        type(mock_controls_server).port = PropertyMock(side_effect=Exception("Update error"))
        
        # Should handle update exceptions gracefully
        result = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        
        # Should return False due to error (ports remain unchanged from defaults)
        self.assertFalse(result)
        
        # URLs should remain at defaults
        urls = self.manager.get_current_urls()
        self.assertEqual(urls['display'], "http://localhost:8080")
        self.assertEqual(urls['controls'], "http://localhost:8081")
    
    def test_network_socket_error_handling(self):
        """Test handling of network socket errors."""
        # Mock socket operations to raise network errors
        with patch('socket.socket') as mock_socket:
            mock_socket_instance = Mock()
            mock_socket_instance.bind.side_effect = socket.error("Network error")
            mock_socket.return_value.__enter__.return_value = mock_socket_instance
            
            # Should handle socket errors gracefully
            available = self.manager.is_port_available(8080)
            self.assertFalse(available)
    
    def test_port_availability_os_error(self):
        """Test handling of OS errors during port availability check."""
        with patch('socket.socket') as mock_socket:
            mock_socket_instance = Mock()
            mock_socket_instance.bind.side_effect = OSError("OS error")
            mock_socket.return_value.__enter__.return_value = mock_socket_instance
            
            # Should handle OS errors gracefully
            available = self.manager.is_port_available(8080)
            self.assertFalse(available)
    
    def test_find_available_ports_all_ports_busy(self):
        """Test find_available_ports when all ports are busy."""
        # Mock is_port_available to always return False
        with patch.object(self.manager, 'is_port_available', return_value=False):
            web_port, controls_port = self.manager.find_available_ports(8080, 8081)
            
            # Should still return some ports (even if not actually available)
            self.assertIsInstance(web_port, int)
            self.assertIsInstance(controls_port, int)
            self.assertNotEqual(web_port, controls_port)


class TestHyperlinkWidgetErrorHandling(unittest.TestCase):
    """Test cases for hyperlink widget error handling."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = HyperlinkConfig()
        self.manager = DynamicHyperlinkManager(self.config)
    
    def test_refresh_hyperlink_display_with_none_widgets(self):
        """Test refresh_hyperlink_display with None widgets."""
        hyperlink_widgets = {
            'display': None,
            'controls': None
        }
        
        # Should handle None widgets gracefully
        self.manager.refresh_hyperlink_display(hyperlink_widgets)
        # Should not raise an exception
    
    def test_refresh_hyperlink_display_with_missing_keys(self):
        """Test refresh_hyperlink_display with missing dictionary keys."""
        # Empty dictionary
        self.manager.refresh_hyperlink_display({})
        
        # Dictionary with only one key
        mock_widget = Mock()
        self.manager.refresh_hyperlink_display({'display': mock_widget})
        
        # Should not raise exceptions
    
    def test_refresh_hyperlink_display_with_widget_configure_error(self):
        """Test refresh_hyperlink_display with widget configure errors."""
        # Create mock widgets that raise exceptions on configure
        mock_display_widget = Mock()
        mock_display_widget.configure.side_effect = tk.TclError("Configure error")
        
        mock_controls_widget = Mock()
        mock_controls_widget.configure.side_effect = tk.TclError("Configure error")
        
        hyperlink_widgets = {
            'display': mock_display_widget,
            'controls': mock_controls_widget
        }
        
        # Should handle configure errors gracefully
        self.manager.refresh_hyperlink_display(hyperlink_widgets)
        # Should not raise an exception
    
    def test_refresh_hyperlink_display_with_widget_attribute_error(self):
        """Test refresh_hyperlink_display with widget attribute errors."""
        # Create mock widgets without configure method
        mock_display_widget = Mock(spec=[])  # No methods
        mock_controls_widget = Mock(spec=[])
        
        hyperlink_widgets = {
            'display': mock_display_widget,
            'controls': mock_controls_widget
        }
        
        # Should handle missing configure method gracefully
        self.manager.refresh_hyperlink_display(hyperlink_widgets)
        # Should not raise an exception
    
    def test_handle_server_unavailable_basic_functionality(self):
        """Test basic handle_server_unavailable functionality."""
        # Test that the method returns proper fallback URLs
        fallback_urls = self.manager.handle_server_unavailable()
        
        # Should return URLs based on current config
        expected_urls = {
            'display': "http://localhost:8080",
            'controls': "http://localhost:8081"
        }
        
        self.assertEqual(fallback_urls, expected_urls)


class TestIntegratedErrorHandling(unittest.TestCase):
    """Test cases for integrated error handling across components."""
    
    def setUp(self):
        """Set up test environment."""
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
    
    def tearDown(self):
        """Clean up test environment."""
        self.pygame_patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_main_window_with_missing_icon_and_server_errors(self):
        """Test main window with both missing icon and server errors."""
        # Create main window (which should handle missing icon gracefully)
        main_window = MainWindow(self.playlist_manager, self.player_engine)
        main_window.root.withdraw()
        
        try:
            # Create mock servers that raise exceptions
            mock_web_server = Mock()
            mock_web_server.port = Mock(side_effect=Exception("Server error"))
            
            mock_controls_server = Mock()
            mock_controls_server.port = Mock(side_effect=Exception("Server error"))
            
            # Should handle both icon and server errors gracefully
            if hasattr(main_window, 'set_server_instances'):
                main_window.set_server_instances(mock_web_server, mock_controls_server)
            
            # Window should still be functional
            self.assertEqual(main_window.root.title(), "OBSmusic")
            
        finally:
            try:
                if main_window.root and main_window.root.winfo_exists():
                    main_window.root.destroy()
            except tk.TclError:
                pass
    
    def test_cascading_error_recovery(self):
        """Test recovery from cascading errors."""
        # Create components with various error conditions
        config = HyperlinkConfig()
        manager = DynamicHyperlinkManager(config)
        
        # First error: server communication failure
        mock_web_server = Mock()
        type(mock_web_server).port = PropertyMock(side_effect=Exception("First error"))
        
        result1 = manager.update_from_servers(mock_web_server, None)
        self.assertFalse(result1)
        
        # Second error: widget update failure
        mock_widget = Mock()
        mock_widget.configure.side_effect = tk.TclError("Widget error")
        
        manager.refresh_hyperlink_display({'display': mock_widget})
        # Should not raise exception
        
        # Recovery: working server
        working_server = Mock()
        working_server.port = 9000
        working_server.is_running = True
        
        result2 = manager.update_from_servers(working_server, None)
        self.assertTrue(result2)
        
        # Should recover and work normally
        urls = manager.get_current_urls()
        self.assertEqual(urls['display'], "http://localhost:9000")
    
    def test_error_logging_and_debugging(self):
        """Test that errors are properly logged for debugging."""
        with patch('gui.hyperlink_config.logger') as mock_logger:
            # Create manager
            manager = DynamicHyperlinkManager()
            
            # Cause an error
            mock_server = Mock()
            type(mock_server).port = PropertyMock(side_effect=Exception("Test error"))
            
            manager.update_from_servers(mock_server, None)
            
            # Should log the error
            mock_logger.warning.assert_called()
    
    def test_graceful_degradation_scenarios(self):
        """Test graceful degradation in various error scenarios."""
        scenarios = [
            # Scenario 1: Missing icon, working servers
            {
                'icon_path': 'missing.ico',
                'web_server_port': 8080,
                'controls_server_port': 8081,
                'expected_title': 'OBSmusic',
                'expected_urls': True
            },
            # Scenario 2: Working icon, failing servers
            {
                'icon_path': None,  # Use default
                'web_server_error': True,
                'expected_title': 'OBSmusic',
                'expected_fallback_urls': True
            },
            # Scenario 3: Both icon and servers failing
            {
                'icon_path': 'missing.ico',
                'web_server_error': True,
                'controls_server_error': True,
                'expected_title': 'OBSmusic',
                'expected_fallback_urls': True
            }
        ]
        
        for i, scenario in enumerate(scenarios):
            with self.subTest(scenario=i):
                # Create branding config
                if scenario.get('icon_path'):
                    branding_config = BrandingConfig(icon_path=scenario['icon_path'])
                else:
                    branding_config = BrandingConfig()
                
                branding_manager = BrandingManager(branding_config)
                
                # Create hyperlink manager
                hyperlink_manager = DynamicHyperlinkManager()
                
                # Test branding
                root = tk.Tk()
                root.withdraw()
                
                try:
                    branding_manager.apply_window_branding(root)
                    
                    if 'expected_title' in scenario:
                        self.assertEqual(root.title(), scenario['expected_title'])
                    
                    # Test hyperlink functionality
                    if scenario.get('web_server_error'):
                        mock_web_server = Mock()
                        mock_web_server.port = Mock(side_effect=Exception("Server error"))
                    else:
                        mock_web_server = Mock()
                        mock_web_server.port = scenario.get('web_server_port', 8080)
                        mock_web_server.is_running = True
                    
                    if scenario.get('controls_server_error'):
                        mock_controls_server = Mock()
                        mock_controls_server.port = Mock(side_effect=Exception("Server error"))
                    else:
                        mock_controls_server = Mock()
                        mock_controls_server.port = scenario.get('controls_server_port', 8081)
                        mock_controls_server.is_running = True
                    
                    hyperlink_manager.update_from_servers(mock_web_server, mock_controls_server)
                    
                    if scenario.get('expected_urls') or scenario.get('expected_fallback_urls'):
                        urls = hyperlink_manager.get_current_urls()
                        self.assertIsNotNone(urls['display'])
                        self.assertIsNotNone(urls['controls'])
                        self.assertTrue(urls['display'].startswith('http://'))
                        self.assertTrue(urls['controls'].startswith('http://'))
                
                finally:
                    try:
                        if root and root.winfo_exists():
                            root.destroy()
                    except tk.TclError:
                        pass


if __name__ == '__main__':
    unittest.main()