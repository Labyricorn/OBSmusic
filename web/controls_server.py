"""
Separate Flask web server for music player controls interface.
Runs on a different port from the main display server.
"""

import logging
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
import socket
from typing import Optional, Dict, Any
import json
import os

logger = logging.getLogger(__name__)


class ControlsServer:
    """Flask web server for music player controls interface."""
    
    def __init__(self, host: str = '127.0.0.1', port: int = 8081, debug_mode: bool = False):
        self.host = host
        self.port = port
        self.debug_mode = debug_mode
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'music_player_controls_secret_key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.server_thread: Optional[threading.Thread] = None
        self.is_running = False
        
        # Current song data for display
        self.current_song_data = {
            'title': 'No song playing',
            'artist': 'Music Player',
            'status': 'Stopped'
        }
        
        # Control callbacks
        self._control_callbacks = {}
        
        # Load configuration
        self.config = self._load_config()
        
        self._setup_routes()
        self._setup_socketio_events()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json file."""
        config_path = os.path.join('data', 'config.json')
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.debug(f"Loaded config from {config_path}")
                    return config
            else:
                logger.warning(f"Config file not found at {config_path}, using defaults")
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {e}")
        
        # Return default config if loading fails
        return {
            'background_color': '#000000',
            'player_background_color': 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
            'player_frame_fill_color': 'rgba(255, 255, 255, 0.1)',
            'title': {'color': '#ffffff'},
            'artist': {'color': '#cccccc'}
        }
    
    def _setup_routes(self):
        """Set up Flask routes for the controls server."""
        
        @self.app.route('/')
        def controls():
            """Main controls interface route."""
            try:
                return render_template('controls.html', 
                                     song_data=self.current_song_data,
                                     config=self.config)
            except Exception as e:
                logger.error(f"Error rendering controls template: {e}")
                return self._create_fallback_controls()
        
        @self.app.route('/api/song')
        def get_current_song():
            """API endpoint to get current song data."""
            return jsonify(self.current_song_data)
        
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
            logger.info(f"Controls client connected: {request.sid}")
            # Send current song data to newly connected client
            emit('song_update', self.current_song_data)
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            logger.info(f"Controls client disconnected: {request.sid}")
        
        @self.socketio.on('request_song_update')
        def handle_song_request():
            """Handle request for current song data."""
            emit('song_update', self.current_song_data)
        
        @self.socketio.on('control_action')
        def handle_control_action(data):
            """Handle control actions from the web controls interface."""
            action = data.get('action')
            logger.info(f"Received control action: {action}")
            
            if action in self._control_callbacks:
                try:
                    self._control_callbacks[action]()
                    logger.debug(f"Executed control action: {action}")
                except Exception as e:
                    logger.error(f"Error executing control action {action}: {e}")
            else:
                logger.warning(f"No callback registered for control action: {action}")
    
    def _create_fallback_controls(self) -> str:
        """Create a fallback HTML controls page when template is missing."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Music Player Controls</title>
            <style>
                body {{ 
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
                    color: #fff; 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px; 
                    min-height: 100vh;
                    margin: 0;
                }}
                .controls {{ margin: 20px 0; }}
                button {{ 
                    background: #ff6b6b; 
                    color: white; 
                    border: none; 
                    padding: 15px 20px; 
                    margin: 5px; 
                    border-radius: 50px; 
                    cursor: pointer; 
                    font-size: 18px;
                }}
                button:hover {{ background: #ff5252; }}
                .now-playing {{ 
                    background: rgba(255,255,255,0.1); 
                    padding: 20px; 
                    border-radius: 10px; 
                    margin-bottom: 30px; 
                }}
            </style>
        </head>
        <body>
            <div class="now-playing">
                <h1>Music Player Controls</h1>
                <h2>{self.current_song_data['title']}</h2>
                <h3>{self.current_song_data['artist']}</h3>
                <p>Status: {self.current_song_data['status']}</p>
            </div>
            <div class="controls">
                <button onclick="alert('Template not found - controls not functional')">⏮ Previous</button>
                <button onclick="alert('Template not found - controls not functional')">⏹ Stop</button>
                <button onclick="alert('Template not found - controls not functional')">⏸ Pause</button>
                <button onclick="alert('Template not found - controls not functional')">▶ Play</button>
                <button onclick="alert('Template not found - controls not functional')">⏭ Next</button>
            </div>
            <p style="margin-top: 40px; opacity: 0.7;">Controls template not found. Please ensure controls.html exists in web/templates/</p>
        </body>
        </html>
        """
    
    def _find_available_port(self, start_port: int = 8081) -> int:
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
        """Start the controls server in a separate thread."""
        if self.is_running:
            logger.warning("Controls server is already running")
            return True
        
        try:
            # Try to find an available port if the default is taken
            try:
                self.port = self._find_available_port(self.port)
            except RuntimeError as e:
                logger.error(f"Failed to find available port for controls server: {e}")
                return False
            
            # Start server in a separate thread
            self.server_thread = threading.Thread(
                target=self._run_server,
                daemon=True
            )
            self.server_thread.start()
            
            logger.info(f"Controls server starting on http://{self.host}:{self.port}")
            self.is_running = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to start controls server: {e}")
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
                logger.error(f"Controls server port {self.port} is already in use")
                # Try to find another port
                try:
                    new_port = self._find_available_port(self.port + 1)
                    logger.info(f"Trying alternative port for controls server: {new_port}")
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
                    logger.error(f"Failed to start controls server on alternative port: {retry_error}")
                    self.is_running = False
            else:
                logger.error(f"Network error starting controls server: {e}")
                self.is_running = False
        except Exception as e:
            logger.error(f"Unexpected controls server error: {e}")
            self.is_running = False
    
    def stop(self):
        """Stop the controls server."""
        if not self.is_running:
            return
        
        self.is_running = False
        logger.info("Controls server stopped")
    
    def update_song_data(self, title: str, artist: str, status: str = 'Stopped', is_playing: bool = False):
        """Update current song data and broadcast to all connected clients."""
        self.current_song_data = {
            'title': title,
            'artist': artist,
            'status': status,
            'is_playing': is_playing
        }
        
        # Broadcast update to all connected WebSocket clients
        if self.is_running:
            try:
                self.socketio.emit('song_update', self.current_song_data)
                logger.debug(f"Broadcasted controls song update: {title} by {artist} ({status})")
            except Exception as e:
                logger.error(f"Failed to broadcast controls song update: {e}")
    
    def set_control_callbacks(self, play_callback=None, pause_callback=None, stop_callback=None, 
                             next_callback=None, previous_callback=None):
        """Set callbacks for control actions from the web interface."""
        if play_callback:
            self._control_callbacks['play'] = play_callback
        if pause_callback:
            self._control_callbacks['pause'] = pause_callback
        if stop_callback:
            self._control_callbacks['stop'] = stop_callback
        if next_callback:
            self._control_callbacks['next'] = next_callback
        if previous_callback:
            self._control_callbacks['previous'] = previous_callback
        
        logger.debug(f"Controls server callbacks set: {list(self._control_callbacks.keys())}")
    
    def get_server_url(self) -> str:
        """Get the controls server URL."""
        return f"http://{self.host}:{self.port}"


# Factory function for creating controls server instance
def create_controls_server(host: str = '127.0.0.1', port: int = 8081, debug_mode: bool = False) -> ControlsServer:
    """Create and return a ControlsServer instance."""
    return ControlsServer(host, port, debug_mode)


if __name__ == '__main__':
    # For testing purposes
    server = create_controls_server()
    if server.start():
        print(f"Controls server running at {server.get_server_url()}")
        print("Press Ctrl+C to stop")
        try:
            # Keep the main thread alive
            import time
            while server.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            server.stop()
    else:
        print("Failed to start controls server")