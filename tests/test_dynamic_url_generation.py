"""
Tests for dynamic URL generation and port detection functionality.

Tests the HyperlinkConfig and DynamicHyperlinkManager classes for proper
URL generation, port detection, and server communication as specified in requirements.
"""

import unittest
import socket
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from gui.hyperlink_config import HyperlinkConfig, DynamicHyperlinkManager


class TestHyperlinkConfig(unittest.TestCase):
    """Test cases for HyperlinkConfig class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = HyperlinkConfig()
    
    def test_default_configuration(self):
        """Test default configuration values."""
        self.assertEqual(self.config.web_server_port, 8080)
        self.assertEqual(self.config.controls_server_port, 8081)
        self.assertEqual(self.config.host, "localhost")
    
    def test_custom_configuration(self):
        """Test custom configuration values."""
        config = HyperlinkConfig(
            web_server_port=9000,
            controls_server_port=9001,
            host="127.0.0.1"
        )
        
        self.assertEqual(config.web_server_port, 9000)
        self.assertEqual(config.controls_server_port, 9001)
        self.assertEqual(config.host, "127.0.0.1")
    
    def test_get_display_url(self):
        """Test display URL generation."""
        # Test with default ports
        expected_url = "http://localhost:8080"
        self.assertEqual(self.config.get_display_url(), expected_url)
        
        # Test with custom ports
        self.config.web_server_port = 9090
        expected_url = "http://localhost:9090"
        self.assertEqual(self.config.get_display_url(), expected_url)
    
    def test_get_controls_url(self):
        """Test controls URL generation."""
        # Test with default ports
        expected_url = "http://localhost:8081"
        self.assertEqual(self.config.get_controls_url(), expected_url)
        
        # Test with custom ports
        self.config.controls_server_port = 9091
        expected_url = "http://localhost:9091"
        self.assertEqual(self.config.get_controls_url(), expected_url)
    
    def test_update_ports_returns_true_when_changed(self):
        """Test that update_ports returns True when ports change."""
        result = self.config.update_ports(9000, 9001)
        
        self.assertTrue(result)
        self.assertEqual(self.config.web_server_port, 9000)
        self.assertEqual(self.config.controls_server_port, 9001)
    
    def test_update_ports_returns_false_when_unchanged(self):
        """Test that update_ports returns False when ports don't change."""
        result = self.config.update_ports(8080, 8081)
        
        self.assertFalse(result)
        self.assertEqual(self.config.web_server_port, 8080)
        self.assertEqual(self.config.controls_server_port, 8081)
    
    def test_get_urls_dictionary(self):
        """Test get_urls returns correct dictionary."""
        urls = self.config.get_urls()
        
        expected_urls = {
            'display': 'http://localhost:8080',
            'controls': 'http://localhost:8081'
        }
        
        self.assertEqual(urls, expected_urls)
    
    def test_url_generation_with_different_hosts(self):
        """Test URL generation with different host configurations."""
        test_hosts = ["127.0.0.1", "0.0.0.0", "example.com"]
        
        for host in test_hosts:
            with self.subTest(host=host):
                config = HyperlinkConfig(host=host)
                
                display_url = config.get_display_url()
                controls_url = config.get_controls_url()
                
                self.assertEqual(display_url, f"http://{host}:8080")
                self.assertEqual(controls_url, f"http://{host}:8081")
    
    def test_url_generation_with_high_port_numbers(self):
        """Test URL generation with high port numbers."""
        config = HyperlinkConfig(
            web_server_port=65535,
            controls_server_port=65534
        )
        
        display_url = config.get_display_url()
        controls_url = config.get_controls_url()
        
        self.assertEqual(display_url, "http://localhost:65535")
        self.assertEqual(controls_url, "http://localhost:65534")


class TestDynamicHyperlinkManager(unittest.TestCase):
    """Test cases for DynamicHyperlinkManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = HyperlinkConfig()
        self.manager = DynamicHyperlinkManager(self.config)
    
    def test_initialization_with_config(self):
        """Test manager initialization with provided config."""
        self.assertEqual(self.manager.config, self.config)
        self.assertEqual(self.manager._last_known_ports, (8080, 8081))
    
    def test_initialization_without_config(self):
        """Test manager initialization without provided config."""
        manager = DynamicHyperlinkManager()
        
        self.assertIsInstance(manager.config, HyperlinkConfig)
        self.assertEqual(manager.config.web_server_port, 8080)
        self.assertEqual(manager.config.controls_server_port, 8081)
    
    def test_detect_server_ports_with_running_servers(self):
        """Test port detection with running server instances."""
        # Create mock servers
        mock_web_server = Mock()
        mock_web_server.port = 9000
        mock_web_server.is_running = True
        
        mock_controls_server = Mock()
        mock_controls_server.port = 9001
        mock_controls_server.is_running = True
        
        # Test port detection
        web_port, controls_port = self.manager.detect_server_ports(
            mock_web_server, mock_controls_server
        )
        
        self.assertEqual(web_port, 9000)
        self.assertEqual(controls_port, 9001)
    
    def test_detect_server_ports_with_stopped_servers(self):
        """Test port detection with stopped server instances."""
        # Create mock servers that are not running
        mock_web_server = Mock()
        mock_web_server.port = 9000
        mock_web_server.is_running = False
        
        mock_controls_server = Mock()
        mock_controls_server.port = 9001
        mock_controls_server.is_running = False
        
        # Test port detection (should use configured defaults)
        web_port, controls_port = self.manager.detect_server_ports(
            mock_web_server, mock_controls_server
        )
        
        self.assertEqual(web_port, 8080)  # Default fallback
        self.assertEqual(controls_port, 8081)  # Default fallback
    
    def test_detect_server_ports_with_get_current_port_method(self):
        """Test port detection using get_current_port method."""
        # Create mock servers with get_current_port method but no port attribute
        mock_web_server = Mock(spec=['get_current_port'])
        mock_web_server.get_current_port.return_value = 9500
        
        mock_controls_server = Mock(spec=['get_current_port'])
        mock_controls_server.get_current_port.return_value = 9501
        
        # Test port detection
        web_port, controls_port = self.manager.detect_server_ports(
            mock_web_server, mock_controls_server
        )
        
        self.assertEqual(web_port, 9500)
        self.assertEqual(controls_port, 9501)
    
    def test_detect_server_ports_with_exception_handling(self):
        """Test port detection with exception handling."""
        # Create mock servers that raise exceptions when accessing port
        mock_web_server = Mock()
        type(mock_web_server).port = PropertyMock(side_effect=Exception("Server error"))
        
        mock_controls_server = Mock()
        type(mock_controls_server).port = PropertyMock(side_effect=Exception("Server error"))
        
        # Test port detection (should use last known ports)
        web_port, controls_port = self.manager.detect_server_ports(
            mock_web_server, mock_controls_server
        )
        
        # Should fall back to last known ports (initial defaults)
        self.assertEqual(web_port, 8080)
        self.assertEqual(controls_port, 8081)
    
    def test_update_from_servers_returns_true_when_changed(self):
        """Test that update_from_servers returns True when ports change."""
        # Create mock servers with different ports
        mock_web_server = Mock()
        mock_web_server.port = 9000
        mock_web_server.is_running = True
        
        mock_controls_server = Mock()
        mock_controls_server.port = 9001
        mock_controls_server.is_running = True
        
        # Update from servers
        result = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        
        self.assertTrue(result)
        self.assertEqual(self.manager.config.web_server_port, 9000)
        self.assertEqual(self.manager.config.controls_server_port, 9001)
    
    def test_update_from_servers_returns_false_when_unchanged(self):
        """Test that update_from_servers returns False when ports don't change."""
        # Create mock servers with same ports as defaults
        mock_web_server = Mock()
        mock_web_server.port = 8080
        mock_web_server.is_running = True
        
        mock_controls_server = Mock()
        mock_controls_server.port = 8081
        mock_controls_server.is_running = True
        
        # Update from servers
        result = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        
        self.assertFalse(result)
        self.assertEqual(self.manager.config.web_server_port, 8080)
        self.assertEqual(self.manager.config.controls_server_port, 8081)
    
    def test_get_current_urls(self):
        """Test getting current URLs."""
        urls = self.manager.get_current_urls()
        
        expected_urls = {
            'display': 'http://localhost:8080',
            'controls': 'http://localhost:8081'
        }
        
        self.assertEqual(urls, expected_urls)
    
    def test_refresh_hyperlink_display(self):
        """Test refreshing hyperlink display widgets."""
        # Create mock hyperlink widgets
        mock_display_widget = Mock()
        mock_controls_widget = Mock()
        
        hyperlink_widgets = {
            'display': mock_display_widget,
            'controls': mock_controls_widget
        }
        
        # Refresh hyperlink display
        self.manager.refresh_hyperlink_display(hyperlink_widgets)
        
        # Verify widgets were updated
        mock_display_widget.configure.assert_called_with(text="http://localhost:8080")
        mock_controls_widget.configure.assert_called_with(text="http://localhost:8081")
        
        # Verify URL attributes were set
        self.assertEqual(mock_display_widget.url, "http://localhost:8080")
        self.assertEqual(mock_controls_widget.url, "http://localhost:8081")
    
    def test_refresh_hyperlink_display_with_missing_widgets(self):
        """Test refreshing hyperlink display with missing widgets."""
        # Test with empty dictionary
        self.manager.refresh_hyperlink_display({})
        # Should not raise an exception
        
        # Test with None widgets
        hyperlink_widgets = {
            'display': None,
            'controls': None
        }
        
        self.manager.refresh_hyperlink_display(hyperlink_widgets)
        # Should not raise an exception
    
    def test_handle_server_unavailable(self):
        """Test handling when servers are unavailable."""
        fallback_urls = self.manager.handle_server_unavailable()
        
        expected_urls = {
            'display': 'http://localhost:8080',
            'controls': 'http://localhost:8081'
        }
        
        self.assertEqual(fallback_urls, expected_urls)
    
    def test_is_port_available(self):
        """Test port availability checking."""
        # Test with a port that should be available (high port number)
        available = self.manager.is_port_available(65432)
        self.assertTrue(available)
        
        # Test with a port that might be in use (common port)
        # Note: This test might be flaky depending on system state
        # We'll just verify the method doesn't crash
        result = self.manager.is_port_available(80)
        self.assertIsInstance(result, bool)
    
    def test_find_available_ports(self):
        """Test finding available ports."""
        web_port, controls_port = self.manager.find_available_ports(50000, 50001)
        
        # Verify ports are in expected range
        self.assertGreaterEqual(web_port, 50000)
        self.assertGreaterEqual(controls_port, 50001)
        
        # Verify ports are different
        self.assertNotEqual(web_port, controls_port)
    
    def test_get_config(self):
        """Test getting configuration."""
        config = self.manager.get_config()
        self.assertEqual(config, self.config)
    
    def test_string_representations(self):
        """Test string representations of the manager."""
        str_repr = str(self.manager)
        self.assertIn("DynamicHyperlinkManager", str_repr)
        self.assertIn("http://localhost:8080", str_repr)
        self.assertIn("http://localhost:8081", str_repr)
        
        repr_str = repr(self.manager)
        self.assertIn("DynamicHyperlinkManager", repr_str)
        self.assertIn("config=", repr_str)
    
    @patch('socket.socket')
    def test_port_availability_with_socket_error(self, mock_socket):
        """Test port availability checking with socket errors."""
        # Mock socket to raise OSError
        mock_socket_instance = Mock()
        mock_socket_instance.bind.side_effect = OSError("Port in use")
        mock_socket.return_value.__enter__.return_value = mock_socket_instance
        
        # Test port availability
        available = self.manager.is_port_available(8080)
        self.assertFalse(available)
    
    def test_update_from_servers_with_exception(self):
        """Test update_from_servers with exception handling."""
        # Create mock servers that raise exceptions during port detection
        mock_web_server = Mock()
        type(mock_web_server).port = PropertyMock(side_effect=Exception("Connection error"))
        
        mock_controls_server = Mock()
        type(mock_controls_server).port = PropertyMock(side_effect=Exception("Connection error"))
        
        # Update from servers (should handle exceptions gracefully)
        result = self.manager.update_from_servers(mock_web_server, mock_controls_server)
        
        # Should return False due to error (ports remain unchanged from defaults)
        self.assertFalse(result)
    
    def test_refresh_hyperlink_display_with_exception(self):
        """Test refresh_hyperlink_display with widget exceptions."""
        # Create mock widget that raises exception on configure
        mock_display_widget = Mock()
        mock_display_widget.configure.side_effect = Exception("Widget error")
        
        hyperlink_widgets = {
            'display': mock_display_widget,
            'controls': None
        }
        
        # Should handle exception gracefully
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
        
        # Test with custom config
        custom_config = HyperlinkConfig(host="127.0.0.1", web_server_port=9000, controls_server_port=9001)
        custom_manager = DynamicHyperlinkManager(custom_config)
        
        custom_fallback_urls = custom_manager.handle_server_unavailable()
        expected_custom_urls = {
            'display': "http://127.0.0.1:9000",
            'controls': "http://127.0.0.1:9001"
        }
        
        self.assertEqual(custom_fallback_urls, expected_custom_urls)
    
    def test_port_detection_priority_order(self):
        """Test that port detection follows correct priority order."""
        # Create mock server with both port attribute and get_current_port method
        mock_web_server = Mock()
        mock_web_server.port = 9000
        mock_web_server.is_running = True
        mock_web_server.get_current_port.return_value = 9500
        
        # Port attribute should take priority when server is running
        web_port, _ = self.manager.detect_server_ports(mock_web_server, None)
        self.assertEqual(web_port, 9000)
        
        # When server is not running, should use configured port
        mock_web_server.is_running = False
        web_port, _ = self.manager.detect_server_ports(mock_web_server, None)
        self.assertEqual(web_port, 8080)  # Default fallback
    
    def test_last_known_ports_fallback(self):
        """Test fallback to last known ports."""
        # Update with known good ports
        mock_web_server = Mock()
        mock_web_server.port = 9000
        mock_web_server.is_running = True
        
        mock_controls_server = Mock()
        mock_controls_server.port = 9001
        mock_controls_server.is_running = True
        
        # First update to establish last known ports
        self.manager.update_from_servers(mock_web_server, mock_controls_server)
        
        # Now create servers that will cause exceptions
        error_web_server = Mock()
        type(error_web_server).port = PropertyMock(side_effect=Exception("Error"))
        
        error_controls_server = Mock()
        type(error_controls_server).port = PropertyMock(side_effect=Exception("Error"))
        
        # Should fall back to last known ports
        web_port, controls_port = self.manager.detect_server_ports(
            error_web_server, error_controls_server
        )
        
        self.assertEqual(web_port, 9000)
        self.assertEqual(controls_port, 9001)


if __name__ == '__main__':
    unittest.main()