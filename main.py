#!/usr/bin/env python3
"""
Music Player Application
A Python-based music player with playlist management and OBS integration.
"""

import sys
import os
import threading
import argparse
import logging
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import application components
from core.playlist_manager import PlaylistManager
from core.player_engine import PlayerEngine
from gui.main_window import MainWindow
from web.server import WebServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MusicPlayerApp:
    """Main application class that coordinates all components."""
    
    def __init__(self, config_dir=None, web_port=8080, enable_gui=True, enable_web=True):
        """Initialize the music player application.
        
        Args:
            config_dir: Optional custom directory for configuration files
            web_port: Port for the web server
            enable_gui: Whether to enable GUI components
            enable_web: Whether to enable web server
        """
        self.config_dir = Path(config_dir) if config_dir else project_root / "data"
        self.config_dir.mkdir(exist_ok=True)
        self.web_port = web_port
        self.enable_gui = enable_gui
        self.enable_web = enable_web
        
        # Component references (will be initialized later)
        self.playlist_manager = None
        self.player_engine = None
        self.web_server = None
        self.gui = None
        
        # Threading
        self.web_thread = None
        self.running = False
        
        logger.info(f"Music Player initialized with config dir: {self.config_dir}")
        logger.info(f"GUI enabled: {self.enable_gui}, Web enabled: {self.enable_web}")
    
    def initialize_components(self):
        """Initialize all application components and connect them."""
        try:
            logger.info("Initializing application components...")
            
            # Initialize playlist manager (always needed)
            playlist_file = str(self.config_dir / "playlist.json")
            artwork_dir = str(self.config_dir / "artwork")
            self.playlist_manager = PlaylistManager(playlist_file, artwork_dir)
            logger.info("Playlist manager initialized")
            
            # Initialize player engine (always needed)
            self.player_engine = PlayerEngine()
            logger.info("Player engine initialized")
            
            # Connect player engine with playlist manager
            self.player_engine.set_playlist(self.playlist_manager.get_playlist())
            logger.info("Player engine connected to playlist")
            
            # Initialize web server (if enabled)
            if self.enable_web:
                self.web_server = WebServer(host='127.0.0.1', port=self.web_port)
                logger.info("Web server initialized")
                
                # Set up player engine callbacks for web updates
                self._setup_player_web_integration()
            else:
                logger.info("Web server disabled")
            
            # Initialize GUI (if enabled)
            if self.enable_gui:
                self.gui = MainWindow(self.playlist_manager, self.player_engine)
                logger.info("GUI initialized")
                
                # Set up additional GUI callbacks for web updates (if web is enabled)
                if self.enable_web:
                    self._setup_gui_web_integration()
            else:
                logger.info("GUI disabled")
            
            # Validate configuration
            if not self.enable_gui and not self.enable_web:
                logger.error("Both GUI and web server are disabled - application would have no interface")
                return False
            
            logger.info("All enabled components initialized and integrated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            return False
    
    def _setup_player_web_integration(self):
        """Set up integration between player engine and web server for real-time updates."""
        def on_song_changed(song):
            """Handle song change events and update web display."""
            try:
                if self.web_server and song:
                    # Extract artwork URL if available
                    artwork_url = None
                    if song.artwork_path and os.path.exists(song.artwork_path):
                        # Convert local artwork path to web-accessible URL
                        artwork_filename = os.path.basename(song.artwork_path)
                        artwork_url = f"/static/artwork/{artwork_filename}"
                    
                    # Update web display
                    self.web_server.update_song_data(
                        title=song.title,
                        artist=song.artist,
                        artwork_url=artwork_url,
                        is_playing=self.player_engine.is_playing()
                    )
                    logger.debug(f"Updated web display: {song.get_display_name()}")
                    
            except Exception as e:
                logger.error(f"Error updating web display on song change: {e}")
        
        def on_state_changed(state):
            """Handle playback state changes and update web display."""
            try:
                if self.web_server:
                    current_song = self.player_engine.get_current_song()
                    if current_song:
                        # Update playing state
                        self.web_server.update_song_data(
                            title=current_song.title,
                            artist=current_song.artist,
                            artwork_url=self.web_server.current_song_data.get('artwork_url'),
                            is_playing=self.player_engine.is_playing()
                        )
                    else:
                        # No song playing
                        self.web_server.update_song_data(
                            title="No song playing",
                            artist="Music Player",
                            artwork_url=None,
                            is_playing=False
                        )
                    logger.debug(f"Updated web display state: {state.value}")
                    
            except Exception as e:
                logger.error(f"Error updating web display on state change: {e}")
        
        # Set up callbacks
        self.player_engine.set_on_song_changed(on_song_changed)
        self.player_engine.set_on_state_changed(on_state_changed)
        
        logger.info("Player-web integration callbacks set up")
    
    def _setup_gui_web_integration(self):
        """Set up additional integration between GUI and web server."""
        # The GUI already has callbacks set up with the player engine,
        # so web updates will happen automatically through the player callbacks.
        
        # Override playlist manager methods to ensure player engine stays synchronized
        original_add_song = self.playlist_manager.add_song
        original_remove_song = self.playlist_manager.remove_song
        original_reorder_songs = self.playlist_manager.reorder_songs
        original_set_current_song = self.playlist_manager.set_current_song
        original_set_loop_enabled = self.playlist_manager.set_loop_enabled
        
        def synchronized_add_song(*args, **kwargs):
            result = original_add_song(*args, **kwargs)
            if result:
                self._update_player_playlist()
                # Update web display if this is the first song or current song
                current_song = self.playlist_manager.get_current_song()
                if current_song and self.web_server:
                    artwork_url = None
                    if current_song.artwork_path and os.path.exists(current_song.artwork_path):
                        artwork_filename = os.path.basename(current_song.artwork_path)
                        artwork_url = f"/static/artwork/{artwork_filename}"
                    
                    self.web_server.update_song_data(
                        title=current_song.title,
                        artist=current_song.artist,
                        artwork_url=artwork_url,
                        is_playing=self.player_engine.is_playing()
                    )
            return result
        
        def synchronized_remove_song(*args, **kwargs):
            result = original_remove_song(*args, **kwargs)
            if result:
                self._update_player_playlist()
            return result
        
        def synchronized_reorder_songs(*args, **kwargs):
            result = original_reorder_songs(*args, **kwargs)
            if result:
                self._update_player_playlist()
            return result
        
        def synchronized_set_current_song(*args, **kwargs):
            result = original_set_current_song(*args, **kwargs)
            if result:
                self._update_player_playlist()
            return result
        
        def synchronized_set_loop_enabled(*args, **kwargs):
            original_set_loop_enabled(*args, **kwargs)
            self._update_player_playlist()
        
        # Replace methods with synchronized versions
        self.playlist_manager.add_song = synchronized_add_song
        self.playlist_manager.remove_song = synchronized_remove_song
        self.playlist_manager.reorder_songs = synchronized_reorder_songs
        self.playlist_manager.set_current_song = synchronized_set_current_song
        self.playlist_manager.set_loop_enabled = synchronized_set_loop_enabled
        
        logger.info("GUI-web integration with playlist synchronization set up")
    
    def _update_player_playlist(self):
        """Update player engine with current playlist state."""
        if self.player_engine and self.playlist_manager:
            self.player_engine.set_playlist(self.playlist_manager.get_playlist())
    
    def start_web_server(self):
        """Start the web server in a separate thread."""
        if self.web_server:
            success = self.web_server.start()
            if success:
                logger.info(f"Web server started on {self.web_server.get_server_url()}")
                return True
            else:
                logger.error("Failed to start web server")
                return False
        return False
    
    def run(self):
        """Start the application."""
        logger.info("Starting Music Player Application")
        
        if not self.initialize_components():
            logger.error("Failed to initialize application components")
            return 1
        
        self.running = True
        
        # Start web server (if enabled)
        if self.enable_web:
            if not self.start_web_server():
                logger.warning("Web server failed to start, continuing without web interface")
        
        try:
            print(f"Music Player Application started")
            if self.web_server and self.web_server.is_running:
                print(f"Web interface available at: {self.web_server.get_server_url()}")
            
            if self.enable_gui:
                # Start GUI main loop
                logger.info("Starting GUI main loop")
                print("Use the GUI to manage your playlist and playback")
                
                # Run the GUI main loop (this will block until GUI is closed)
                self.gui.run()
            else:
                # Headless mode - keep running until interrupted
                logger.info("Running in headless mode (web server only)")
                print("Running in headless mode. Web interface available for playlist management.")
                print("Press Ctrl+C to stop the application.")
                
                try:
                    while self.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("Application interrupted by user")
            
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Application error: {e}")
            return 1
        finally:
            self.shutdown()
        
        return 0
    
    def shutdown(self):
        """Gracefully shutdown the application."""
        logger.info("Shutting down Music Player Application")
        self.running = False
        
        # Stop player engine
        if self.player_engine:
            self.player_engine.stop()
            self.player_engine.shutdown()
            logger.info("Player engine stopped")
        
        # Stop web server
        if self.web_server:
            self.web_server.stop()
            logger.info("Web server stopped")
        
        # Save playlist
        if self.playlist_manager:
            self.playlist_manager.save_playlist()
            logger.info("Playlist saved")
        
        logger.info("Application shutdown complete")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Music Player with OBS Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Start with default settings
  %(prog)s --debug --port 9090      # Enable debug logging on port 9090
  %(prog)s --config-dir ./my_config # Use custom config directory
  %(prog)s --no-gui                 # Run in headless mode (web only)
  %(prog)s --no-web                 # Run without web server (GUI only)
        """
    )
    parser.add_argument(
        "--config-dir",
        type=str,
        help="Custom directory for configuration files (default: ./data)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Web server port (default: 8080)"
    )
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Run in headless mode without GUI (web server only)"
    )
    parser.add_argument(
        "--no-web",
        action="store_true",
        help="Run without web server (GUI only)"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Log file path (default: console only)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Music Player v1.0.0"
    )
    
    return parser.parse_args()


def main():
    """Application entry point."""
    args = parse_arguments()
    
    # Configure logging
    log_handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    log_handlers.append(console_handler)
    
    # File handler (if specified)
    if args.log_file:
        try:
            file_handler = logging.FileHandler(args.log_file)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            log_handlers.append(file_handler)
            print(f"Logging to file: {args.log_file}")
        except Exception as e:
            print(f"Warning: Could not create log file {args.log_file}: {e}")
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        handlers=log_handlers,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if args.debug:
        logger.debug("Debug logging enabled")
    
    # Validate arguments
    if args.no_gui and args.no_web:
        logger.error("Cannot disable both GUI and web server - application would have no interface")
        print("Error: Cannot use both --no-gui and --no-web options together")
        return 1
    
    # Create and run application
    app = MusicPlayerApp(
        config_dir=args.config_dir, 
        web_port=args.port,
        enable_gui=not args.no_gui,
        enable_web=not args.no_web
    )
    return app.run()


if __name__ == "__main__":
    sys.exit(main())