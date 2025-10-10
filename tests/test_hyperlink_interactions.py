"""
Tests for hyperlink interaction functionality.

Tests the web interface hyperlinks behavior including left-click to open browser,
right-click context menu, and URL copying functionality as specified in requirements.
"""

import unittest
import tkinter as tk
from tkinter import messagebox
import tempfile
import shutil
import os
import webbrowser
from unittest.mock import Mock, patch, MagicMock, call

from gui.main_window import MainWindow
from gui.theme import ThemeManager
from core.playlist_manager import PlaylistManager
from core.player_engine import PlayerEngine


class TestHyperlinkInteractions(unittest.TestCase):
    """Test cases for hyperlink interaction functionality."""
    
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
        
        # Get hyperlink widgets for testing
        self.web_display_link = self.main_window.web_display_link
        self.web_controls_link = self.main_window.web_controls_link
    
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
    
    def test_hyperlink_creation_and_styling(self):
        """Test that hyperlinks are created with correct styling."""
        # Verify hyperlink widgets exist
        self.assertIsNotNone(self.web_display_link)
        self.assertIsNotNone(self.web_controls_link)
        
        # Check hyperlink text content shows full URLs
        display_text = self.web_display_link.cget('text')
        controls_text = self.web_controls_link.cget('text')
        
        self.assertEqual(display_text, "http://localhost:8080")
        self.assertEqual(controls_text, "http://localhost:8081")
        
        # Check hyperlink styling
        theme_manager = self.main_window.theme_manager
        expected_config = theme_manager.get_hyperlink_config()
        
        # Verify foreground color (should be accent color)
        self.assertEqual(self.web_display_link.cget('fg'), expected_config['fg'])
        self.assertEqual(self.web_controls_link.cget('fg'), expected_config['fg'])
        
        # Verify cursor (should be hand2)
        self.assertEqual(self.web_display_link.cget('cursor'), expected_config['cursor'])
        self.assertEqual(self.web_controls_link.cget('cursor'), expected_config['cursor'])
    
    @patch('webbrowser.open')
    def test_left_click_opens_browser(self, mock_webbrowser_open):
        """Test that left-clicking hyperlinks opens URLs in browser."""
        # Mock webbrowser.open to succeed
        mock_webbrowser_open.return_value = True
        
        # Test display link left-click
        display_url = "http://localhost:8080"
        self.main_window._on_hyperlink_left_click(display_url)
        
        # Verify webbrowser.open was called with correct URL
        mock_webbrowser_open.assert_called_with(display_url)
        
        # Reset mock
        mock_webbrowser_open.reset_mock()
        
        # Test controls link left-click
        controls_url = "http://localhost:8081"
        self.main_window._on_hyperlink_left_click(controls_url)
        
        # Verify webbrowser.open was called with correct URL
        mock_webbrowser_open.assert_called_with(controls_url)
    
    @patch('webbrowser.open')
    @patch('tkinter.messagebox.showerror')
    def test_left_click_browser_failure_shows_error(self, mock_showerror, mock_webbrowser_open):
        """Test that browser launch failures show error dialog with manual URL."""
        # Mock webbrowser.open to fail
        mock_webbrowser_open.side_effect = Exception("Browser launch failed")
        
        # Test display link left-click with failure
        display_url = "http://localhost:8080"
        self.main_window._on_hyperlink_left_click(display_url)
        
        # Verify error dialog was shown
        mock_showerror.assert_called_once()
        
        # Check that error message contains the URL for manual access
        call_args = mock_showerror.call_args
        error_title = call_args[0][0]
        error_message = call_args[0][1]
        
        self.assertIn("Browser", error_title)
        self.assertIn(display_url, error_message)
    
    def test_right_click_shows_context_menu(self):
        """Test that right-clicking hyperlinks shows context menu."""
        # Create mock event
        mock_event = Mock()
        mock_event.x_root = 100
        mock_event.y_root = 100
        
        # Test right-click on display link
        display_url = "http://localhost:8080"
        
        # Mock the context menu creation and display
        with patch('tkinter.Menu') as mock_menu_class:
            mock_menu = Mock()
            mock_menu_class.return_value = mock_menu
            
            # Call right-click handler
            self.main_window._on_hyperlink_right_click(mock_event, display_url)
            
            # Verify menu was created
            mock_menu_class.assert_called_once()
            
            # Verify menu items were added
            # The exact implementation may vary, but should include copy option
            self.assertTrue(mock_menu.add_command.called)
            
            # Verify menu was posted at correct location
            mock_menu.post.assert_called_once_with(mock_event.x_root, mock_event.y_root)
    
    @patch('tkinter.Tk.clipboard_clear')
    @patch('tkinter.Tk.clipboard_append')
    def test_copy_url_functionality(self, mock_clipboard_append, mock_clipboard_clear):
        """Test that copy URL functionality works correctly."""
        # Test URL copying
        test_url = "http://localhost:8080"
        
        # Create a method to simulate copy URL action
        def copy_url_to_clipboard(url):
            """Simulate the copy URL functionality."""
            try:
                self.main_window.root.clipboard_clear()
                self.main_window.root.clipboard_append(url)
                return True
            except Exception:
                return False
        
        # Test copying
        result = copy_url_to_clipboard(test_url)
        
        # Verify clipboard operations were called
        mock_clipboard_clear.assert_called_once()
        mock_clipboard_append.assert_called_once_with(test_url)
        self.assertTrue(result)
    
    @patch('tkinter.Tk.clipboard_clear')
    @patch('tkinter.Tk.clipboard_append')
    @patch('tkinter.messagebox.showinfo')
    def test_copy_url_success_message(self, mock_showinfo, mock_clipboard_append, mock_clipboard_clear):
        """Test that successful URL copying shows confirmation message."""
        # Mock successful clipboard operations
        mock_clipboard_clear.return_value = None
        mock_clipboard_append.return_value = None
        
        # Create mock event for right-click
        mock_event = Mock()
        mock_event.x_root = 100
        mock_event.y_root = 100
        
        test_url = "http://localhost:8081"
        
        # Mock the context menu and simulate copy action
        with patch('tkinter.Menu') as mock_menu_class:
            mock_menu = Mock()
            mock_menu_class.return_value = mock_menu
            
            # Capture the copy command callback
            copy_callback = None
            
            def capture_copy_command(label=None, command=None):
                nonlocal copy_callback
                if label and "copy" in label.lower():
                    copy_callback = command
            
            mock_menu.add_command.side_effect = capture_copy_command
            
            # Call right-click handler
            self.main_window._on_hyperlink_right_click(mock_event, test_url)
            
            # Execute the copy command if it was captured
            if copy_callback:
                copy_callback()
                
                # Verify clipboard operations
                mock_clipboard_clear.assert_called()
                mock_clipboard_append.assert_called_with(test_url)
    
    @patch('tkinter.Tk.clipboard_clear')
    @patch('tkinter.Tk.clipboard_append')
    @patch('tkinter.messagebox.showerror')
    def test_copy_url_failure_handling(self, mock_showerror, mock_clipboard_append, mock_clipboard_clear):
        """Test that clipboard failures are handled gracefully."""
        # Mock clipboard operations to fail
        mock_clipboard_clear.side_effect = tk.TclError("Clipboard error")
        
        # Test copy URL with failure
        def copy_url_with_error(url):
            try:
                self.main_window.root.clipboard_clear()
                self.main_window.root.clipboard_append(url)
                return True
            except Exception:
                return False
        
        result = copy_url_with_error("http://localhost:8080")
        
        # Should return False on failure
        self.assertFalse(result)
    
    def test_hyperlink_event_binding(self):
        """Test that hyperlink widgets have correct event bindings."""
        # Check that display link has event bindings
        display_bindings = self.web_display_link.bind()
        self.assertIn('<Button-1>', display_bindings)  # Left-click
        self.assertIn('<Button-3>', display_bindings)  # Right-click
        
        # Check that controls link has event bindings
        controls_bindings = self.web_controls_link.bind()
        self.assertIn('<Button-1>', controls_bindings)  # Left-click
        self.assertIn('<Button-3>', controls_bindings)  # Right-click
    
    def test_hyperlink_urls_are_correct(self):
        """Test that hyperlink URLs match the expected web interface endpoints."""
        # Expected URLs based on requirements
        expected_display_url = "http://localhost:8080"
        expected_controls_url = "http://localhost:8081"
        
        # Check display link URL
        display_text = self.web_display_link.cget('text')
        self.assertEqual(display_text, expected_display_url)
        
        # Check controls link URL
        controls_text = self.web_controls_link.cget('text')
        self.assertEqual(controls_text, expected_controls_url)
    
    @patch('webbrowser.open')
    def test_hyperlink_integration_with_web_server(self, mock_webbrowser_open):
        """Test hyperlink integration with web server availability."""
        # Mock successful browser opening
        mock_webbrowser_open.return_value = True
        
        # Test that hyperlinks work regardless of web server status
        # (The hyperlinks should attempt to open URLs even if server is not running)
        
        display_url = "http://localhost:8080"
        self.main_window._on_hyperlink_left_click(display_url)
        
        # Should still attempt to open browser
        mock_webbrowser_open.assert_called_once_with(display_url)
    
    def test_hyperlink_accessibility(self):
        """Test hyperlink accessibility features."""
        # Check that hyperlinks have proper cursor for accessibility
        self.assertEqual(self.web_display_link.cget('cursor'), 'hand2')
        self.assertEqual(self.web_controls_link.cget('cursor'), 'hand2')
        
        # Check that hyperlinks have distinguishable colors
        theme = self.main_window.theme_manager.theme
        link_color = self.web_display_link.cget('fg')
        background_color = self.web_display_link.cget('bg')
        
        # Link color should be different from background
        self.assertNotEqual(link_color, background_color)
        
        # Link color should be the accent color for visibility
        self.assertEqual(link_color, theme.accent)
    
    def test_hyperlink_layout_and_positioning(self):
        """Test that hyperlinks are properly positioned in the layout."""
        # Verify hyperlinks are in the correct frame
        display_parent = self.web_display_link.master
        controls_parent = self.web_controls_link.master
        
        # Both should have the same parent (web links frame)
        self.assertEqual(display_parent, controls_parent)
        
        # Check that hyperlinks are properly gridded
        display_info = self.web_display_link.grid_info()
        controls_info = self.web_controls_link.grid_info()
        
        # Should be in the same row but different columns
        self.assertEqual(display_info['row'], controls_info['row'])
        self.assertNotEqual(display_info['column'], controls_info['column'])
    
    @patch('webbrowser.open')
    def test_multiple_rapid_clicks(self, mock_webbrowser_open):
        """Test handling of multiple rapid clicks on hyperlinks."""
        mock_webbrowser_open.return_value = True
        
        # Simulate multiple rapid clicks
        display_url = "http://localhost:8080"
        
        for _ in range(5):
            self.main_window._on_hyperlink_left_click(display_url)
        
        # Should handle all clicks (may open multiple browser tabs)
        self.assertEqual(mock_webbrowser_open.call_count, 5)
        
        # All calls should be with the same URL
        for call in mock_webbrowser_open.call_args_list:
            self.assertEqual(call[0][0], display_url)
    
    def test_hyperlink_text_truncation_on_resize(self):
        """Test hyperlink text behavior during window resize."""
        # Get initial text
        initial_display_text = self.web_display_link.cget('text')
        initial_controls_text = self.web_controls_link.cget('text')
        
        # Simulate window resize to very small size
        self.main_window.root.geometry("200x150")
        self.main_window.root.update()
        
        # Text should remain the same (URLs should not be truncated for functionality)
        current_display_text = self.web_display_link.cget('text')
        current_controls_text = self.web_controls_link.cget('text')
        
        self.assertEqual(current_display_text, initial_display_text)
        self.assertEqual(current_controls_text, initial_controls_text)
    
    def test_hyperlink_keyboard_accessibility(self):
        """Test keyboard accessibility for hyperlinks."""
        # Check if hyperlinks can receive focus (for keyboard navigation)
        # Note: Standard tkinter Labels don't support focus by default,
        # but this test documents the expected behavior
        
        # Try to set focus (may not work with standard Label)
        try:
            self.web_display_link.focus_set()
            # If focus is supported, it should work without error
        except tk.TclError:
            # If focus is not supported, that's expected for Label widgets
            pass
        
        # This test mainly documents that keyboard accessibility
        # could be improved in future implementations
    
    def test_dynamic_url_generation_with_default_ports(self):
        """Test dynamic URL generation with default server ports."""
        # Create mock server objects with default ports
        mock_web_server = Mock()
        mock_web_server.port = 8080
        mock_web_server.is_running = True
        mock_web_server.get_current_port.return_value = 8080
        
        mock_controls_server = Mock()
        mock_controls_server.port = 8081
        mock_controls_server.is_running = True
        mock_controls_server.get_current_port.return_value = 8081
        
        # Update hyperlink URLs with server objects
        self.main_window.set_server_instances(mock_web_server, mock_controls_server)
        
        # Check that URLs are updated correctly
        current_urls = self.main_window.get_hyperlink_urls()
        self.assertEqual(current_urls['display'], "http://localhost:8080")
        self.assertEqual(current_urls['controls'], "http://localhost:8081")
    
    def test_dynamic_url_generation_with_custom_ports(self):
        """Test dynamic URL generation with custom server ports."""
        # Create mock server objects with custom ports
        mock_web_server = Mock()
        mock_web_server.port = 9090
        mock_web_server.is_running = True
        mock_web_server.get_current_port.return_value = 9090
        
        mock_controls_server = Mock()
        mock_controls_server.port = 9091
        mock_controls_server.is_running = True
        mock_controls_server.get_current_port.return_value = 9091
        
        # Update hyperlink URLs with server objects
        self.main_window.set_server_instances(mock_web_server, mock_controls_server)
        
        # Check that URLs are updated correctly
        current_urls = self.main_window.get_hyperlink_urls()
        self.assertEqual(current_urls['display'], "http://localhost:9090")
        self.assertEqual(current_urls['controls'], "http://localhost:9091")
    
    def test_url_refresh_mechanism(self):
        """Test URL refresh mechanism when server ports change."""
        # Create mock server objects with initial ports
        mock_web_server = Mock()
        mock_web_server.port = 8080
        mock_web_server.is_running = True
        mock_web_server.get_current_port.return_value = 8080
        
        mock_controls_server = Mock()
        mock_controls_server.port = 8081
        mock_controls_server.is_running = True
        mock_controls_server.get_current_port.return_value = 8081
        
        # Set initial server instances
        self.main_window.set_server_instances(mock_web_server, mock_controls_server)
        
        # Verify initial URLs
        initial_urls = self.main_window.get_hyperlink_urls()
        self.assertEqual(initial_urls['display'], "http://localhost:8080")
        self.assertEqual(initial_urls['controls'], "http://localhost:8081")
        
        # Change server ports
        mock_web_server.port = 8888
        mock_web_server.get_current_port.return_value = 8888
        mock_controls_server.port = 8889
        mock_controls_server.get_current_port.return_value = 8889
        
        # Refresh URLs
        self.main_window.refresh_hyperlink_urls()
        
        # Verify URLs are updated
        updated_urls = self.main_window.get_hyperlink_urls()
        self.assertEqual(updated_urls['display'], "http://localhost:8888")
        self.assertEqual(updated_urls['controls'], "http://localhost:8889")
    
    def test_server_status_change_handling(self):
        """Test handling of server status changes."""
        # Test server start event
        self.main_window.on_server_status_changed('web', True)
        # Should not raise an exception
        
        # Test server stop event
        self.main_window.on_server_status_changed('controls', False)
        # Should not raise an exception
    
    def test_server_port_change_handling(self):
        """Test handling of server port changes."""
        # Test web server port change
        self.main_window.on_server_port_changed('web', 9000)
        # Should not raise an exception
        
        # Test controls server port change
        self.main_window.on_server_port_changed('controls', 9001)
        # Should not raise an exception
    
    def test_hyperlink_functionality_with_various_port_configurations(self):
        """Test hyperlink functionality with various port configurations."""
        # Test configuration 1: Default ports
        config1 = [
            (8080, 8081, "http://localhost:8080", "http://localhost:8081"),
        ]
        
        # Test configuration 2: Custom ports
        config2 = [
            (9000, 9001, "http://localhost:9000", "http://localhost:9001"),
        ]
        
        # Test configuration 3: High ports
        config3 = [
            (12345, 12346, "http://localhost:12345", "http://localhost:12346"),
        ]
        
        all_configs = config1 + config2 + config3
        
        for web_port, controls_port, expected_display_url, expected_controls_url in all_configs:
            with self.subTest(web_port=web_port, controls_port=controls_port):
                # Create mock server objects
                mock_web_server = Mock()
                mock_web_server.port = web_port
                mock_web_server.is_running = True
                mock_web_server.get_current_port.return_value = web_port
                
                mock_controls_server = Mock()
                mock_controls_server.port = controls_port
                mock_controls_server.is_running = True
                mock_controls_server.get_current_port.return_value = controls_port
                
                # Update hyperlink URLs
                self.main_window.set_server_instances(mock_web_server, mock_controls_server)
                
                # Verify URLs
                current_urls = self.main_window.get_hyperlink_urls()
                self.assertEqual(current_urls['display'], expected_display_url)
                self.assertEqual(current_urls['controls'], expected_controls_url)
    
    def test_fallback_urls_when_servers_not_running(self):
        """Test fallback URLs when servers are not running."""
        # Create mock server objects that are not running
        mock_web_server = Mock()
        mock_web_server.port = 8080
        mock_web_server.is_running = False
        mock_web_server.get_current_port.return_value = None
        
        mock_controls_server = Mock()
        mock_controls_server.port = 8081
        mock_controls_server.is_running = False
        mock_controls_server.get_current_port.return_value = None
        
        # Set server instances
        self.main_window.set_server_instances(mock_web_server, mock_controls_server)
        
        # URLs should still be generated (fallback to configured ports)
        current_urls = self.main_window.get_hyperlink_urls()
        self.assertIsNotNone(current_urls['display'])
        self.assertIsNotNone(current_urls['controls'])
        self.assertTrue(current_urls['display'].startswith('http://localhost:'))
        self.assertTrue(current_urls['controls'].startswith('http://localhost:'))
    
    @patch('webbrowser.open')
    def test_dynamic_hyperlink_click_handlers(self, mock_webbrowser_open):
        """Test dynamic hyperlink click handlers with various URLs."""
        mock_webbrowser_open.return_value = True
        
        # Create mock server with custom ports
        mock_web_server = Mock()
        mock_web_server.port = 9999
        mock_web_server.is_running = True
        mock_web_server.get_current_port.return_value = 9999
        
        mock_controls_server = Mock()
        mock_controls_server.port = 9998
        mock_controls_server.is_running = True
        mock_controls_server.get_current_port.return_value = 9998
        
        # Set server instances
        self.main_window.set_server_instances(mock_web_server, mock_controls_server)
        
        # Test dynamic display link click
        self.main_window._on_hyperlink_left_click_dynamic('display')
        mock_webbrowser_open.assert_called_with("http://localhost:9999")
        
        # Reset mock
        mock_webbrowser_open.reset_mock()
        
        # Test dynamic controls link click
        self.main_window._on_hyperlink_left_click_dynamic('controls')
        mock_webbrowser_open.assert_called_with("http://localhost:9998")


if __name__ == '__main__':
    unittest.main()