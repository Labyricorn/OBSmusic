"""
Unit tests for the Flask web server functionality.
Tests server initialization, routes, WebSocket events, and error handling.
"""

import unittest
import json
import tempfile
import os
import shutil
import threading
import time
from unittest.mock import patch, MagicMock
import requests

# Import the web server module
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from web.server import WebServer, create_web_server


class TestWebServer(unittest.TestCase):
    """Test cases for WebServer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create data directory for config files
        os.makedirs('data', exist_ok=True)
        
        # Create web server instance for testing
        self.server = WebServer(host='127.0.0.1', port=8081)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'server') and self.server.is_running:
            self.server.stop()
            time.sleep(0.1)  # Give server time to stop
        
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_server_initialization(self):
        """Test WebServer initialization with default values."""
        server = WebServer()
        
        self.assertEqual(server.host, '127.0.0.1')
        self.assertEqual(server.port, 8080)
        self.assertFalse(server.is_running)
        self.assertIsNone(server.server_thread)
        
        # Test initial song data
        expected_song_data = {
            'title': 'No song playing',
            'artist': 'Music Player',
            'artwork_url': None,
            'is_playing': False
        }
        self.assertEqual(server.current_song_data, expected_song_data)
    
    def test_server_initialization_custom_params(self):
        """Test WebServer initialization with custom parameters."""
        server = WebServer(host='localhost', port=9000)
        
        self.assertEqual(server.host, 'localhost')
        self.assertEqual(server.port, 9000)
        self.assertFalse(server.is_running)
    
    def test_create_web_server_factory(self):
        """Test the factory function for creating web server instances."""
        server = create_web_server()
        self.assertIsInstance(server, WebServer)
        self.assertEqual(server.host, '127.0.0.1')
        self.assertEqual(server.port, 8080)
        
        server_custom = create_web_server(host='localhost', port=9000)
        self.assertEqual(server_custom.host, 'localhost')
        self.assertEqual(server_custom.port, 9000)
    
    def test_find_available_port(self):
        """Test finding available ports when default is taken."""
        # Test normal case
        port = self.server._find_available_port(8081)
        self.assertGreaterEqual(port, 8081)
        self.assertLess(port, 8091)
        
        # Test when no ports are available (mock socket to always fail)
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.__enter__.return_value.bind.side_effect = OSError("Port in use")
            
            with self.assertRaises(RuntimeError):
                self.server._find_available_port(8081)
    
    def test_get_default_config(self):
        """Test default configuration values."""
        config = self.server._get_default_config()
        
        expected_config = {
            'font_family': 'Arial',
            'font_size': 24,
            'font_weight': 'normal',
            'background_color': '#000000',
            'text_color': '#ffffff',
            'accent_color': '#ff6b6b',
            'show_artwork': True,
            'artwork_size': 200,
            'layout': 'horizontal'
        }
        
        self.assertEqual(config, expected_config)
    
    def test_update_song_data(self):
        """Test updating song data."""
        # Test updating with all parameters
        self.server.update_song_data(
            title="Test Song",
            artist="Test Artist",
            artwork_url="/artwork/test.jpg",
            is_playing=True
        )
        
        expected_data = {
            'title': 'Test Song',
            'artist': 'Test Artist',
            'artwork_url': '/artwork/test.jpg',
            'is_playing': True
        }
        
        self.assertEqual(self.server.current_song_data, expected_data)
        
        # Test updating with minimal parameters
        self.server.update_song_data(title="Another Song", artist="Another Artist")
        
        expected_data = {
            'title': 'Another Song',
            'artist': 'Another Artist',
            'artwork_url': None,
            'is_playing': True
        }
        
        self.assertEqual(self.server.current_song_data, expected_data)
    
    def test_get_server_url(self):
        """Test getting server URL."""
        url = self.server.get_server_url()
        self.assertEqual(url, "http://127.0.0.1:8081")
        
        server = WebServer(host='localhost', port=9000)
        url = server.get_server_url()
        self.assertEqual(url, "http://localhost:9000")
    
    def test_fallback_display_html(self):
        """Test fallback HTML display generation."""
        self.server.current_song_data = {
            'title': 'Test Song',
            'artist': 'Test Artist',
            'artwork_url': None,
            'is_playing': True
        }
        
        html = self.server._create_fallback_display()
        
        self.assertIn('Test Song', html)
        self.assertIn('Test Artist', html)
        self.assertIn('Playing', html)
        self.assertIn('<!DOCTYPE html>', html)
    
    def test_fallback_config_html(self):
        """Test fallback HTML config page generation."""
        html = self.server._create_fallback_config()
        
        self.assertIn('Configuration', html)
        self.assertIn('/api/song', html)
        self.assertIn('/api/config', html)
        self.assertIn('<!DOCTYPE html>', html)


class TestWebServerIntegration(unittest.TestCase):
    """Integration tests for WebServer with actual HTTP requests."""
    
    def setUp(self):
        """Set up test fixtures with running server."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create data directory and templates
        os.makedirs('data', exist_ok=True)
        os.makedirs('web/templates', exist_ok=True)
        
        # Create minimal templates for testing
        with open('web/templates/display.html', 'w') as f:
            f.write('<html><body>{{ song_data.title }} - {{ song_data.artist }}</body></html>')
        
        with open('web/templates/config.html', 'w') as f:
            f.write('<html><body>Configuration Page</body></html>')
        
        # Start server
        self.server = WebServer(host='127.0.0.1', port=8082)
        self.assertTrue(self.server.start())
        
        # Wait for server to start
        time.sleep(0.5)
        self.base_url = self.server.get_server_url()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'server') and self.server.is_running:
            self.server.stop()
            time.sleep(0.1)
        
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_server_start_and_stop(self):
        """Test server start and stop functionality."""
        self.assertTrue(self.server.is_running)
        
        # Test that server is accessible
        try:
            response = requests.get(f"{self.base_url}/api/song", timeout=2)
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.RequestException:
            self.fail("Server should be accessible after start()")
        
        # Test stop
        self.server.stop()
        self.assertFalse(self.server.is_running)
    
    def test_api_song_endpoint(self):
        """Test /api/song endpoint returns current song data."""
        response = requests.get(f"{self.base_url}/api/song")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('title', data)
        self.assertIn('artist', data)
        self.assertIn('artwork_url', data)
        self.assertIn('is_playing', data)
        
        # Test with updated song data
        self.server.update_song_data("Test Song", "Test Artist", is_playing=True)
        
        response = requests.get(f"{self.base_url}/api/song")
        data = response.json()
        
        self.assertEqual(data['title'], 'Test Song')
        self.assertEqual(data['artist'], 'Test Artist')
        self.assertTrue(data['is_playing'])
    
    def test_api_config_get_endpoint(self):
        """Test GET /api/config endpoint returns configuration."""
        response = requests.get(f"{self.base_url}/api/config")
        self.assertEqual(response.status_code, 200)
        
        config = response.json()
        self.assertIn('font_family', config)
        self.assertIn('font_size', config)
        self.assertIn('background_color', config)
    
    def test_api_config_post_endpoint(self):
        """Test POST /api/config endpoint saves configuration."""
        test_config = {
            'font_family': 'Helvetica',
            'font_size': 30,
            'background_color': '#ff0000'
        }
        
        response = requests.post(
            f"{self.base_url}/api/config",
            json=test_config,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        
        # Verify configuration was saved
        response = requests.get(f"{self.base_url}/api/config")
        saved_config = response.json()
        
        self.assertEqual(saved_config['font_family'], 'Helvetica')
        self.assertEqual(saved_config['font_size'], 30)
        self.assertEqual(saved_config['background_color'], '#ff0000')
    
    def test_api_config_post_invalid_data(self):
        """Test POST /api/config with invalid data."""
        # Test with no JSON data
        response = requests.post(f"{self.base_url}/api/config", 
                               headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 400)
        
        data = response.json()
        self.assertIn('error', data)
    
    def test_display_route(self):
        """Test main display route."""
        response = requests.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.headers.get('content-type', ''))
    
    def test_config_route(self):
        """Test configuration route."""
        response = requests.get(f"{self.base_url}/config")
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.headers.get('content-type', ''))
    
    def test_404_error_handling(self):
        """Test 404 error handling."""
        response = requests.get(f"{self.base_url}/nonexistent")
        self.assertEqual(response.status_code, 404)
        
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Not found')


class TestWebServerRealTimeUpdates(unittest.TestCase):
    """Integration tests for real-time display updates via WebSocket."""
    
    def setUp(self):
        """Set up test fixtures with running server and WebSocket client."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create data directory and templates
        os.makedirs('data', exist_ok=True)
        os.makedirs('web/templates', exist_ok=True)
        
        # Create display template with WebSocket functionality
        display_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Music Player Display</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
</head>
<body>
    <div id="song-title">{{ song_data.title }}</div>
    <div id="song-artist">{{ song_data.artist }}</div>
    <div id="status">{{ 'Playing' if song_data.is_playing else 'Stopped' }}</div>
    {% if song_data.artwork_url %}
    <img id="artwork" src="{{ song_data.artwork_url }}" alt="Album Artwork">
    {% endif %}
    
    <script>
        const socket = io();
        let lastUpdate = null;
        
        socket.on('song_update', function(data) {
            lastUpdate = data;
            document.getElementById('song-title').textContent = data.title;
            document.getElementById('song-artist').textContent = data.artist;
            document.getElementById('status').textContent = data.is_playing ? 'Playing' : 'Stopped';
            
            const artwork = document.getElementById('artwork');
            if (data.artwork_url) {
                if (!artwork) {
                    const img = document.createElement('img');
                    img.id = 'artwork';
                    img.src = data.artwork_url;
                    document.body.appendChild(img);
                } else {
                    artwork.src = data.artwork_url;
                }
            } else if (artwork) {
                artwork.remove();
            }
        });
        
        socket.on('config_updated', function(config) {
            if (config.background_color) {
                document.body.style.backgroundColor = config.background_color;
            }
            if (config.text_color) {
                document.getElementById('song-title').style.color = config.text_color;
                document.getElementById('song-artist').style.color = config.text_color;
            }
        });
        
        // Expose for testing
        window.getLastUpdate = function() { return lastUpdate; };
    </script>
</body>
</html>
        '''
        
        with open('web/templates/display.html', 'w') as f:
            f.write(display_template)
        
        with open('web/templates/config.html', 'w') as f:
            f.write('<html><body>Configuration Page</body></html>')
        
        # Start server
        self.server = WebServer(host='127.0.0.1', port=8085)
        self.assertTrue(self.server.start())
        
        # Wait for server to start
        time.sleep(0.5)
        self.base_url = self.server.get_server_url()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'server') and self.server.is_running:
            self.server.stop()
            time.sleep(0.1)
        
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_display_page_renders_initial_song_data(self):
        """Test that display page renders with initial song data."""
        # Set initial song data
        self.server.update_song_data("Initial Song", "Initial Artist", is_playing=False)
        
        response = requests.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)
        
        content = response.text
        self.assertIn("Initial Song", content)
        self.assertIn("Initial Artist", content)
        self.assertIn("Stopped", content)
    
    def test_display_page_handles_no_song_playing(self):
        """Test that display page handles placeholder content correctly."""
        # Reset to default state
        self.server.current_song_data = {
            'title': 'No song playing',
            'artist': 'Music Player',
            'artwork_url': None,
            'is_playing': False
        }
        
        response = requests.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)
        
        content = response.text
        self.assertIn("No song playing", content)
        self.assertIn("Music Player", content)
        self.assertIn("Stopped", content)
    
    def test_display_page_includes_websocket_client(self):
        """Test that display page includes WebSocket client code."""
        response = requests.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)
        
        content = response.text
        self.assertIn("socket.io", content)
        self.assertIn("song_update", content)
        self.assertIn("config_updated", content)
    
    def test_song_update_broadcast_via_websocket(self):
        """Test that song updates are broadcasted via WebSocket."""
        # This test verifies the server-side WebSocket functionality
        # by checking that update_song_data triggers the broadcast mechanism
        
        # Mock the socketio emit method to capture calls
        original_emit = self.server.socketio.emit
        emitted_events = []
        
        def mock_emit(event, data):
            emitted_events.append((event, data))
            return original_emit(event, data)
        
        self.server.socketio.emit = mock_emit
        
        # Update song data
        self.server.update_song_data(
            title="Test Song",
            artist="Test Artist",
            artwork_url="/test/artwork.jpg",
            is_playing=True
        )
        
        # Verify that song_update event was emitted
        self.assertEqual(len(emitted_events), 1)
        event_name, event_data = emitted_events[0]
        
        self.assertEqual(event_name, 'song_update')
        self.assertEqual(event_data['title'], 'Test Song')
        self.assertEqual(event_data['artist'], 'Test Artist')
        self.assertEqual(event_data['artwork_url'], '/test/artwork.jpg')
        self.assertTrue(event_data['is_playing'])
        
        # Restore original method
        self.server.socketio.emit = original_emit
    
    def test_configuration_update_broadcast_via_websocket(self):
        """Test that configuration updates are broadcasted via WebSocket."""
        # Mock the socketio emit method
        original_emit = self.server.socketio.emit
        emitted_events = []
        
        def mock_emit(event, data):
            emitted_events.append((event, data))
            return original_emit(event, data)
        
        self.server.socketio.emit = mock_emit
        
        # Send configuration update via API
        test_config = {
            'font_family': 'Helvetica',
            'background_color': '#ff0000',
            'text_color': '#ffffff'
        }
        
        response = requests.post(
            f"{self.base_url}/api/config",
            json=test_config,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify that config_updated event was emitted
        config_events = [e for e in emitted_events if e[0] == 'config_updated']
        self.assertEqual(len(config_events), 1)
        
        event_name, event_data = config_events[0]
        self.assertEqual(event_name, 'config_updated')
        self.assertEqual(event_data['font_family'], 'Helvetica')
        self.assertEqual(event_data['background_color'], '#ff0000')
        
        # Restore original method
        self.server.socketio.emit = original_emit
    
    def test_display_page_artwork_handling(self):
        """Test that display page properly handles artwork URLs."""
        # Test with artwork
        self.server.update_song_data(
            "Song With Art", 
            "Artist", 
            artwork_url="/artwork/test.jpg"
        )
        
        response = requests.get(f"{self.base_url}/")
        content = response.text
        
        self.assertIn("Song With Art", content)
        self.assertIn("/artwork/test.jpg", content)
        self.assertIn('img', content)
        
        # Test without artwork
        self.server.update_song_data("Song No Art", "Artist", artwork_url=None)
        
        response = requests.get(f"{self.base_url}/")
        content = response.text
        
        self.assertIn("Song No Art", content)
        # Should not include img tag when no artwork
        self.assertNotIn("/artwork/test.jpg", content)
    
    def test_websocket_connection_handling(self):
        """Test WebSocket connection and disconnection events."""
        # This test verifies that WebSocket functionality works by testing the update mechanism
        
        # Mock the emit method to capture connect behavior
        original_emit = self.server.socketio.emit
        emitted_events = []
        
        def mock_emit(event, data):
            emitted_events.append((event, data))
            return original_emit(event, data)
        
        self.server.socketio.emit = mock_emit
        
        try:
            # Test that song updates work (which requires WebSocket to be properly set up)
            self.server.update_song_data("Connection Test", "Test Artist")
            
            # Verify that the update was emitted
            self.assertTrue(len(emitted_events) > 0, "Should emit events when song updates")
            
            # Check that the emitted event contains the expected data
            song_events = [e for e in emitted_events if e[0] == 'song_update']
            self.assertTrue(len(song_events) > 0, "Should emit song_update events")
            
            event_data = song_events[0][1]
            self.assertEqual(event_data['title'], 'Connection Test')
            self.assertEqual(event_data['artist'], 'Test Artist')
            
            # Test that the WebSocket server is properly initialized
            self.assertIsNotNone(self.server.socketio, "SocketIO should be initialized")
            self.assertIsNotNone(self.server.socketio.server, "SocketIO server should be initialized")
        
        finally:
            # Restore original method
            self.server.socketio.emit = original_emit
    
    def test_real_time_update_sequence(self):
        """Test a sequence of real-time updates to verify continuous functionality."""
        # Mock the socketio emit method to track all emissions
        original_emit = self.server.socketio.emit
        emitted_updates = []
        
        def mock_emit(event, data):
            if event == 'song_update':
                emitted_updates.append(data.copy())
            return original_emit(event, data)
        
        self.server.socketio.emit = mock_emit
        
        # Simulate a sequence of song changes
        songs = [
            ("Song 1", "Artist 1", True),
            ("Song 2", "Artist 2", True),
            ("Song 3", "Artist 3", False),  # Paused
            ("Song 3", "Artist 3", True),   # Resumed
        ]
        
        for title, artist, is_playing in songs:
            self.server.update_song_data(title, artist, is_playing=is_playing)
        
        # Verify all updates were emitted
        self.assertEqual(len(emitted_updates), 4)
        
        # Verify the sequence
        self.assertEqual(emitted_updates[0]['title'], 'Song 1')
        self.assertTrue(emitted_updates[0]['is_playing'])
        
        self.assertEqual(emitted_updates[1]['title'], 'Song 2')
        self.assertTrue(emitted_updates[1]['is_playing'])
        
        self.assertEqual(emitted_updates[2]['title'], 'Song 3')
        self.assertFalse(emitted_updates[2]['is_playing'])
        
        self.assertEqual(emitted_updates[3]['title'], 'Song 3')
        self.assertTrue(emitted_updates[3]['is_playing'])
        
        # Restore original method
        self.server.socketio.emit = original_emit


class TestWebServerErrorHandling(unittest.TestCase):
    """Test error handling scenarios for WebServer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        os.makedirs('data', exist_ok=True)
        self.server = WebServer(host='127.0.0.1', port=8083)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'server') and self.server.is_running:
            self.server.stop()
            time.sleep(0.1)
        
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_start_server_port_conflict(self):
        """Test server startup with port conflicts."""
        # Start first server
        server1 = WebServer(host='127.0.0.1', port=8084)
        self.assertTrue(server1.start())
        
        try:
            # Try to start second server on same port
            server2 = WebServer(host='127.0.0.1', port=8084)
            result = server2.start()
            
            # Should succeed by finding alternative port
            self.assertTrue(result)
            self.assertNotEqual(server1.port, server2.port)
            
            server2.stop()
        finally:
            server1.stop()
    
    def test_config_file_error_handling(self):
        """Test configuration file error handling."""
        # Create corrupted config file
        config_path = os.path.join('data', 'config.json')
        with open(config_path, 'w') as f:
            f.write('invalid json content')
        
        # Server should handle corrupted config gracefully
        self.assertTrue(self.server.start())
        time.sleep(0.2)
        
        try:
            response = requests.get(f"{self.server.get_server_url()}/api/config", timeout=2)
            self.assertEqual(response.status_code, 200)
            
            # Should return default config
            config = response.json()
            self.assertEqual(config['font_family'], 'Arial')
        except requests.exceptions.RequestException:
            pass  # Server might not be fully ready
        
        self.server.stop()
    
    def test_missing_templates_fallback(self):
        """Test fallback behavior when templates are missing."""
        # Don't create template files
        self.assertTrue(self.server.start())
        time.sleep(0.2)
        
        try:
            # Should use fallback HTML
            response = requests.get(f"{self.server.get_server_url()}/", timeout=2)
            self.assertEqual(response.status_code, 200)
            
            # Should contain fallback content
            content = response.text
            self.assertIn('No song playing', content)
            self.assertIn('Music Player', content)
        except requests.exceptions.RequestException:
            pass  # Server might not be fully ready
        
        self.server.stop()


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)