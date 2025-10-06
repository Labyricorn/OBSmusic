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
from web.controls_server import ControlsServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MusicPlayerApp:
    """Main application class that coordinates all components."""
    
    def __init__(self, config_dir=None, web_port=8080, enable_gui=True, enable_web=True, debug_mode=False):
        """Initialize the music player application.
        
        Args:
            config_dir: Optional custom directory for configuration files
            web_port: Port for the web server
            enable_gui: Whether to enable GUI components
            enable_web: Whether to enable web server
            debug_mode: Whether debug mode is enabled
        """
        self.config_dir = Path(config_dir) if config_dir else project_root / "data"
        self.config_dir.mkdir(exist_ok=True)
        self.web_port = web_port
        self.enable_gui = enable_gui
        self.enable_web = enable_web
        self.debug_mode = debug_mode
        
        # Component references (will be initialized later)
        self.playlist_manager = None
        self.player_engine = None
        self.web_server = None
        self.controls_server = None
        self.gui = None
        
        # Threading
        self.web_thread = None
        self.player_update_thread = None
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
                self.web_server = WebServer(host='127.0.0.1', port=self.web_port, debug_mode=self.debug_mode)
                logger.info("Web server initialized")
                
                # Initialize controls server on next available port (still needed for serving the controls page)
                self.controls_server = ControlsServer(host='127.0.0.1', port=self.web_port + 1, debug_mode=self.debug_mode)
                logger.info("Controls server initialized")
                
                # Set up player engine callbacks for web updates
                self._setup_player_web_integration()
                
                # Set up web server callback for song ended events
                self.web_server.set_on_song_ended_callback(self._on_web_song_ended)
                
                # Set up controls integration on the main web server
                self._setup_controls_integration()
                
                # Initialize web display with current song data
                self._initialize_web_display()
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
        # Don't set callbacks here if GUI is enabled - instead enhance GUI callbacks
        if not self.enable_gui:
            # Only set callbacks if GUI is disabled (headless mode)
            def on_song_changed(song):
                """Handle song change events and update web display."""
                self._update_web_display_for_song(song)
            
            def on_state_changed(state):
                """Handle playback state changes and update web display."""
                self._update_web_display_for_state(state)
            
            # Set up callbacks for headless mode
            self.player_engine.set_on_song_changed(on_song_changed)
            self.player_engine.set_on_state_changed(on_state_changed)
            logger.info("Player-web integration callbacks set up for headless mode")
        else:
            logger.info("GUI enabled - web integration will be handled through GUI callbacks")
    
    def _update_web_display_for_song(self, song):
        """Update web display when song changes."""
        try:
            logger.info(f"Updating web display for song: {song.get_display_name() if song else 'None'}")
            if self.web_server and song:
                # Extract artwork URL if available
                artwork_url = None
                if song.artwork_path:
                    # Convert local artwork path to web-accessible URL
                    artwork_filename = os.path.basename(song.artwork_path)
                    # Check if artwork file exists in the expected location
                    artwork_full_path = os.path.join(self.config_dir, "artwork", artwork_filename)
                    if os.path.exists(artwork_full_path):
                        artwork_url = f"/static/artwork/{artwork_filename}"
                    else:
                        logger.warning(f"Artwork file not found: {artwork_full_path}")
                        # Try the original path as fallback
                        if os.path.exists(song.artwork_path):
                            artwork_url = f"/static/artwork/{artwork_filename}"
                        else:
                            # Use placeholder image
                            artwork_url = "/static/artwork/placeholder.jpg"
                else:
                    # No artwork path, use placeholder
                    artwork_url = "/static/artwork/placeholder.jpg"
                
                # Generate audio URL for web playback
                audio_url = None
                if song.file_path and os.path.exists(song.file_path):
                    import base64
                    # Encode the file path as base64 for the URL
                    encoded_path = base64.b64encode(song.file_path.encode()).decode()
                    audio_url = f"/api/audio/{encoded_path}"
                
                # Update web display
                status = self._get_status_string(self.player_engine.get_state())
                self.web_server.update_song_data(
                    title=song.title,
                    artist=song.artist,
                    artwork_url=artwork_url,
                    is_playing=self.player_engine.is_playing(),
                    status=status,
                    audio_url=audio_url
                )
                logger.debug(f"Updated web display: {song.get_display_name()}")
                
        except Exception as e:
            logger.error(f"Error updating web display on song change: {e}")
    
    def _update_web_display_for_state(self, state):
        """Update web display when playback state changes."""
        try:
            if self.web_server:
                status = self._get_status_string(state)
                current_song = self.player_engine.get_current_song()
                if current_song:
                    # Generate audio URL for current song
                    audio_url = None
                    if current_song.file_path and os.path.exists(current_song.file_path):
                        import base64
                        encoded_path = base64.b64encode(current_song.file_path.encode()).decode()
                        audio_url = f"/api/audio/{encoded_path}"
                    
                    # Update playing state
                    self.web_server.update_song_data(
                        title=current_song.title,
                        artist=current_song.artist,
                        artwork_url=self.web_server.current_song_data.get('artwork_url'),
                        is_playing=self.player_engine.is_playing(),
                        status=status,
                        audio_url=audio_url
                    )
                else:
                    # No song playing
                    self.web_server.update_song_data(
                        title="No song playing",
                        artist="Music Player",
                        artwork_url="/static/artwork/placeholder.jpg",
                        is_playing=False,
                        status=status,
                        audio_url=None
                    )
                logger.debug(f"Updated web display state: {state.value}")
                
        except Exception as e:
            logger.error(f"Error updating web display on state change: {e}")
    
    def _setup_gui_web_integration(self):
        """Set up additional integration between GUI and web server."""
        # Enhance the GUI callbacks to also update the web display
        # Store references to the original GUI callbacks
        original_gui_song_callback = self.gui._on_song_changed
        original_gui_state_callback = self.gui._on_playback_state_changed
        
        def enhanced_song_callback(song):
            """Enhanced song callback that updates both GUI and web."""
            # Call original GUI callback
            original_gui_song_callback(song)
            # Also update web display
            self._update_web_display_for_song(song)

        
        def enhanced_state_callback(state):
            """Enhanced state callback that updates both GUI and web."""
            # Call original GUI callback
            original_gui_state_callback(state)
            # Also update web display
            self._update_web_display_for_state(state)

        
        # Replace the GUI callbacks with enhanced versions
        self.gui._on_song_changed = enhanced_song_callback
        self.gui._on_playback_state_changed = enhanced_state_callback
        
        # Re-set the callbacks on the player engine with the enhanced versions
        self.player_engine.set_on_song_changed(enhanced_song_callback)
        self.player_engine.set_on_state_changed(enhanced_state_callback)
        
        logger.info("Enhanced GUI callbacks with web integration")
        
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
                    artwork_url = "/static/artwork/placeholder.jpg"  # Default to placeholder
                    if current_song.artwork_path:
                        artwork_filename = os.path.basename(current_song.artwork_path)
                        # Check if artwork file exists in the expected location
                        artwork_full_path = os.path.join(self.config_dir, "artwork", artwork_filename)
                        if os.path.exists(artwork_full_path):
                            artwork_url = f"/static/artwork/{artwork_filename}"
                        elif os.path.exists(current_song.artwork_path):
                            artwork_url = f"/static/artwork/{artwork_filename}"
                    
                    # Generate audio URL for current song
                    audio_url = None
                    if current_song.file_path and os.path.exists(current_song.file_path):
                        import base64
                        encoded_path = base64.b64encode(current_song.file_path.encode()).decode()
                        audio_url = f"/api/audio/{encoded_path}"
                    
                    status = self._get_status_string(self.player_engine.get_state())
                    self.web_server.update_song_data(
                        title=current_song.title,
                        artist=current_song.artist,
                        artwork_url=artwork_url,
                        is_playing=self.player_engine.is_playing(),
                        status=status,
                        audio_url=audio_url
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
                # Also trigger web display update for the new current song
                if self.web_server and result:
                    artwork_url = "/static/artwork/placeholder.jpg"  # Default to placeholder
                    if result.artwork_path:
                        artwork_filename = os.path.basename(result.artwork_path)
                        artwork_full_path = os.path.join(self.config_dir, "artwork", artwork_filename)
                        if os.path.exists(artwork_full_path):
                            artwork_url = f"/static/artwork/{artwork_filename}"
                        elif os.path.exists(result.artwork_path):
                            artwork_url = f"/static/artwork/{artwork_filename}"
                    
                    # Generate audio URL for the selected song
                    audio_url = None
                    if result.file_path and os.path.exists(result.file_path):
                        import base64
                        encoded_path = base64.b64encode(result.file_path.encode()).decode()
                        audio_url = f"/api/audio/{encoded_path}"
                    
                    status = self._get_status_string(self.player_engine.get_state())
                    self.web_server.update_song_data(
                        title=result.title,
                        artist=result.artist,
                        artwork_url=artwork_url,
                        is_playing=self.player_engine.is_playing(),
                        status=status,
                        audio_url=audio_url
                    )
                    logger.info(f"Updated web display from playlist selection: {result.get_display_name()}")
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
    
    def _initialize_web_display(self):
        """Initialize web display with current song data from playlist."""
        try:
            if self.web_server and self.playlist_manager:
                current_song = self.playlist_manager.get_current_song()
                if current_song:
                    # Generate artwork URL for current song
                    artwork_url = "/static/artwork/placeholder.jpg"  # Default to placeholder
                    if current_song.artwork_path:
                        artwork_filename = os.path.basename(current_song.artwork_path)
                        # Check if artwork file exists in the expected location
                        artwork_full_path = os.path.join(self.config_dir, "artwork", artwork_filename)
                        if os.path.exists(artwork_full_path):
                            artwork_url = f"/static/artwork/{artwork_filename}"
                        elif os.path.exists(current_song.artwork_path):
                            artwork_url = f"/static/artwork/{artwork_filename}"
                    
                    # Generate audio URL for current song
                    audio_url = None
                    if current_song.file_path and os.path.exists(current_song.file_path):
                        import base64
                        encoded_path = base64.b64encode(current_song.file_path.encode()).decode()
                        audio_url = f"/api/audio/{encoded_path}"
                    
                    # Update web display with current song
                    status = self._get_status_string(self.player_engine.get_state())
                    self.web_server.update_song_data(
                        title=current_song.title,
                        artist=current_song.artist,
                        artwork_url=artwork_url,
                        is_playing=False,  # Not playing initially
                        status=status,
                        audio_url=audio_url
                    )
                    logger.info(f"Initialized web display with current song: {current_song.get_display_name()}")
                else:
                    # No current song, use default display
                    status = self._get_status_string(self.player_engine.get_state())
                    self.web_server.update_song_data(
                        title="No song playing",
                        artist="Music Player",
                        artwork_url="/static/artwork/placeholder.jpg",
                        is_playing=False,
                        status=status,
                        audio_url=None
                    )
                    logger.info("Initialized web display with default state (no current song)")
        except Exception as e:
            logger.error(f"Error initializing web display: {e}")
    
    def _get_status_string(self, state):
        """Convert PlaybackState enum to string for web display."""
        from core.player_engine import PlaybackState
        
        if state == PlaybackState.PLAYING:
            return "Playing"
        elif state == PlaybackState.PAUSED:
            return "Paused"
        elif state == PlaybackState.STOPPED:
            return "Stopped"
        elif state == PlaybackState.LOADING:
            return "Loading"
        else:
            return "Stopped"
    
    def _on_web_song_ended(self):
        """Handle when a song ends in the web audio player."""
        try:
            logger.info("Web audio player reported song ended")
            if self.player_engine:
                # Trigger playlist advancement without changing state first
                from core.player_engine import PlaybackState
                
                # Debug: Check auto-advance setting
                auto_advance_enabled = self.player_engine.is_auto_advance_enabled()
                logger.info(f"Auto-advance enabled: {auto_advance_enabled}")
                
                with self.player_engine._lock:
                    if self.player_engine.get_state() == PlaybackState.PLAYING:
                        # Set position to end of song
                        self.player_engine._position = self.player_engine._duration
                        
                        logger.info("Calling _handle_song_finished to advance to next song")
                        # Handle song finished (includes playlist advancement)
                        # This will advance to next song if auto-advance is enabled
                        self.player_engine._handle_song_finished()
                        
                        logger.info("Player engine synchronized with web audio song end")
                    else:
                        logger.warning(f"Song ended but player state is {self.player_engine.get_state()}, not PLAYING")
        except Exception as e:
            logger.error(f"Error handling web song ended: {e}")
    
    def _setup_controls_integration(self):
        """Set up integration between controls interface and player engine."""
        if self.web_server and self.player_engine:
            # Set up control callbacks on the main web server (since controls connect to main server)
            self.web_server.set_control_callbacks(
                play_callback=self._on_controls_play,
                pause_callback=self._on_controls_pause,
                stop_callback=self._on_controls_stop,
                next_callback=self._on_controls_next,
                previous_callback=self._on_controls_previous
            )
            logger.info("Controls integration callbacks set up on main web server")
    
    def _on_controls_play(self):
        """Handle play command from controls interface."""
        try:
            if self.player_engine.is_paused():
                # Resume playback
                self.player_engine.play()
            else:
                # Start playing current song or first song
                current_song = self.playlist_manager.get_current_song()
                if current_song:
                    self.player_engine.play_song(current_song)
                elif not self.playlist_manager.is_empty():
                    # Play first song
                    first_song = self.playlist_manager.set_current_song(0)
                    if first_song:
                        self.player_engine.play_song(first_song)
            logger.debug("Controls play command executed")
        except Exception as e:
            logger.error(f"Error executing controls play command: {e}")
    
    def _on_controls_pause(self):
        """Handle pause command from controls interface."""
        try:
            self.player_engine.pause()
            logger.debug("Controls pause command executed")
        except Exception as e:
            logger.error(f"Error executing controls pause command: {e}")
    
    def _on_controls_stop(self):
        """Handle stop command from controls interface."""
        try:
            self.player_engine.stop()
            logger.debug("Controls stop command executed")
        except Exception as e:
            logger.error(f"Error executing controls stop command: {e}")
    
    def _on_controls_next(self):
        """Handle next command from controls interface."""
        try:
            self.player_engine.next_song()
            logger.debug("Controls next command executed")
        except Exception as e:
            logger.error(f"Error executing controls next command: {e}")
    
    def _on_controls_previous(self):
        """Handle previous command from controls interface."""
        try:
            self.player_engine.previous_song()
            logger.debug("Controls previous command executed")
        except Exception as e:
            logger.error(f"Error executing controls previous command: {e}")
    
    def _update_player_playlist(self):
        """Update player engine with current playlist state."""
        if self.player_engine and self.playlist_manager:
            self.player_engine.set_playlist(self.playlist_manager.get_playlist())
    
    def _start_player_update_thread(self):
        """Start a background thread to regularly update the player engine."""
        def player_update_loop():
            """Background loop to update player engine for pygame event processing."""
            logger.info("Player update thread started")
            while self.running:
                try:
                    if self.player_engine:
                        self.player_engine.update()
                    time.sleep(0.1)  # Update every 100ms, same as GUI
                except Exception as e:
                    logger.error(f"Error in player update thread: {e}")
                    time.sleep(1)  # Wait longer on error to avoid spam
            logger.info("Player update thread stopped")
        
        if not self.player_update_thread or not self.player_update_thread.is_alive():
            self.player_update_thread = threading.Thread(target=player_update_loop, daemon=True)
            self.player_update_thread.start()
            logger.info("Started player update background thread")
    
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
    
    def start_controls_server(self):
        """Start the controls server in a separate thread."""
        if self.controls_server:
            success = self.controls_server.start()
            if success:
                logger.info(f"Controls server started on {self.controls_server.get_server_url()}")
                return True
            else:
                logger.error("Failed to start controls server")
                return False
        return False
    
    def run(self):
        """Start the application."""
        logger.info("Starting Music Player Application")
        
        if not self.initialize_components():
            logger.error("Failed to initialize application components")
            return 1
        
        self.running = True
        
        # Start player update thread (essential for pygame event processing)
        self._start_player_update_thread()
        
        # Start web server (if enabled)
        if self.enable_web:
            if not self.start_web_server():
                logger.warning("Web server failed to start, continuing without web interface")
            
            # Start controls server (if web is enabled)
            if not self.start_controls_server():
                logger.warning("Controls server failed to start, continuing without controls interface")
        
        try:
            print(f"Music Player Application started")
            if self.web_server and self.web_server.is_running:
                print(f"Web display available at: {self.web_server.get_server_url()}")
            if self.controls_server and self.controls_server.is_running:
                print(f"Web controls available at: {self.controls_server.get_server_url()}")
            
            if self.enable_gui:
                # Start GUI main loop
                logger.info("Starting GUI main loop")
                print("Use the GUI to manage your playlist and playback")
                
                # Run the GUI main loop (this will block until GUI is closed)
                # Let GUI handle player updates for more reliable event processing
                self.gui.run(skip_player_updates=False)
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
        
        # Stop controls server
        if self.controls_server:
            self.controls_server.stop()
            logger.info("Controls server stopped")
        
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
        enable_web=not args.no_web,
        debug_mode=args.debug
    )
    return app.run()


if __name__ == "__main__":
    sys.exit(main())