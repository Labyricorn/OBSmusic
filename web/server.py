"""
Flask web server for OBS integration with real-time song updates.
Provides display routes and configuration interface.
"""

import logging
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
import socket
from typing import Optional, Dict, Any
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebServer:
    """Flask web server for OBS integration with WebSocket support."""
    
    def __init__(self, host: str = '127.0.0.1', port: int = 8080):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'music_player_secret_key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.server_thread: Optional[threading.Thread] = None
        self.is_running = False
        
        # Current song data for display
        self.current_song_data = {
            'title': 'No song playing',
            'artist': 'Music Player',
            'artwork_url': None,
            'is_playing': False
        }
        
        self._setup_routes()
        self._setup_socketio_events()
    
    def _setup_routes(self):
        """Set up Flask routes for the web server."""
        
        @self.app.route('/')
        def display():
            """Main display route for OBS browser source."""
            try:
                return render_template('display.html', song_data=self.current_song_data)
            except Exception as e:
                logger.error(f"Error rendering display template: {e}")
                return self._create_fallback_display()
        
        @self.app.route('/config')
        def config():
            """Configuration interface route."""
            try:
                return render_template('config.html')
            except Exception as e:
                logger.error(f"Error rendering config template: {e}")
                return self._create_fallback_config()
        
        @self.app.route('/api/song')
        def get_current_song():
            """API endpoint to get current song data."""
            return jsonify(self.current_song_data)
        
        @self.app.route('/static/artwork/<filename>')
        def serve_artwork(filename):
            """Serve artwork files."""
            try:
                from flask import send_from_directory
                artwork_dir = os.path.join('data', 'artwork')
                if os.path.exists(os.path.join(artwork_dir, filename)):
                    return send_from_directory(artwork_dir, filename)
                else:
                    return jsonify({'error': 'Artwork not found'}), 404
            except Exception as e:
                logger.error(f"Error serving artwork {filename}: {e}")
                return jsonify({'error': 'Failed to serve artwork'}), 500
        
        @self.app.route('/api/config', methods=['GET', 'POST'])
        def handle_config():
            """Handle configuration GET and POST requests."""
            if request.method == 'GET':
                # Return current configuration
                config_path = os.path.join('data', 'config.json')
                try:
                    if os.path.exists(config_path):
                        with open(config_path, 'r') as f:
                            config = json.load(f)
                    else:
                        config = self._get_default_config()
                    return jsonify(config)
                except Exception as e:
                    logger.error(f"Error loading configuration: {e}")
                    return jsonify(self._get_default_config())
            
            elif request.method == 'POST':
                # Update configuration
                try:
                    config_data = request.get_json()
                    if config_data is None:
                        return jsonify({'error': 'No configuration data provided'}), 400
                    
                    # Save configuration
                    config_path = os.path.join('data', 'config.json')
                    os.makedirs(os.path.dirname(config_path), exist_ok=True)
                    
                    with open(config_path, 'w') as f:
                        json.dump(config_data, f, indent=2)
                    
                    # Emit configuration update to all connected clients
                    self.socketio.emit('config_updated', config_data)
                    
                    return jsonify({'success': True, 'message': 'Configuration updated'})
                except Exception as e:
                    logger.error(f"Error saving configuration: {e}")
                    # Check if it's a JSON parsing error
                    if "400 Bad Request" in str(e) or "JSON" in str(e):
                        return jsonify({'error': 'Invalid JSON data'}), 400
                    return jsonify({'error': 'Failed to save configuration'}), 500
        
        @self.app.errorhandler(404)
        def not_found(error):
            """Handle 404 errors."""
            return jsonify({'error': 'Not found'}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            """Handle 500 errors."""
            logger.error(f"Internal server error: {error}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def _setup_socketio_events(self):
        """Set up WebSocket event handlers."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            logger.info(f"Client connected: {request.sid}")
            # Send current song data to newly connected client
            emit('song_update', self.current_song_data)
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            logger.info(f"Client disconnected: {request.sid}")
        
        @self.socketio.on('request_song_update')
        def handle_song_request():
            """Handle request for current song data."""
            emit('song_update', self.current_song_data)
    
    def _create_fallback_display(self) -> str:
        """Create a fallback HTML display when template is missing."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Music Player Display</title>
            <style>
                body {{ 
                    background: #000; 
                    color: #fff; 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px; 
                }}
            </style>
        </head>
        <body>
            <h1>{self.current_song_data['title']}</h1>
            <h2>{self.current_song_data['artist']}</h2>
            <p>Status: {'Playing' if self.current_song_data['is_playing'] else 'Stopped'}</p>
        </body>
        </html>
        """
    
    def _create_fallback_config(self) -> str:
        """Create a fallback HTML config page when template is missing."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Music Player Configuration</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    padding: 20px; 
                    max-width: 600px; 
                    margin: 0 auto; 
                }
            </style>
        </head>
        <body>
            <h1>Configuration</h1>
            <p>Configuration interface will be available when templates are implemented.</p>
            <p>Current API endpoints:</p>
            <ul>
                <li>GET /api/song - Get current song data</li>
                <li>GET /api/config - Get configuration</li>
                <li>POST /api/config - Update configuration</li>
            </ul>
        </body>
        </html>
        """
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration settings."""
        return {
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
    
    def _find_available_port(self, start_port: int = 8080) -> int:
        """Find an available port starting from the given port."""
        for port in range(start_port, start_port + 50):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((self.host, port))
                    return port
            except OSError:
                continue
        raise RuntimeError(f"No available ports found starting from {start_port}")
    
    def start(self) -> bool:
        """Start the web server in a separate thread."""
        if self.is_running:
            logger.warning("Web server is already running")
            return True
        
        try:
            # Try to find an available port if the default is taken
            try:
                self.port = self._find_available_port(self.port)
            except RuntimeError as e:
                logger.error(f"Failed to find available port: {e}")
                return False
            
            # Start server in a separate thread
            self.server_thread = threading.Thread(
                target=self._run_server,
                daemon=True
            )
            self.server_thread.start()
            
            logger.info(f"Web server starting on http://{self.host}:{self.port}")
            self.is_running = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to start web server: {e}")
            return False
    
    def _run_server(self):
        """Run the Flask-SocketIO server with comprehensive error handling."""
        try:
            self.socketio.run(
                self.app,
                host=self.host,
                port=self.port,
                debug=False,
                use_reloader=False,
                log_output=False
            )
        except OSError as e:
            if "Address already in use" in str(e):
                logger.error(f"Port {self.port} is already in use")
                # Try to find another port
                try:
                    new_port = self._find_available_port(self.port + 1)
                    logger.info(f"Trying alternative port: {new_port}")
                    self.port = new_port
                    self.socketio.run(
                        self.app,
                        host=self.host,
                        port=self.port,
                        debug=False,
                        use_reloader=False,
                        log_output=False
                    )
                except Exception as retry_error:
                    logger.error(f"Failed to start on alternative port: {retry_error}")
                    self.is_running = False
            else:
                logger.error(f"Network error starting web server: {e}")
                self.is_running = False
        except Exception as e:
            logger.error(f"Unexpected web server error: {e}")
            self.is_running = False
    
    def stop(self):
        """Stop the web server."""
        if not self.is_running:
            return
        
        self.is_running = False
        logger.info("Web server stopped")
    
    def update_song_data(self, title: str, artist: str, artwork_url: Optional[str] = None, is_playing: bool = True):
        """Update current song data and broadcast to all connected clients."""
        self.current_song_data = {
            'title': title,
            'artist': artist,
            'artwork_url': artwork_url,
            'is_playing': is_playing
        }
        
        # Broadcast update to all connected WebSocket clients
        if self.is_running:
            self.socketio.emit('song_update', self.current_song_data)
            logger.info(f"Broadcasted song update: {title} by {artist}")
    
    def get_server_url(self) -> str:
        """Get the server URL."""
        return f"http://{self.host}:{self.port}"


# Factory function for creating web server instance
def create_web_server(host: str = '127.0.0.1', port: int = 8080) -> WebServer:
    """Create and return a WebServer instance."""
    return WebServer(host, port)


if __name__ == '__main__':
    # For testing purposes
    server = create_web_server()
    if server.start():
        print(f"Server running at {server.get_server_url()}")
        print("Press Ctrl+C to stop")
        try:
            # Keep the main thread alive
            import time
            while server.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            server.stop()
    else:
        print("Failed to start server")