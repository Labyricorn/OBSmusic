"""
Tests for hyperlink URL updates when server ports change.

Tests the dynamic hyperlink URL update functionality including server port
change detection, URL refresh mechanisms, and integration with GUI components.
"""

import unittest
import tkinter as tk
import tempfile
import shutil
import os
from unittest.mock import Mock, patch, MagicMock, call, PropertyMock

from gui.hyperlink_config import HyperlinkConfig, DynamicHyperlinkManager
from gui.main_window import MainWindow
from core.playlist_manager import PlaylistManager
from core.player_engine import PlayerEngine


class TestHyperlinkUrlUpdates(unittest.TestCase):
    """Test cases for hyperlink URL updates functionality."""
    
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
        
        # Create hyperlink configuration and manager
        self.config = HyperlinkConfig()
        self.manager = DynamicHyperlinkManager(self.config)
        
        # Create main window
        self.main_window = MainWindow(self.playlist_manager, self.player_engine)
        self.main_window.root.withdraw()  # Hide window during tests
    
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
    
    def test_url_update_when_web_server_port_changes(self):
        """Test URL update when web server port changes."""
        # Create mock servers with initial ports
        mock_web_server = Mock()
        mock_web_server.port = 8080
        mock_web_server.is_running = True
        
        mock_controls_server = Mock()
        mock_controls_server.port = 8081
        mock_controls_server.is_running = True
        
        # Initial update
        changed = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        self.assertFalse(changed)  # No change from defaults
        
        # Change web server port
        mock_web_server.port = 9000
        
        # Update again
        changed = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        self.assertTrue(changed)
        
        # Verify URLs are updated
        urls = self.manager.get_current_urls()
        self.assertEqual(urls['display'], "http://localhost:9000")
        self.assertEqual(urls['controls'], "http://localhost:8081")
    
    def test_url_update_when_controls_server_port_changes(self):
        """Test URL update when controls server port changes."""
        # Create mock servers with initial ports
        mock_web_server = Mock()
        mock_web_server.port = 8080
        mock_web_server.is_running = True
        
        mock_controls_server = Mock()
        mock_controls_server.port = 8081
        mock_controls_server.is_running = True
        
        # Initial update
        self.manager.update_from_servers(mock_web_server, mock_controls_server)
        
        # Change controls server port
        mock_controls_server.port = 9001
        
        # Update again
        changed = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        self.assertTrue(changed)
        
        # Verify URLs are updated
        urls = self.manager.get_current_urls()
        self.assertEqual(urls['display'], "http://localhost:8080")
        self.assertEqual(urls['controls'], "http://localhost:9001")
    
    def test_url_update_when_both_server_ports_change(self):
        """Test URL update when both server ports change."""
        # Create mock servers with initial ports
        mock_web_server = Mock()
        mock_web_server.port = 8080
        mock_web_server.is_running = True
        
        mock_controls_server = Mock()
        mock_controls_server.port = 8081
        mock_controls_server.is_running = True
        
        # Initial update
        self.manager.update_from_servers(mock_web_server, mock_controls_server)
        
        # Change both server ports
        mock_web_server.port = 9000
        mock_controls_server.port = 9001
        
        # Update again
        changed = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        self.assertTrue(changed)
        
        # Verify URLs are updated
        urls = self.manager.get_current_urls()
        self.assertEqual(urls['display'], "http://localhost:9000")
        self.assertEqual(urls['controls'], "http://localhost:9001")
    
    def test_no_url_update_when_ports_unchanged(self):
        """Test no URL update when ports remain unchanged."""
        # Create mock servers with same ports
        mock_web_server = Mock()
        mock_web_server.port = 8080
        mock_web_server.is_running = True
        
        mock_controls_server = Mock()
        mock_controls_server.port = 8081
        mock_controls_server.is_running = True
        
        # Multiple updates with same ports
        changed1 = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        changed2 = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        changed3 = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        
        # Only first update should report no change (since they match defaults)
        self.assertFalse(changed1)
        self.assertFalse(changed2)
        self.assertFalse(changed3)
    
    def test_hyperlink_widget_update_on_port_change(self):
        """Test that hyperlink widgets are updated when ports change."""
        # Create mock hyperlink widgets
        mock_display_widget = Mock()
        mock_controls_widget = Mock()
        
        hyperlink_widgets = {
            'display': mock_display_widget,
            'controls': mock_controls_widget
        }
        
        # Initial refresh
        self.manager.refresh_hyperlink_display(hyperlink_widgets)
        
        # Verify initial URLs
        mock_display_widget.configure.assert_called_with(text="http://localhost:8080")
        mock_controls_widget.configure.assert_called_with(text="http://localhost:8081")
        
        # Reset mocks
        mock_display_widget.reset_mock()
        mock_controls_widget.reset_mock()
        
        # Change ports
        self.config.update_ports(9000, 9001)
        
        # Refresh again
        self.manager.refresh_hyperlink_display(hyperlink_widgets)
        
        # Verify updated URLs
        mock_display_widget.configure.assert_called_with(text="http://localhost:9000")
        mock_controls_widget.configure.assert_called_with(text="http://localhost:9001")
    
    def test_url_update_with_server_restart_scenario(self):
        """Test URL update when servers restart with different ports."""
        # Create mock servers initially running
        mock_web_server = Mock()
        mock_web_server.port = 8080
        mock_web_server.is_running = True
        
        mock_controls_server = Mock()
        mock_controls_server.port = 8081
        mock_controls_server.is_running = True
        
        # Initial update
        self.manager.update_from_servers(mock_web_server, mock_controls_server)
        
        # Simulate server stop
        mock_web_server.is_running = False
        mock_controls_server.is_running = False
        
        # Update (should use configured defaults)
        changed = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        self.assertFalse(changed)  # No change since defaults match
        
        # Simulate server restart with new ports
        mock_web_server.port = 8888
        mock_web_server.is_running = True
        mock_controls_server.port = 8889
        mock_controls_server.is_running = True
        
        # Update again
        changed = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        self.assertTrue(changed)
        
        # Verify new URLs
        urls = self.manager.get_current_urls()
        self.assertEqual(urls['display'], "http://localhost:8888")
        self.assertEqual(urls['controls'], "http://localhost:8889")
    
    def test_url_update_with_get_current_port_method(self):
        """Test URL update using get_current_port method."""
        # Create mock servers with get_current_port method but no port attribute
        mock_web_server = Mock(spec=['get_current_port'])
        mock_web_server.get_current_port.return_value = 9500
        
        mock_controls_server = Mock(spec=['get_current_port'])
        mock_controls_server.get_current_port.return_value = 9501
        
        # Update from servers
        changed = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        self.assertTrue(changed)
        
        # Verify URLs
        urls = self.manager.get_current_urls()
        self.assertEqual(urls['display'], "http://localhost:9500")
        self.assertEqual(urls['controls'], "http://localhost:9501")
        
        # Change ports via get_current_port
        mock_web_server.get_current_port.return_value = 9600
        mock_controls_server.get_current_port.return_value = 9601
        
        # Update again
        changed = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        self.assertTrue(changed)
        
        # Verify updated URLs
        urls = self.manager.get_current_urls()
        self.assertEqual(urls['display'], "http://localhost:9600")
        self.assertEqual(urls['controls'], "http://localhost:9601")
    
    def test_url_update_with_mixed_server_states(self):
        """Test URL update with mixed server running states."""
        # Create servers with mixed states
        mock_web_server = Mock()
        mock_web_server.port = 9000
        mock_web_server.is_running = True  # Running
        
        mock_controls_server = Mock()
        mock_controls_server.port = 9001
        mock_controls_server.is_running = False  # Not running
        
        # Update from servers
        changed = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        self.assertTrue(changed)
        
        # Web server port should be used, controls should use default
        urls = self.manager.get_current_urls()
        self.assertEqual(urls['display'], "http://localhost:9000")
        self.assertEqual(urls['controls'], "http://localhost:8081")  # Default
    
    def test_url_update_frequency_and_performance(self):
        """Test URL update frequency and performance."""
        # Create mock servers
        mock_web_server = Mock()
        mock_web_server.port = 8080
        mock_web_server.is_running = True
        
        mock_controls_server = Mock()
        mock_controls_server.port = 8081
        mock_controls_server.is_running = True
        
        # Perform many updates with same ports
        for _ in range(100):
            changed = self.manager.update_from_servers(mock_web_server, mock_controls_server)
            self.assertFalse(changed)
        
        # Change port once
        mock_web_server.port = 9000
        changed = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        self.assertTrue(changed)
        
        # Perform many more updates with same ports
        for _ in range(100):
            changed = self.manager.update_from_servers(mock_web_server, mock_controls_server)
            self.assertFalse(changed)
    
    def test_url_update_with_invalid_port_numbers(self):
        """Test URL update with invalid port numbers."""
        # Create mock servers with invalid ports
        mock_web_server = Mock()
        mock_web_server.port = -1  # Invalid port
        mock_web_server.is_running = True
        
        mock_controls_server = Mock()
        mock_controls_server.port = 70000  # Port too high
        mock_controls_server.is_running = True
        
        # Update should handle invalid ports gracefully
        changed = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        
        # Should still generate URLs (even if ports are invalid)
        urls = self.manager.get_current_urls()
        self.assertEqual(urls['display'], "http://localhost:-1")
        self.assertEqual(urls['controls'], "http://localhost:70000")
    
    def test_url_update_with_server_communication_errors(self):
        """Test URL update with server communication errors."""
        # Create mock servers that raise exceptions
        mock_web_server = Mock()
        type(mock_web_server).port = PropertyMock(side_effect=Exception("Communication error"))
        
        mock_controls_server = Mock()
        type(mock_controls_server).port = PropertyMock(side_effect=Exception("Communication error"))
        
        # Update should handle errors gracefully
        changed = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        self.assertFalse(changed)
        
        # Should fall back to last known ports (defaults)
        urls = self.manager.get_current_urls()
        self.assertEqual(urls['display'], "http://localhost:8080")
        self.assertEqual(urls['controls'], "http://localhost:8081")
    
    def test_url_update_with_partial_server_errors(self):
        """Test URL update with partial server communication errors."""
        # First set up a known state
        mock_baseline_web = Mock()
        mock_baseline_web.port = 8888
        mock_baseline_web.is_running = True
        
        mock_baseline_controls = Mock()
        mock_baseline_controls.port = 8889
        mock_baseline_controls.is_running = True
        
        # Set baseline to establish last known ports
        self.manager.update_from_servers(mock_baseline_web, mock_baseline_controls)
        
        # Now create servers where one works and one fails
        # Due to the current implementation, when ANY server raises an exception during port access,
        # the entire detection falls back to last known ports
        mock_web_server = Mock()
        mock_web_server.port = 9000
        mock_web_server.is_running = True
        
        mock_controls_server = Mock()
        type(mock_controls_server).port = PropertyMock(side_effect=Exception("Controls error"))
        
        # Update should handle partial errors by falling back to last known ports
        changed = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        self.assertFalse(changed)  # No change because it falls back to last known ports
        
        # Should fall back to last known ports for both servers
        urls = self.manager.get_current_urls()
        self.assertEqual(urls['display'], "http://localhost:8888")  # Last known
        self.assertEqual(urls['controls'], "http://localhost:8889")  # Last known
    
    def test_hyperlink_widget_url_attribute_update(self):
        """Test that hyperlink widget URL attributes are updated."""
        # Create mock hyperlink widgets
        mock_display_widget = Mock()
        mock_controls_widget = Mock()
        
        hyperlink_widgets = {
            'display': mock_display_widget,
            'controls': mock_controls_widget
        }
        
        # Change ports
        self.config.update_ports(9000, 9001)
        
        # Refresh hyperlink display
        self.manager.refresh_hyperlink_display(hyperlink_widgets)
        
        # Verify URL attributes are set
        self.assertEqual(mock_display_widget.url, "http://localhost:9000")
        self.assertEqual(mock_controls_widget.url, "http://localhost:9001")
    
    def test_url_update_callback_integration(self):
        """Test URL update integration with callback mechanisms."""
        # Track URL changes
        url_changes = []
        
        def url_change_callback(old_urls, new_urls):
            url_changes.append((old_urls, new_urls))
        
        # Create mock servers
        mock_web_server = Mock()
        mock_web_server.port = 8080
        mock_web_server.is_running = True
        
        mock_controls_server = Mock()
        mock_controls_server.port = 8081
        mock_controls_server.is_running = True
        
        # Initial state
        old_urls = self.manager.get_current_urls()
        
        # Update servers
        mock_web_server.port = 9000
        changed = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        
        if changed:
            new_urls = self.manager.get_current_urls()
            url_change_callback(old_urls, new_urls)
        
        # Verify callback was triggered
        self.assertEqual(len(url_changes), 1)
        old, new = url_changes[0]
        self.assertEqual(old['display'], "http://localhost:8080")
        self.assertEqual(new['display'], "http://localhost:9000")
    
    def test_concurrent_url_updates(self):
        """Test handling of concurrent URL updates."""
        # Create multiple mock server pairs
        servers_list = []
        for i in range(5):
            web_server = Mock()
            web_server.port = 8080 + i * 10
            web_server.is_running = True
            
            controls_server = Mock()
            controls_server.port = 8081 + i * 10
            controls_server.is_running = True
            
            servers_list.append((web_server, controls_server))
        
        # Update from different server pairs rapidly
        results = []
        for web_server, controls_server in servers_list:
            changed = self.manager.update_from_servers(web_server, controls_server)
            results.append(changed)
            urls = self.manager.get_current_urls()
            results.append(urls)
        
        # Verify final state matches last update
        final_urls = self.manager.get_current_urls()
        expected_web_port = 8080 + (len(servers_list) - 1) * 10
        expected_controls_port = 8081 + (len(servers_list) - 1) * 10
        
        self.assertEqual(final_urls['display'], f"http://localhost:{expected_web_port}")
        self.assertEqual(final_urls['controls'], f"http://localhost:{expected_controls_port}")
    
    def test_url_update_with_custom_host_configuration(self):
        """Test URL update with custom host configuration."""
        # Create config with custom host
        custom_config = HyperlinkConfig(host="127.0.0.1")
        custom_manager = DynamicHyperlinkManager(custom_config)
        
        # Create mock servers
        mock_web_server = Mock()
        mock_web_server.port = 9000
        mock_web_server.is_running = True
        
        mock_controls_server = Mock()
        mock_controls_server.port = 9001
        mock_controls_server.is_running = True
        
        # Update from servers
        changed = custom_manager.update_from_servers(mock_web_server, mock_controls_server)
        self.assertTrue(changed)
        
        # Verify URLs use custom host
        urls = custom_manager.get_current_urls()
        self.assertEqual(urls['display'], "http://127.0.0.1:9000")
        self.assertEqual(urls['controls'], "http://127.0.0.1:9001")
    
    def test_url_update_persistence_across_manager_instances(self):
        """Test URL update persistence across manager instances."""
        # Create first manager and update ports
        manager1 = DynamicHyperlinkManager()
        
        mock_web_server = Mock()
        mock_web_server.port = 9000
        mock_web_server.is_running = True
        
        mock_controls_server = Mock()
        mock_controls_server.port = 9001
        mock_controls_server.is_running = True
        
        manager1.update_from_servers(mock_web_server, mock_controls_server)
        
        # Create second manager with same config
        manager2 = DynamicHyperlinkManager(manager1.config)
        
        # Should have same URLs
        urls1 = manager1.get_current_urls()
        urls2 = manager2.get_current_urls()
        
        self.assertEqual(urls1, urls2)
    
    def test_url_update_with_server_port_range_validation(self):
        """Test URL update with server port range validation."""
        # Test with various port ranges
        port_ranges = [
            (1024, 1025),    # Low ports
            (8080, 8081),    # Default ports
            (49152, 49153),  # Dynamic/private ports
            (65534, 65535),  # High ports
        ]
        
        for web_port, controls_port in port_ranges:
            with self.subTest(web_port=web_port, controls_port=controls_port):
                mock_web_server = Mock()
                mock_web_server.port = web_port
                mock_web_server.is_running = True
                
                mock_controls_server = Mock()
                mock_controls_server.port = controls_port
                mock_controls_server.is_running = True
                
                # Update from servers
                self.manager.update_from_servers(mock_web_server, mock_controls_server)
                
                # Verify URLs
                urls = self.manager.get_current_urls()
                self.assertEqual(urls['display'], f"http://localhost:{web_port}")
                self.assertEqual(urls['controls'], f"http://localhost:{controls_port}")


if __name__ == '__main__':
    unittest.main()