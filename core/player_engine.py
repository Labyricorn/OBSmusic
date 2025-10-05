"""
Audio playback engine using pygame.mixer for MP3 playback.
"""

import os
import threading
import time
import logging
from enum import Enum
from typing import Optional, Callable, TYPE_CHECKING
from pathlib import Path

try:
    import pygame
    import pygame.mixer
except ImportError as e:
    logging.error(f"Required dependency missing: {e}")
    raise

# Import playlist for type hints
if TYPE_CHECKING:
    from models.playlist import Playlist
    from models.song import Song

logger = logging.getLogger(__name__)


class PlaybackState(Enum):
    """Enumeration of possible playback states."""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    LOADING = "loading"


class PlayerEngine:
    """Audio playback engine for MP3 files using pygame.mixer."""
    
    def __init__(self, frequency: int = 44100, size: int = -16, channels: int = 2, buffer: int = 1024):
        """Initialize the player engine.
        
        Args:
            frequency: Audio frequency (default: 44100 Hz)
            size: Audio sample size (default: -16 bit signed)
            channels: Number of audio channels (default: 2 for stereo)
            buffer: Audio buffer size (default: 1024)
        """
        self._state = PlaybackState.STOPPED
        self._current_file = None
        self._volume = 0.7  # Default volume (0.0 to 1.0)
        self._position = 0.0  # Current position in seconds
        self._duration = 0.0  # Total duration in seconds
        
        # Playlist integration
        self._playlist = None
        self._current_song = None
        self._auto_advance = True  # Whether to automatically advance to next song
        
        # Threading
        self._lock = threading.RLock()
        self._position_thread = None
        self._position_thread_running = False
        
        # Event callbacks
        self._on_playback_finished = None
        self._on_playback_error = None
        self._on_state_changed = None
        self._on_song_changed = None
        
        # Initialize pygame mixer
        self._initialize_mixer(frequency, size, channels, buffer)
        
        logger.info("PlayerEngine initialized successfully")
    
    def _initialize_mixer(self, frequency: int, size: int, channels: int, buffer: int) -> None:
        """Initialize pygame mixer with specified parameters.
        
        Args:
            frequency: Audio frequency
            size: Audio sample size
            channels: Number of audio channels
            buffer: Audio buffer size
            
        Raises:
            RuntimeError: If mixer initialization fails
        """
        try:
            # Initialize pygame (required for event system)
            pygame.init()
            
            # Initialize pygame mixer
            pygame.mixer.pre_init(frequency=frequency, size=size, channels=channels, buffer=buffer)
            pygame.mixer.init()
            
            # Set up event handling for music end
            pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
            
            logger.debug(f"Pygame mixer initialized: {frequency}Hz, {size}bit, {channels}ch, buffer={buffer}")
            
        except Exception as e:
            error_msg = f"Failed to initialize pygame mixer: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def set_on_playback_finished(self, callback: Callable[[], None]) -> None:
        """Set callback for when playback finishes naturally.
        
        Args:
            callback: Function to call when playback finishes
        """
        self._on_playback_finished = callback
    
    def set_on_playback_error(self, callback: Callable[[str], None]) -> None:
        """Set callback for when playback encounters an error.
        
        Args:
            callback: Function to call with error message
        """
        self._on_playback_error = callback
    
    def set_on_state_changed(self, callback: Callable[[PlaybackState], None]) -> None:
        """Set callback for when playback state changes.
        
        Args:
            callback: Function to call with new state
        """
        self._on_state_changed = callback
    
    def set_on_song_changed(self, callback: Callable[['Song'], None]) -> None:
        """Set callback for when current song changes.
        
        Args:
            callback: Function to call with new Song
        """
        self._on_song_changed = callback
    
    # Playlist Integration Methods
    
    def set_playlist(self, playlist: 'Playlist') -> None:
        """Set the playlist for automatic song advancement.
        
        Args:
            playlist: Playlist instance to use
        """
        with self._lock:
            self._playlist = playlist
            logger.debug(f"Set playlist with {len(playlist)} songs")
    
    def get_playlist(self) -> Optional['Playlist']:
        """Get the current playlist.
        
        Returns:
            Current Playlist instance or None
        """
        return self._playlist
    
    def get_current_song(self) -> Optional['Song']:
        """Get the currently playing/loaded song.
        
        Returns:
            Current Song instance or None
        """
        return self._current_song
    
    def set_auto_advance(self, enabled: bool) -> None:
        """Enable or disable automatic advancement to next song.
        
        Args:
            enabled: Whether to automatically advance to next song
        """
        with self._lock:
            self._auto_advance = enabled
            logger.debug(f"Auto-advance {'enabled' if enabled else 'disabled'}")
    
    def is_auto_advance_enabled(self) -> bool:
        """Check if auto-advance is enabled.
        
        Returns:
            True if auto-advance is enabled, False otherwise
        """
        return self._auto_advance
    
    def play_song(self, song: 'Song') -> bool:
        """Play a specific song from the playlist.
        
        Args:
            song: Song instance to play
            
        Returns:
            True if playback started successfully, False otherwise
        """
        with self._lock:
            try:
                if not song.is_valid():
                    logger.warning(f"Cannot play invalid song: {song.get_display_name()}")
                    return False
                
                # Update current song
                old_song = self._current_song
                self._current_song = song
                
                # Update playlist current index if playlist is set
                if self._playlist:
                    try:
                        song_index = self._playlist.songs.index(song)
                        self._playlist.current_index = song_index
                    except ValueError:
                        logger.warning(f"Song not found in current playlist: {song.get_display_name()}")
                
                # Start playback
                success = self.play(song.file_path)
                
                if success and old_song != song:
                    self._notify_song_changed(song)
                
                return success
                
            except Exception as e:
                error_msg = f"Failed to play song {song.get_display_name()}: {e}"
                logger.error(error_msg)
                self._handle_error(error_msg)
                return False
    
    def next_song(self) -> bool:
        """Advance to the next song in the playlist.
        
        Returns:
            True if advanced successfully, False otherwise
        """
        with self._lock:
            if not self._playlist:
                logger.warning("No playlist set for next song")
                return False
            
            next_song = self._playlist.next_song()
            if next_song:
                return self.play_song(next_song)
            else:
                logger.debug("No next song available (end of playlist, loop disabled)")
                return False
    
    def previous_song(self) -> bool:
        """Go to the previous song in the playlist.
        
        Returns:
            True if went to previous successfully, False otherwise
        """
        with self._lock:
            if not self._playlist:
                logger.warning("No playlist set for previous song")
                return False
            
            previous_song = self._playlist.previous_song()
            if previous_song:
                return self.play_song(previous_song)
            else:
                logger.debug("No previous song available (beginning of playlist, loop disabled)")
                return False
    
    def play_current_playlist_song(self) -> bool:
        """Play the current song from the playlist.
        
        Returns:
            True if playback started successfully, False otherwise
        """
        with self._lock:
            if not self._playlist:
                logger.warning("No playlist set")
                return False
            
            current_song = self._playlist.get_current_song()
            if current_song:
                return self.play_song(current_song)
            else:
                logger.warning("No current song in playlist")
                return False
    
    def _notify_song_changed(self, song: 'Song') -> None:
        """Notify that the current song has changed.
        
        Args:
            song: New current song
        """
        if self._on_song_changed:
            try:
                self._on_song_changed(song)
            except Exception as e:
                logger.error(f"Error in song changed callback: {e}")
    
    def _handle_song_finished(self) -> None:
        """Handle when a song finishes playing."""
        with self._lock:
            if self._auto_advance and self._playlist:
                # Try to advance to next song
                if not self.next_song():
                    # No next song available, stop playback
                    logger.debug("End of playlist reached, stopping playback")
            
            # Call the original playback finished callback
            if self._on_playback_finished:
                try:
                    self._on_playback_finished()
                except Exception as e:
                    logger.error(f"Error in playback finished callback: {e}")
    
    def play(self, file_path: Optional[str] = None) -> bool:
        """Start playing an MP3 file or resume current playback.
        
        Args:
            file_path: Path to MP3 file to play (optional if resuming)
            
        Returns:
            True if playback started successfully, False otherwise
        """
        with self._lock:
            try:
                if file_path:
                    # Load new file
                    if not self._load_file(file_path):
                        return False
                elif self._state == PlaybackState.PAUSED:
                    # Resume paused playback
                    pygame.mixer.music.unpause()
                    self._set_state(PlaybackState.PLAYING)
                    self._start_position_tracking()
                    logger.debug("Resumed playback")
                    return True
                elif self._current_file:
                    # Restart current file
                    if not self._load_file(self._current_file):
                        return False
                else:
                    logger.warning("No file to play")
                    return False
                
                # Start playback
                pygame.mixer.music.play()
                self._set_state(PlaybackState.PLAYING)
                self._start_position_tracking()
                
                logger.info(f"Started playing: {Path(self._current_file).name}")
                return True
                
            except Exception as e:
                error_msg = f"Failed to start playback: {e}"
                logger.error(error_msg)
                self._handle_error(error_msg)
                return False
    
    def pause(self) -> bool:
        """Pause current playback.
        
        Returns:
            True if paused successfully, False otherwise
        """
        with self._lock:
            try:
                if self._state == PlaybackState.PLAYING:
                    pygame.mixer.music.pause()
                    self._set_state(PlaybackState.PAUSED)
                    self._stop_position_tracking()
                    logger.debug("Paused playback")
                    return True
                else:
                    logger.warning(f"Cannot pause from state: {self._state}")
                    return False
                    
            except Exception as e:
                error_msg = f"Failed to pause playback: {e}"
                logger.error(error_msg)
                self._handle_error(error_msg)
                return False
    
    def stop(self) -> bool:
        """Stop current playback and reset position.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        with self._lock:
            try:
                if self._state in [PlaybackState.PLAYING, PlaybackState.PAUSED]:
                    pygame.mixer.music.stop()
                    self._position = 0.0
                    self._set_state(PlaybackState.STOPPED)
                    self._stop_position_tracking()
                    logger.debug("Stopped playback")
                    return True
                else:
                    logger.debug(f"Already stopped (state: {self._state})")
                    return True
                    
            except Exception as e:
                error_msg = f"Failed to stop playback: {e}"
                logger.error(error_msg)
                self._handle_error(error_msg)
                return False
    
    def set_volume(self, volume: float) -> bool:
        """Set playback volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
            
        Returns:
            True if volume set successfully, False otherwise
        """
        try:
            # Clamp volume to valid range
            volume = max(0.0, min(1.0, volume))
            
            with self._lock:
                pygame.mixer.music.set_volume(volume)
                self._volume = volume
                
            logger.debug(f"Set volume to {volume:.2f}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to set volume: {e}"
            logger.error(error_msg)
            return False
    
    def get_volume(self) -> float:
        """Get current volume level.
        
        Returns:
            Current volume (0.0 to 1.0)
        """
        return self._volume
    
    def is_playing(self) -> bool:
        """Check if audio is currently playing.
        
        Returns:
            True if playing, False otherwise
        """
        return self._state == PlaybackState.PLAYING
    
    def is_paused(self) -> bool:
        """Check if audio is currently paused.
        
        Returns:
            True if paused, False otherwise
        """
        return self._state == PlaybackState.PAUSED
    
    def is_stopped(self) -> bool:
        """Check if audio is currently stopped.
        
        Returns:
            True if stopped, False otherwise
        """
        return self._state == PlaybackState.STOPPED
    
    def get_state(self) -> PlaybackState:
        """Get current playback state.
        
        Returns:
            Current PlaybackState
        """
        return self._state
    
    def get_position(self) -> float:
        """Get current playback position in seconds.
        
        Returns:
            Current position in seconds
        """
        return self._position
    
    def get_duration(self) -> float:
        """Get total duration of current file in seconds.
        
        Returns:
            Duration in seconds (0.0 if no file loaded)
        """
        return self._duration
    
    def get_current_file(self) -> Optional[str]:
        """Get path of currently loaded file.
        
        Returns:
            File path or None if no file loaded
        """
        return self._current_file
    
    def seek(self, position: float) -> bool:
        """Seek to specific position in current file.
        
        Note: pygame.mixer doesn't support seeking, so this will restart playback
        from the beginning. This is a limitation of the pygame library.
        
        Args:
            position: Position in seconds (currently ignored due to pygame limitation)
            
        Returns:
            False (seeking not supported by pygame.mixer)
        """
        logger.warning("Seeking not supported by pygame.mixer")
        return False
    
    def _load_file(self, file_path: str) -> bool:
        """Load an MP3 file for playback.
        
        Args:
            file_path: Path to the MP3 file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            self._set_state(PlaybackState.LOADING)
            
            # Load the file
            pygame.mixer.music.load(file_path)
            
            self._current_file = file_path
            self._position = 0.0
            
            # Try to get duration (pygame doesn't provide this directly)
            # We'll use mutagen if available, otherwise set to 0
            self._duration = self._get_file_duration(file_path)
            
            logger.debug(f"Loaded file: {Path(file_path).name} (duration: {self._duration:.1f}s)")
            return True
            
        except Exception as e:
            error_msg = f"Failed to load file {file_path}: {e}"
            logger.error(error_msg)
            self._handle_error(error_msg)
            return False
    
    def _get_file_duration(self, file_path: str) -> float:
        """Get duration of MP3 file using mutagen.
        
        Args:
            file_path: Path to the MP3 file
            
        Returns:
            Duration in seconds, or 0.0 if unable to determine
        """
        try:
            from mutagen import File as MutagenFile
            
            audio_file = MutagenFile(file_path)
            if audio_file and hasattr(audio_file, 'info') and audio_file.info:
                return getattr(audio_file.info, 'length', 0.0)
            
        except Exception as e:
            logger.debug(f"Could not get duration for {file_path}: {e}")
        
        return 0.0
    
    def _set_state(self, new_state: PlaybackState) -> None:
        """Set playback state and notify callback.
        
        Args:
            new_state: New playback state
        """
        if self._state != new_state:
            old_state = self._state
            self._state = new_state
            
            logger.debug(f"State changed: {old_state.value} -> {new_state.value}")
            
            if self._on_state_changed:
                try:
                    self._on_state_changed(new_state)
                except Exception as e:
                    logger.error(f"Error in state change callback: {e}")
    
    def _handle_error(self, error_message: str) -> None:
        """Handle playback error with graceful recovery.
        
        Args:
            error_message: Error description
        """
        self._set_state(PlaybackState.STOPPED)
        self._stop_position_tracking()
        
        logger.error(f"Playback error: {error_message}")
        
        # Try to skip to next song if auto-advance is enabled and we have a playlist
        if self._auto_advance and self._playlist and self._current_song:
            logger.info("Attempting to skip to next song due to playback error")
            try:
                # Mark current song as having an error to avoid infinite loops
                if hasattr(self._current_song, '_playback_error_count'):
                    self._current_song._playback_error_count += 1
                else:
                    self._current_song._playback_error_count = 1
                
                # If this song has failed too many times, don't try to play it again
                if self._current_song._playback_error_count >= 3:
                    logger.warning(f"Song has failed {self._current_song._playback_error_count} times, skipping: {self._current_song.get_display_name()}")
                    # Try to advance to next song
                    if self.next_song():
                        logger.info("Successfully skipped to next song after error")
                        return
                else:
                    # Try to play next song
                    if self.next_song():
                        logger.info("Successfully skipped to next song after error")
                        return
                        
            except Exception as skip_error:
                logger.error(f"Failed to skip to next song after error: {skip_error}")
        
        # Notify error callback
        if self._on_playback_error:
            try:
                self._on_playback_error(error_message)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")
    
    def _start_position_tracking(self) -> None:
        """Start position tracking thread."""
        if not self._position_thread_running:
            self._position_thread_running = True
            self._position_thread = threading.Thread(target=self._position_tracker, daemon=True)
            self._position_thread.start()
    
    def _stop_position_tracking(self) -> None:
        """Stop position tracking thread."""
        self._position_thread_running = False
        if self._position_thread and self._position_thread.is_alive():
            self._position_thread.join(timeout=1.0)
    
    def _position_tracker(self) -> None:
        """Track playback position in separate thread."""
        start_time = time.time()
        
        while self._position_thread_running and self._state == PlaybackState.PLAYING:
            try:
                # Check if music is still playing
                if not pygame.mixer.music.get_busy():
                    # Music finished
                    with self._lock:
                        if self._state == PlaybackState.PLAYING:
                            self._position = self._duration
                            self._set_state(PlaybackState.STOPPED)
                            
                            # Handle song finished (includes playlist advancement)
                            self._handle_song_finished()
                    break
                
                # Update position
                elapsed = time.time() - start_time
                with self._lock:
                    self._position = min(elapsed, self._duration)
                
                time.sleep(0.1)  # Update every 100ms
                
            except Exception as e:
                logger.error(f"Error in position tracker: {e}")
                break
        
        self._position_thread_running = False
    
    def update(self) -> None:
        """Update the player engine (process pygame events).
        
        This should be called regularly from the main thread to process
        pygame events, especially the music end event.
        """
        try:
            # Process pygame events
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:  # Music end event
                    with self._lock:
                        if self._state == PlaybackState.PLAYING:
                            self._position = self._duration
                            self._set_state(PlaybackState.STOPPED)
                            
                            # Handle song finished (includes playlist advancement)
                            self._handle_song_finished()
        
        except Exception as e:
            logger.error(f"Error in player update: {e}")
    
    def shutdown(self) -> None:
        """Shutdown the player engine and cleanup resources."""
        logger.info("Shutting down PlayerEngine")
        
        with self._lock:
            # Stop playback
            self.stop()
            
            # Stop position tracking
            self._stop_position_tracking()
            
            # Cleanup pygame
            try:
                pygame.mixer.quit()
            except Exception as e:
                logger.error(f"Error during pygame cleanup: {e}")
        
        logger.info("PlayerEngine shutdown complete")
    
    def get_info(self) -> dict:
        """Get comprehensive player information.
        
        Returns:
            Dictionary with player state information
        """
        playlist_info = None
        if self._playlist:
            playlist_info = {
                'total_songs': len(self._playlist),
                'current_index': self._playlist.current_index,
                'loop_enabled': self._playlist.loop_enabled
            }
        
        current_song_info = None
        if self._current_song:
            current_song_info = {
                'title': self._current_song.title,
                'artist': self._current_song.artist,
                'album': self._current_song.album,
                'display_name': self._current_song.get_display_name()
            }
        
        return {
            'state': self._state.value,
            'current_file': self._current_file,
            'position': self._position,
            'duration': self._duration,
            'volume': self._volume,
            'is_playing': self.is_playing(),
            'is_paused': self.is_paused(),
            'is_stopped': self.is_stopped(),
            'auto_advance': self._auto_advance,
            'playlist': playlist_info,
            'current_song': current_song_info
        }
    
    def __str__(self) -> str:
        """String representation of the player."""
        if self._current_file:
            filename = Path(self._current_file).name
            return f"PlayerEngine({self._state.value}, {filename}, {self._position:.1f}s/{self._duration:.1f}s)"
        else:
            return f"PlayerEngine({self._state.value}, no file loaded)"
    
    def __repr__(self) -> str:
        """Developer representation of the player."""
        return f"PlayerEngine(state={self._state}, file='{self._current_file}', pos={self._position:.1f})"