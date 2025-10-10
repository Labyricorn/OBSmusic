"""
Main window GUI for the music player application.

This module provides the desktop GUI interface with playlist display,
playback controls, and file management functionality.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
import webbrowser
from typing import Optional, List, Callable, Dict
from pathlib import Path

from models.song import Song
from models.playlist import Playlist
from core.playlist_manager import PlaylistManager
from core.player_engine import PlayerEngine, PlaybackState
from gui.theme import get_theme_manager, apply_modern_theme
from gui.hyperlink_config import HyperlinkConfig, DynamicHyperlinkManager
from gui.branding_config import get_branding_manager

logger = logging.getLogger(__name__)


class MainWindow:
    """Main window for the music player GUI."""
    
    def __init__(self, playlist_manager: PlaylistManager, player_engine: PlayerEngine):
        """Initialize the main window.
        
        Args:
            playlist_manager: PlaylistManager instance for playlist operations
            player_engine: PlayerEngine instance for playback control
        """
        self.playlist_manager = playlist_manager
        self.player_engine = player_engine
        
        # GUI components
        self.root = None
        self.playlist_widget = None
        self.current_song_label = None
        self.play_button = None
        self.pause_button = None
        self.stop_button = None
        self.next_button = None
        self.previous_button = None
        self.loop_var = None
        self.loop_checkbox = None
        
        # Theme manager
        self.theme_manager = get_theme_manager()
        
        # Branding manager
        self.branding_manager = get_branding_manager()
        
        # Dynamic hyperlink manager for web interface URLs
        self.hyperlink_manager = DynamicHyperlinkManager()
        self.hyperlink_widgets = {}  # Store hyperlink widgets for updates
        
        # Server references for dynamic URL updates
        self._web_server_ref = None
        self._controls_server_ref = None
        
        # State tracking
        self._updating_gui = False
        self._drag_start_index = None
        self._selected_index = None  # Track GUI selection separately from current song
        
        # Fade animation state for Now Playing display
        self._fade_after_id = None
        self._fade_alpha = 1.0
        
        # Set up player callbacks
        self._setup_player_callbacks()
        
        # Create the GUI
        self._create_gui()
        
        # Initial GUI update
        self._update_gui()
        
        logger.info("MainWindow initialized successfully")
    
    def _setup_player_callbacks(self) -> None:
        """Set up callbacks for player engine events."""
        self.player_engine.set_on_state_changed(self._on_playback_state_changed)
        self.player_engine.set_on_song_changed(self._on_song_changed)
        self.player_engine.set_on_playback_error(self._on_playback_error)
    
    def _create_gui(self) -> None:
        """Create the main GUI window and components."""
        # Create main window
        self.root = tk.Tk()
        
        # Apply branding (icon and title)
        branding_success = self.branding_manager.apply_window_branding(self.root)
        if not branding_success:
            logger.warning("Branding application failed, using fallback title")
            self.root.title("Music Player")  # Fallback title
        
        # Apply modern theme with compact sizing and error handling
        try:
            theme_applied = apply_modern_theme(self.root)
            if not theme_applied:
                logger.warning("Modern theme application failed, using fallback styling")
                self._apply_emergency_fallback_styling()
            else:
                logger.info("Modern theme applied successfully")
        except Exception as e:
            logger.error(f"Critical error applying modern theme: {e}")
            self._apply_emergency_fallback_styling()
        
        # Configure grid weights for responsive resizing
        # Row 0: Now Playing (fixed height)
        # Row 1: Playlist (expandable - gets extra space)
        # Row 2: Controls (fixed height)
        # Row 3: File Management (fixed height)
        # Row 4: Web Interface Hyperlinks (fixed height)
        self.root.grid_rowconfigure(1, weight=1)  # Playlist gets priority for extra space
        self.root.grid_columnconfigure(0, weight=1)
        
        # Set up window resize handler for responsive behavior
        self.root.bind("<Configure>", self._on_window_resize)
        
        # Create main components
        self._create_current_song_display()
        self._create_playlist_display()
        self._create_playback_controls()
        self._create_file_management()
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        logger.debug("GUI components created successfully")
    
    def _create_current_song_display(self) -> None:
        """Create the modern now playing display area with rounded corners and proper styling."""
        # Now Playing frame with modern styling and dark background
        self.now_playing_frame = self.theme_manager.create_now_playing_frame(
            self.root
        )
        self.now_playing_frame.grid(row=0, column=0, sticky="ew", 
                                   padx=self.theme_manager.theme.spacing_medium, 
                                   pady=self.theme_manager.theme.spacing_small)
        self.now_playing_frame.grid_columnconfigure(0, weight=1)
        self.now_playing_frame.grid_rowconfigure(0, weight=1)
        
        # Configure frame to maintain compact height (60px)
        self.now_playing_frame.grid_propagate(False)
        self.now_playing_frame.configure(height=self.theme_manager.theme.now_playing_height)
        
        # Inner container for proper padding and layout
        inner_frame = self.theme_manager.create_modern_frame(self.now_playing_frame)
        inner_frame.grid(row=0, column=0, sticky="nsew", 
                        padx=self.theme_manager.theme.spacing_medium,
                        pady=self.theme_manager.theme.spacing_small)
        inner_frame.grid_columnconfigure(0, weight=1)
        inner_frame.grid_rowconfigure(0, weight=1)
        inner_frame.grid_rowconfigure(1, weight=0)
        
        # Song title label with modern styling and text truncation support
        self.current_song_label = self.theme_manager.create_modern_label(
            inner_frame, 
            text="No song selected",
            style_type="now_playing"
        )
        self.current_song_label.grid(row=0, column=0, sticky="ew")
        
        # Artist/Album label for additional info (smaller, secondary text)
        self.current_artist_label = self.theme_manager.create_modern_label(
            inner_frame,
            text="",
            style_type="secondary"
        )
        self.current_artist_label.grid(row=1, column=0, sticky="ew")
    
    def _create_playlist_display(self) -> None:
        """Create the compact playlist display with modern aesthetics and drag-and-drop reordering."""
        # Playlist frame with modern styling
        playlist_frame = self.theme_manager.create_modern_frame(
            self.root, 
            padding=self.theme_manager.theme.spacing_small
        )
        playlist_frame.grid(row=1, column=0, sticky="nsew", 
                           padx=self.theme_manager.theme.spacing_medium, 
                           pady=self.theme_manager.theme.spacing_small)
        playlist_frame.grid_rowconfigure(0, weight=1)
        playlist_frame.grid_columnconfigure(0, weight=1)
        
        # Create modern playlist widget with alternating row colors and compact design
        self.playlist_widget = self.theme_manager.create_modern_playlist_widget(playlist_frame)
        self.playlist_widget.grid(row=0, column=0, sticky="nsew")
        
        # Set up callbacks for playlist interaction
        self.playlist_widget.set_selection_callback(self._on_playlist_selection_changed)
        self.playlist_widget.set_drag_drop_callback(self._on_playlist_reorder)
    
    def _create_playback_controls(self) -> None:
        """Create compact playback control buttons with modern flat design and hover effects."""
        # Controls frame with fixed height (30px)
        controls_frame = self.theme_manager.create_modern_frame(self.root)
        controls_frame.grid(row=2, column=0, sticky="ew", 
                           padx=self.theme_manager.theme.spacing_medium, 
                           pady=self.theme_manager.theme.spacing_small)
        controls_frame.grid_columnconfigure(5, weight=1)  # Loop checkbox column gets extra space
        
        # Configure frame to maintain compact height (30px)
        controls_frame.grid_propagate(False)
        controls_frame.configure(height=self.theme_manager.theme.controls_height)
        
        # Create modern control buttons (24x24px with 4px spacing)
        # Using specialized control button styling for better visual feedback
        
        self.previous_button = self.theme_manager.create_modern_control_button(
            controls_frame, 
            text="⏮",
            command=self._on_previous_clicked
        )
        self.previous_button.grid(row=0, column=0, padx=self.theme_manager.theme.spacing_small)
        
        self.play_button = self.theme_manager.create_modern_control_button(
            controls_frame, 
            text="▶",
            command=self._on_play_clicked
        )
        self.play_button.grid(row=0, column=1, padx=self.theme_manager.theme.spacing_small)
        
        self.pause_button = self.theme_manager.create_modern_control_button(
            controls_frame, 
            text="⏸",
            command=self._on_pause_clicked
        )
        self.pause_button.grid(row=0, column=2, padx=self.theme_manager.theme.spacing_small)
        
        self.stop_button = self.theme_manager.create_modern_control_button(
            controls_frame, 
            text="⏹",
            command=self._on_stop_clicked
        )
        self.stop_button.grid(row=0, column=3, padx=self.theme_manager.theme.spacing_small)
        
        self.next_button = self.theme_manager.create_modern_control_button(
            controls_frame, 
            text="⏭",
            command=self._on_next_clicked
        )
        self.next_button.grid(row=0, column=4, padx=self.theme_manager.theme.spacing_small)
        
        # Compact loop checkbox with modern styling
        self.loop_var = tk.BooleanVar()
        self.loop_var.set(self.playlist_manager.is_loop_enabled())
        self.loop_checkbox = self.theme_manager.create_modern_checkbutton(
            controls_frame,
            text="Loop",
            variable=self.loop_var,
            command=self._on_loop_toggled
        )
        self.loop_checkbox.grid(row=0, column=5, padx=(self.theme_manager.theme.spacing_large, 0), sticky="e")
    
    def _create_file_management(self) -> None:
        """Create compact file management panel with modern flat button design and hover effects."""
        # File management frame with fixed height (30px)
        file_frame = self.theme_manager.create_modern_frame(self.root)
        file_frame.grid(row=3, column=0, sticky="ew", 
                       padx=self.theme_manager.theme.spacing_medium, 
                       pady=self.theme_manager.theme.spacing_small)
        
        # Configure frame to maintain compact height
        file_frame.grid_propagate(False)
        file_frame.configure(height=self.theme_manager.theme.file_panel_height)
        
        # Create compact file management buttons (80x24px) with modern flat design
        # Using specialized file management button styling for better visual feedback
        
        # Add songs button
        add_button = self.theme_manager.create_modern_file_button(
            file_frame,
            text="Add Songs",
            command=self._on_add_songs_clicked
        )
        add_button.grid(row=0, column=0, padx=self.theme_manager.theme.spacing_small)
        
        # Remove song button
        remove_button = self.theme_manager.create_modern_file_button(
            file_frame,
            text="Remove",
            command=self._on_remove_song_clicked
        )
        remove_button.grid(row=0, column=1, padx=self.theme_manager.theme.spacing_small)
        
        # Clear playlist button
        clear_button = self.theme_manager.create_modern_file_button(
            file_frame,
            text="Clear",
            command=self._on_clear_playlist_clicked
        )
        clear_button.grid(row=0, column=2, padx=self.theme_manager.theme.spacing_small)
        
        # Save playlist button
        save_button = self.theme_manager.create_modern_file_button(
            file_frame,
            text="Save",
            command=self._on_save_playlist_clicked
        )
        save_button.grid(row=0, column=3, padx=self.theme_manager.theme.spacing_small)
        
        # Create web interface hyperlinks on a separate row at the bottom
        # Pass None for server objects initially - they will be set later via set_server_instances
        self._create_web_interface_hyperlinks()
    
    def _create_web_interface_hyperlinks(self, web_server=None, controls_server=None) -> None:
        """Create hyperlinked text elements for web interface access with dynamic URLs.
        
        Args:
            web_server: WebServer instance for port detection (optional)
            controls_server: ControlsServer instance for port detection (optional)
        """
        # Create a separate frame for web interface hyperlinks at the bottom
        web_links_frame = self.theme_manager.create_modern_frame(self.root)
        web_links_frame.grid(row=4, column=0, sticky="ew", 
                            padx=self.theme_manager.theme.spacing_medium, 
                            pady=self.theme_manager.theme.spacing_small)
        
        # Configure grid to center the hyperlinks
        web_links_frame.grid_columnconfigure(0, weight=1)
        web_links_frame.grid_columnconfigure(1, weight=0)
        web_links_frame.grid_columnconfigure(2, weight=0)
        web_links_frame.grid_columnconfigure(3, weight=1)
        
        # Store server references for future URL updates
        self._web_server_ref = web_server
        self._controls_server_ref = controls_server
        
        # Update hyperlink manager with server instances if provided
        if web_server or controls_server:
            self.hyperlink_manager.update_from_servers(web_server, controls_server)
            logger.debug("Updated hyperlink manager with provided server instances")
        
        # Get current URLs from hyperlink manager
        current_urls = self.hyperlink_manager.get_current_urls()
        
        # Web Display hyperlink - use dynamic URL
        web_display_url = current_urls['display']
        self.web_display_link = self.theme_manager.create_modern_hyperlink(
            web_links_frame,
            text=web_display_url,
            url=web_display_url
        )
        self.web_display_link.grid(row=0, column=1, padx=self.theme_manager.theme.spacing_medium, sticky="w")
        
        # Bind click events for web display link with dynamic URL handling
        self.web_display_link.bind("<Button-1>", lambda e: self._on_hyperlink_left_click_dynamic('display'))
        self.web_display_link.bind("<Button-3>", lambda e: self._on_hyperlink_right_click_dynamic(e, 'display'))
        
        # Web Controls hyperlink - use dynamic URL
        web_controls_url = current_urls['controls']
        self.web_controls_link = self.theme_manager.create_modern_hyperlink(
            web_links_frame,
            text=web_controls_url,
            url=web_controls_url
        )
        self.web_controls_link.grid(row=0, column=2, padx=self.theme_manager.theme.spacing_medium, sticky="w")
        
        # Bind click events for web controls link with dynamic URL handling
        self.web_controls_link.bind("<Button-1>", lambda e: self._on_hyperlink_left_click_dynamic('controls'))
        self.web_controls_link.bind("<Button-3>", lambda e: self._on_hyperlink_right_click_dynamic(e, 'controls'))
        
        # Store hyperlink widgets for future updates
        self.hyperlink_widgets = {
            'display': self.web_display_link,
            'controls': self.web_controls_link
        }
        
        logger.debug(f"Created dynamic hyperlinks - Display: {web_display_url}, Controls: {web_controls_url}")
    
    # Event Handlers
    
    def _on_window_resize(self, event) -> None:
        """Handle window resize events for responsive behavior."""
        # Only handle resize events for the root window
        if event.widget != self.root:
            return
            
        # Get current window size
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # Ensure minimum size constraints
        min_width = self.theme_manager.theme.window_min_width
        min_height = self.theme_manager.theme.window_min_height
        
        if width < min_width or height < min_height:
            # Enforce minimum size
            new_width = max(width, min_width)
            new_height = max(height, min_height)
            self.root.geometry(f"{new_width}x{new_height}")
            return
        
        # Calculate available space for playlist (responsive behavior)
        # Total height minus fixed components and their padding/margins
        fixed_height = (
            self.theme_manager.theme.now_playing_height +
            self.theme_manager.theme.controls_height +
            self.theme_manager.theme.file_panel_height +
            30 +  # Web links frame height (estimated)
            (self.theme_manager.theme.spacing_small * 10)  # Padding and margins for all components
        )
        
        playlist_height = max(100, height - fixed_height)  # Minimum 100px for playlist
        
        # Apply responsive scaling to components
        self._apply_responsive_scaling(width, height, playlist_height)
        
        logger.debug(f"Window resized to {width}x{height}, playlist area: {playlist_height}px")
    
    def _apply_responsive_scaling(self, width: int, height: int, playlist_height: int) -> None:
        """Apply responsive scaling to GUI components based on window size.
        
        Args:
            width: Current window width
            height: Current window height
            playlist_height: Available height for playlist area
        """
        try:
            # Update playlist widget to handle new dimensions
            if hasattr(self, 'playlist_widget') and self.playlist_widget:
                self.playlist_widget.handle_resize(width, playlist_height)
            
            # Update Now Playing display for text truncation based on new width
            if hasattr(self, 'current_song_label') and self.current_song_label:
                self._update_now_playing_text_truncation(width)
            
            # Ensure control panel maintains proper spacing at different widths
            self._adjust_control_panel_layout(width)
            
            # Update file management panel layout for smaller widths
            self._adjust_file_management_layout(width)
            
            # Update web links layout
            self._adjust_web_links_layout(width)
            
        except Exception as e:
            logger.warning(f"Error during responsive scaling: {e}")
    
    def _update_now_playing_text_truncation(self, window_width: int) -> None:
        """Update Now Playing text truncation based on window width.
        
        Args:
            window_width: Current window width
        """
        try:
            # Calculate available width for text (window width minus padding and margins)
            available_width = window_width - (self.theme_manager.theme.spacing_medium * 4)  # Left/right padding
            
            # Get current song info
            current_song = self.playlist_manager.get_current_song()
            if current_song:
                # Truncate song title to fit available width
                song_title = current_song.get_display_name()
                truncated_title = self.theme_manager.truncate_text(
                    song_title, 
                    available_width,
                    self.theme_manager.theme.get_font(
                        self.theme_manager.theme.font_size_body,
                        self.theme_manager.theme.font_weight_medium
                    )
                )
                self.current_song_label.configure(text=truncated_title)
                
                # Update artist/album info if available
                artist_info = ""
                if hasattr(current_song, 'artist') and current_song.artist:
                    artist_info = current_song.artist
                if hasattr(current_song, 'album') and current_song.album:
                    if artist_info:
                        artist_info += f" - {current_song.album}"
                    else:
                        artist_info = current_song.album
                
                if artist_info:
                    truncated_artist = self.theme_manager.truncate_text(
                        artist_info,
                        available_width,
                        self.theme_manager.theme.get_font(self.theme_manager.theme.font_size_small)
                    )
                    self.current_artist_label.configure(text=truncated_artist)
                    
        except Exception as e:
            logger.warning(f"Error updating Now Playing text truncation: {e}")
    
    def _adjust_control_panel_layout(self, window_width: int) -> None:
        """Adjust control panel layout for different window widths.
        
        Args:
            window_width: Current window width
        """
        try:
            # At minimum width, ensure buttons are still accessible
            if window_width <= self.theme_manager.theme.window_min_width:
                # Reduce spacing between control buttons at minimum width
                button_spacing = max(2, self.theme_manager.theme.spacing_small // 2)
            else:
                # Use normal spacing
                button_spacing = self.theme_manager.theme.spacing_small
            
            # Update button spacing if needed (this would require re-gridding)
            # For now, the grid weight system handles most of the responsive behavior
            
        except Exception as e:
            logger.warning(f"Error adjusting control panel layout: {e}")
    
    def _adjust_file_management_layout(self, window_width: int) -> None:
        """Adjust file management panel layout for different window widths.
        
        Args:
            window_width: Current window width
        """
        try:
            # At very small widths, we might need to adjust button sizes or layout
            # For now, the buttons maintain their fixed size as per design requirements
            # The grid system handles the overall layout responsiveness
            
            pass  # Current implementation relies on grid weights
            
        except Exception as e:
            logger.warning(f"Error adjusting file management layout: {e}")
    
    def _adjust_web_links_layout(self, window_width: int) -> None:
        """Adjust web links layout for different window widths.
        
        Args:
            window_width: Current window width
        """
        try:
            # At smaller widths, ensure hyperlinks don't overflow
            # The grid centering should handle most cases
            
            pass  # Current implementation relies on grid weights
            
        except Exception as e:
            logger.warning(f"Error adjusting web links layout: {e}")

    def _on_playlist_selection_changed(self, index: int) -> None:
        """Handle playlist selection change from the modern playlist widget.
        
        Args:
            index: Selected song index
        """
        self._selected_index = index
        logger.debug(f"Selected song at index {self._selected_index} (no playback change)")
    
    def _on_playlist_reorder(self, from_index: int, to_index: int) -> None:
        """Handle playlist reordering from drag-and-drop.
        
        Args:
            from_index: Source index
            to_index: Target index
        """
        # Perform reordering
        success = self.playlist_manager.reorder_songs(from_index, to_index)
        if success:
            self._update_playlist_display()
            # Update selected index to follow the moved item
            self._selected_index = to_index
            self.playlist_widget.set_selection(to_index)
            logger.debug(f"Reordered song from {from_index} to {to_index}")
    
    def _on_play_clicked(self) -> None:
        """Handle play button click."""
        if self.player_engine.is_paused():
            # Resume playback
            self.player_engine.play()
        else:
            # Determine which song to play
            song_to_play = None
            
            # If user has selected a song, play that song
            if self._selected_index is not None and 0 <= self._selected_index < self.playlist_manager.get_song_count():
                song_to_play = self.playlist_manager.set_current_song(self._selected_index)
                logger.debug(f"Playing selected song at index {self._selected_index}")
            else:
                # Fall back to current song or first song
                song_to_play = self.playlist_manager.get_current_song()
                if not song_to_play and not self.playlist_manager.is_empty():
                    # Play first song
                    song_to_play = self.playlist_manager.set_current_song(0)
                    logger.debug("Playing first song (no selection)")
            
            # Start playing the determined song
            if song_to_play:
                self.player_engine.play_song(song_to_play)
                logger.debug(f"Started playing: {song_to_play.get_display_name()}")
        
        # Trigger immediate web update after play button is pressed
        self._trigger_web_update()
    
    def _on_pause_clicked(self) -> None:
        """Handle pause button click."""
        self.player_engine.pause()
    
    def _on_stop_clicked(self) -> None:
        """Handle stop button click."""
        self.player_engine.stop()
    
    def _on_next_clicked(self) -> None:
        """Handle next button click."""
        self.player_engine.next_song()
    
    def _on_previous_clicked(self) -> None:
        """Handle previous button click."""
        self.player_engine.previous_song()
    

    
    def _on_loop_toggled(self) -> None:
        """Handle loop checkbox toggle."""
        enabled = self.loop_var.get()
        self.playlist_manager.set_loop_enabled(enabled)
        logger.debug(f"Loop {'enabled' if enabled else 'disabled'}")
    
    def _on_add_songs_clicked(self) -> None:
        """Handle add songs button click."""
        file_paths = filedialog.askopenfilenames(
            title="Select MP3 files",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")],
            parent=self.root
        )
        
        if file_paths:
            added_count = 0
            failed_count = 0
            
            for file_path in file_paths:
                try:
                    if self.playlist_manager.add_song(file_path):
                        added_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"Error adding song {file_path}: {e}")
                    failed_count += 1
            
            # Update display
            self._update_playlist_display()
            
            # Show result message
            if added_count > 0:
                message = f"Added {added_count} song(s) to playlist"
                if failed_count > 0:
                    message += f" ({failed_count} failed)"
                messagebox.showinfo("Songs Added", message, parent=self.root)
            elif failed_count > 0:
                messagebox.showerror("Error", f"Failed to add {failed_count} song(s)", parent=self.root)
    
    def _on_remove_song_clicked(self) -> None:
        """Handle remove song button click."""
        if self._selected_index is None:
            messagebox.showwarning("No Selection", "Please select a song to remove", parent=self.root)
            return
        
        index = self._selected_index
        song = self.playlist_manager.get_songs()[index]
        
        # Confirm removal
        result = messagebox.askyesno(
            "Confirm Removal",
            f"Remove '{song.get_display_name()}' from playlist?",
            parent=self.root
        )
        
        if result:
            success = self.playlist_manager.remove_song(index)
            if success:
                # Update selected index after removal
                if self._selected_index == index:
                    # If we removed the selected song, clear selection
                    self._selected_index = None
                elif self._selected_index is not None and self._selected_index > index:
                    # If selected song was after the removed song, adjust index
                    self._selected_index -= 1
                
                self._update_playlist_display()
                logger.debug(f"Removed song: {song.get_display_name()}")
            else:
                messagebox.showerror("Error", "Failed to remove song", parent=self.root)
    
    def _on_clear_playlist_clicked(self) -> None:
        """Handle clear playlist button click."""
        if self.playlist_manager.is_empty():
            messagebox.showinfo("Empty Playlist", "Playlist is already empty", parent=self.root)
            return
        
        # Confirm clearing
        result = messagebox.askyesno(
            "Confirm Clear",
            "Remove all songs from playlist?",
            parent=self.root
        )
        
        if result:
            self.playlist_manager.clear_playlist()
            self._selected_index = None  # Clear selection when playlist is cleared
            self._update_playlist_display()
            self._update_current_song_display()
            logger.debug("Cleared playlist")
    
    def _on_save_playlist_clicked(self) -> None:
        """Handle save playlist button click."""
        success = self.playlist_manager.save_playlist()
        if success:
            messagebox.showinfo("Playlist Saved", "Playlist saved successfully", parent=self.root)
        else:
            messagebox.showerror("Save Error", "Failed to save playlist", parent=self.root)
    
    def _on_open_web_interface_clicked(self) -> None:
        """Handle web interface button click - opens the HTML display page in browser."""
        try:
            # Default web server URL
            web_url = "http://127.0.0.1:8080"
            
            # Open the web display page in the default browser
            webbrowser.open(web_url)
            logger.info(f"Opened web interface: {web_url}")
            
        except Exception as e:
            logger.error(f"Failed to open web interface: {e}")
            messagebox.showerror(
                "Browser Error", 
                f"Failed to open web interface in browser.\n\nPlease manually navigate to:\nhttp://127.0.0.1:8080",
                parent=self.root
            )
    
    def _on_open_web_controls_clicked(self) -> None:
        """Handle web controls button click - opens the controls page in browser."""
        try:
            # Default controls server URL
            controls_url = "http://127.0.0.1:8081"
            
            # Open the web controls page in the default browser
            webbrowser.open(controls_url)
            logger.info(f"Opened web controls: {controls_url}")
            
        except Exception as e:
            logger.error(f"Failed to open web controls: {e}")
            messagebox.showerror(
                "Browser Error", 
                f"Failed to open web controls in browser.\n\nPlease manually navigate to:\nhttp://127.0.0.1:8081",
                parent=self.root
            )
    
    def _on_hyperlink_left_click(self, url: str) -> None:
        """Handle left-click on hyperlink to open URL in browser with comprehensive error handling.
        
        Args:
            url: URL to open in browser
        """
        logger.debug(f"Attempting to open URL in browser: {url}")
        
        try:
            # Try to open URL in default browser
            webbrowser.open(url)
            logger.info(f"Successfully opened hyperlink: {url}")
        except Exception as e:
            logger.error(f"Failed to open hyperlink {url} in default browser: {e}")
            
            # Try alternative browser opening methods
            fallback_success = False
            
            # Try different webbrowser methods
            try:
                webbrowser.open_new(url)
                logger.info(f"Successfully opened hyperlink using open_new: {url}")
                fallback_success = True
            except Exception as e2:
                logger.warning(f"Failed to open hyperlink using open_new: {e2}")
                
                try:
                    webbrowser.open_new_tab(url)
                    logger.info(f"Successfully opened hyperlink using open_new_tab: {url}")
                    fallback_success = True
                except Exception as e3:
                    logger.warning(f"Failed to open hyperlink using open_new_tab: {e3}")
            
            # If all browser methods failed, show enhanced error dialog with manual instructions
            if not fallback_success:
                logger.error(f"All browser opening methods failed for URL: {url}")
                
                # First show error dialog as expected by tests
                try:
                    messagebox.showerror(
                        "Browser Launch Failed",
                        f"Failed to open URL in browser automatically.\n\n"
                        f"URL: {url}\n\n"
                        f"Please copy the URL manually and paste it into your browser.",
                        parent=self.root
                    )
                except Exception as error_dialog_error:
                    logger.error(f"Failed to show error dialog: {error_dialog_error}")
                
                # Then offer enhanced functionality with copy option
                try:
                    result = messagebox.askyesno(
                        "Copy URL to Clipboard?", 
                        f"Would you like to copy the URL to clipboard for easy access?\n\n"
                        f"URL: {url}",
                        parent=self.root
                    )
                    
                    if result:
                        self._copy_url_to_clipboard(url)
                        messagebox.showinfo(
                            "URL Copied",
                            f"URL has been copied to clipboard.\n\n"
                            f"Please paste it into your browser manually:\n{url}",
                            parent=self.root
                        )
                except Exception as dialog_error:
                    logger.error(f"Failed to show clipboard dialog: {dialog_error}")
                    # Last resort: print to console
                    print(f"MANUAL URL ACCESS REQUIRED: {url}")
    
    def _on_hyperlink_right_click(self, event: tk.Event, url: str) -> None:
        """Handle right-click on hyperlink to show context menu with copy option.
        
        Args:
            event: Tkinter event object
            url: URL to copy to clipboard
        """
        logger.debug(f"Right-click on hyperlink: {url}")
        
        try:
            # Create context menu with error handling
            context_menu = tk.Menu(self.root, tearoff=0)
            
            # Add menu items with error handling
            try:
                context_menu.add_command(
                    label="Copy URL",
                    command=lambda: self._copy_url_to_clipboard(url)
                )
                context_menu.add_separator()
                context_menu.add_command(
                    label="Open in Browser",
                    command=lambda: self._on_hyperlink_left_click(url)
                )
                logger.debug("Context menu items added successfully")
            except Exception as e:
                logger.warning(f"Failed to add context menu items: {e}")
                # Add minimal menu items as fallback
                try:
                    context_menu.add_command(label="Copy URL", command=lambda: self._copy_url_to_clipboard(url))
                except Exception as e2:
                    logger.error(f"Failed to add fallback menu items: {e2}")
            
            # Show context menu at cursor position with error handling
            try:
                # Use post() method for compatibility with tests
                context_menu.post(event.x_root, event.y_root)
                logger.debug("Context menu displayed successfully")
            except Exception as e:
                logger.warning(f"Failed to show context menu at cursor position: {e}")
                # Try showing at a fixed position as fallback
                try:
                    context_menu.post(event.x_root, event.y_root + 10)
                except Exception as e2:
                    logger.error(f"Failed to show context menu at fallback position: {e2}")
                    # Last resort: show simple dialog
                    self._show_url_fallback_dialog(url)
            finally:
                try:
                    context_menu.grab_release()
                except Exception as e:
                    logger.warning(f"Failed to release context menu grab: {e}")
                    
        except Exception as e:
            logger.error(f"Critical error in right-click handler: {e}")
            # Fallback to simple dialog
            self._show_url_fallback_dialog(url)
    
    def _copy_url_to_clipboard(self, url: str) -> None:
        """Copy URL to system clipboard with comprehensive error handling.
        
        Args:
            url: URL to copy to clipboard
        """
        logger.debug(f"Attempting to copy URL to clipboard: {url}")
        
        try:
            # Try standard clipboard operations
            self.root.clipboard_clear()
            self.root.clipboard_append(url)
            self.root.update()  # Ensure clipboard is updated
            logger.info(f"Successfully copied URL to clipboard: {url}")
            
            # Show brief confirmation
            try:
                messagebox.showinfo(
                    "URL Copied",
                    f"URL copied to clipboard successfully!\n\n{url}",
                    parent=self.root
                )
            except Exception as e:
                logger.warning(f"Failed to show clipboard confirmation dialog: {e}")
            
        except Exception as e:
            logger.error(f"Failed to copy URL to clipboard: {e}")
            
            # Try alternative clipboard methods
            clipboard_success = False
            
            # Try using selection instead of clipboard
            try:
                self.root.selection_clear()
                self.root.selection_own()
                self.root.selection_handle(lambda offset, length: url)
                logger.info(f"URL copied to selection as fallback: {url}")
                clipboard_success = True
            except Exception as e2:
                logger.warning(f"Failed to copy to selection: {e2}")
            
            # Show error dialog with manual copy instructions
            try:
                if clipboard_success:
                    messagebox.showinfo(
                        "Clipboard Alternative",
                        f"URL copied using alternative method.\n\n"
                        f"If paste doesn't work, here's the URL to copy manually:\n\n{url}",
                        parent=self.root
                    )
                else:
                    # Show dialog with URL for manual copying
                    messagebox.showerror(
                        "Clipboard Error",
                        f"Failed to copy URL to clipboard automatically.\n\n"
                        f"Please manually copy this URL:\n\n{url}\n\n"
                        f"You can select and copy the URL from this dialog.",
                        parent=self.root
                    )
            except Exception as dialog_error:
                logger.error(f"Failed to show clipboard error dialog: {dialog_error}")
                # Last resort: print to console
                print(f"MANUAL COPY REQUIRED - URL: {url}")
    
    def _show_url_fallback_dialog(self, url: str) -> None:
        """Show a fallback dialog when context menu fails.
        
        Args:
            url: URL to display in fallback dialog
        """
        try:
            result = messagebox.askyesno(
                "URL Actions",
                f"URL: {url}\n\nChoose an action:\n\n"
                f"Yes - Copy to clipboard\n"
                f"No - Open in browser",
                parent=self.root
            )
            
            if result:
                self._copy_url_to_clipboard(url)
            else:
                self._on_hyperlink_left_click(url)
                
        except Exception as e:
            logger.error(f"Failed to show URL fallback dialog: {e}")
            # Last resort: print URL to console
            print(f"URL ACCESS: {url}")
    
    def _on_hyperlink_left_click_dynamic(self, link_type: str) -> None:
        """Handle left-click on dynamic hyperlink to open URL in browser.
        
        Args:
            link_type: Type of link ('display' or 'controls')
        """
        try:
            current_urls = self.hyperlink_manager.get_current_urls()
            url = current_urls.get(link_type)
            
            if url:
                self._on_hyperlink_left_click(url)
                logger.debug(f"Opened dynamic {link_type} hyperlink: {url}")
            else:
                logger.error(f"No URL found for link type: {link_type}")
                
        except Exception as e:
            logger.error(f"Error handling dynamic hyperlink click for {link_type}: {e}")
    
    def _on_hyperlink_right_click_dynamic(self, event: tk.Event, link_type: str) -> None:
        """Handle right-click on dynamic hyperlink to show context menu.
        
        Args:
            event: Tkinter event object
            link_type: Type of link ('display' or 'controls')
        """
        try:
            current_urls = self.hyperlink_manager.get_current_urls()
            url = current_urls.get(link_type)
            
            if url:
                self._on_hyperlink_right_click(event, url)
                logger.debug(f"Showed context menu for dynamic {link_type} hyperlink: {url}")
            else:
                logger.error(f"No URL found for link type: {link_type}")
                
        except Exception as e:
            logger.error(f"Error handling dynamic hyperlink right-click for {link_type}: {e}")
    
    def update_hyperlink_urls(self, web_server=None, controls_server=None) -> None:
        """Update hyperlink URLs based on current server ports.
        
        Args:
            web_server: WebServer instance for port detection (optional)
            controls_server: ControlsServer instance for port detection (optional)
        """
        try:
            # Update hyperlink manager with current server instances
            changed = self.hyperlink_manager.update_from_servers(web_server, controls_server)
            
            if changed and self.hyperlink_widgets:
                # Refresh hyperlink display with new URLs
                self.hyperlink_manager.refresh_hyperlink_display(self.hyperlink_widgets)
                logger.info("Hyperlink URLs updated successfully")
            else:
                logger.debug("Hyperlink URLs unchanged or no widgets to update")
                
        except Exception as e:
            logger.error(f"Error updating hyperlink URLs: {e}")
    
    def set_server_instances(self, web_server=None, controls_server=None) -> None:
        """Set server instances for dynamic hyperlink URL generation.
        
        Args:
            web_server: WebServer instance
            controls_server: ControlsServer instance
        """
        try:
            # Store server references for future URL updates
            self._web_server_ref = web_server
            self._controls_server_ref = controls_server
            
            # Update hyperlink URLs with server instances
            self.update_hyperlink_urls(web_server, controls_server)
            logger.debug("Server instances set for dynamic hyperlink generation")
            
        except Exception as e:
            logger.error(f"Error setting server instances: {e}")
    
    def get_hyperlink_urls(self) -> Dict[str, str]:
        """Get current hyperlink URLs.
        
        Returns:
            Dictionary with current hyperlink URLs
        """
        try:
            return self.hyperlink_manager.get_current_urls()
        except Exception as e:
            logger.error(f"Error getting hyperlink URLs: {e}")
            return {
                'display': 'http://localhost:8080',
                'controls': 'http://localhost:8081'
            }
    
    def refresh_hyperlink_urls(self) -> None:
        """Refresh hyperlink URLs when servers start/stop or change ports.
        
        This method should be called when:
        - Servers start or stop
        - Server ports change at runtime
        - Server configuration is updated
        """
        try:
            # Use stored server references if available
            web_server = getattr(self, '_web_server_ref', None)
            controls_server = getattr(self, '_controls_server_ref', None)
            
            if web_server or controls_server:
                # Update URLs with current server instances
                changed = self.hyperlink_manager.update_from_servers(web_server, controls_server)
                
                if changed and hasattr(self, 'hyperlink_widgets') and self.hyperlink_widgets:
                    # Refresh hyperlink display with new URLs
                    self.hyperlink_manager.refresh_hyperlink_display(self.hyperlink_widgets)
                    logger.info("Hyperlink URLs refreshed successfully")
                else:
                    logger.debug("Hyperlink URLs unchanged or no widgets to update")
            else:
                logger.debug("No server references available for URL refresh")
                
        except Exception as e:
            logger.error(f"Error refreshing hyperlink URLs: {e}")
    
    def on_server_port_changed(self, server_type: str, new_port: int) -> None:
        """Handle server port change events.
        
        Args:
            server_type: Type of server ('web' or 'controls')
            new_port: New port number
        """
        try:
            logger.info(f"Server port changed - {server_type}: {new_port}")
            
            # Refresh URLs to reflect the port change
            self.refresh_hyperlink_urls()
            
        except Exception as e:
            logger.error(f"Error handling server port change: {e}")
    
    def on_server_status_changed(self, server_type: str, is_running: bool) -> None:
        """Handle server status change events.
        
        Args:
            server_type: Type of server ('web' or 'controls')
            is_running: Whether the server is now running
        """
        try:
            status = "started" if is_running else "stopped"
            logger.info(f"Server status changed - {server_type}: {status}")
            
            # Refresh URLs to reflect the status change
            self.refresh_hyperlink_urls()
            
        except Exception as e:
            logger.error(f"Error handling server status change: {e}")
    
    def _apply_emergency_fallback_styling(self) -> None:
        """Apply emergency fallback styling when theme system fails completely."""
        logger.warning("Applying emergency fallback styling")
        
        try:
            # Set basic window properties
            try:
                self.root.configure(bg="#2b2b2b")
                self.root.geometry("400x300")
                self.root.minsize(350, 250)
                logger.debug("Basic window styling applied")
            except Exception as e:
                logger.error(f"Failed to apply basic window styling: {e}")
            
            # Configure basic option database for widgets
            try:
                fallback_options = [
                    ("*background", "#2b2b2b"),
                    ("*foreground", "#ffffff"),
                    ("*Button.background", "#3c3c3c"),
                    ("*Button.foreground", "#ffffff"),
                    ("*Label.background", "#2b2b2b"),
                    ("*Label.foreground", "#ffffff"),
                    ("*Frame.background", "#2b2b2b"),
                    ("*Listbox.background", "#3c3c3c"),
                    ("*Listbox.foreground", "#ffffff"),
                    ("*Listbox.selectBackground", "#4a9eff"),
                ]
                
                for option, value in fallback_options:
                    try:
                        self.root.option_add(option, value)
                    except Exception as e:
                        logger.warning(f"Failed to set fallback option {option}: {e}")
                
                logger.debug("Emergency fallback options applied")
                
            except Exception as e:
                logger.error(f"Failed to apply emergency fallback options: {e}")
            
            logger.info("Emergency fallback styling completed")
            
        except Exception as e:
            logger.error(f"Critical failure in emergency fallback styling: {e}")
    
    # Player Engine Callbacks
    
    def _on_playback_state_changed(self, state: PlaybackState) -> None:
        """Handle playback state change."""
        # Update GUI in main thread
        self.root.after(0, self._update_playback_controls, state)
    
    def _on_song_changed(self, song: Song) -> None:
        """Handle current song change."""
        # Update GUI in main thread
        self.root.after(0, self._update_current_song_display)
        self.root.after(0, self._update_playlist_selection)
        self.root.after(0, self._update_music_note_indicator)
    
    def _on_playback_error(self, error_message: str) -> None:
        """Handle playback error with user notification."""
        # Show error in main thread with more detailed information
        def show_error():
            # Check if this is a file-related error
            if "File not found" in error_message or "not found" in error_message.lower():
                # Offer to clean up invalid songs
                result = messagebox.askyesnocancel(
                    "File Not Found", 
                    f"Playback error: {error_message}\n\nWould you like to remove invalid songs from the playlist?",
                    parent=self.root
                )
                if result is True:  # Yes - clean up
                    self._cleanup_invalid_songs()
                elif result is False:  # No - just show error
                    messagebox.showerror("Playback Error", error_message, parent=self.root)
                # Cancel - do nothing
            else:
                # Show generic error
                messagebox.showerror("Playback Error", error_message, parent=self.root)
        
        self.root.after(0, show_error)
    
    # GUI Update Methods
    
    def _update_gui(self) -> None:
        """Update all GUI components."""
        if self._updating_gui:
            return
        
        self._updating_gui = True
        try:
            self._update_playlist_display()
            self._update_current_song_display()
            self._update_playback_controls()
            self._update_playlist_selection()
        finally:
            self._updating_gui = False
    
    def _update_playlist_display(self) -> None:
        """Update the modern playlist widget display."""
        # Get songs and current index
        songs = self.playlist_manager.get_songs()
        current_index = self.playlist_manager.get_playlist().current_index
        
        # Update the modern playlist widget
        self.playlist_widget.update_playlist(songs, current_index)
        
        # Update selection if we have a selected index
        if self._selected_index is not None and self._selected_index < len(songs):
            self.playlist_widget.set_selection(self._selected_index)
    
    def _update_current_song_display(self) -> None:
        """Update the current song display with modern styling, text truncation, and fade transitions."""
        current_song = self.playlist_manager.get_current_song()
        
        # Prepare the new text content
        if current_song:
            # Primary text: Song title
            song_title = current_song.get_display_name()
            
            # Secondary text: Artist and/or Album info
            artist_album_parts = []
            if hasattr(current_song, 'artist') and current_song.artist and current_song.artist != "Unknown Artist":
                artist_album_parts.append(current_song.artist)
            if hasattr(current_song, 'album') and current_song.album and current_song.album != "Unknown Album":
                artist_album_parts.append(current_song.album)
            
            artist_album_text = " • ".join(artist_album_parts) if artist_album_parts else ""
        else:
            song_title = "No song selected"
            artist_album_text = ""
        
        # Apply fade transition for song changes
        self._apply_fade_transition(song_title, artist_album_text)
    
    def _apply_fade_transition(self, new_title: str, new_artist_album: str) -> None:
        """Apply smooth fade transition when song changes.
        
        Args:
            new_title: New song title text
            new_artist_album: New artist/album text
        """
        # Cancel any existing fade animation
        if self._fade_after_id:
            self.root.after_cancel(self._fade_after_id)
        
        # Get current text to check if it's actually changing
        current_title = self.current_song_label.cget("text")
        
        if current_title == new_title:
            # No change needed, just update artist/album
            self._update_song_text_with_truncation(new_title, new_artist_album)
            return
        
        # Start fade out animation
        self._fade_alpha = 1.0
        self._fade_out_step(new_title, new_artist_album)
    
    def _fade_out_step(self, new_title: str, new_artist_album: str) -> None:
        """Perform one step of the fade out animation."""
        self._fade_alpha -= 0.15  # Fade out in ~7 steps
        
        if self._fade_alpha <= 0:
            # Fade out complete, update text and start fade in
            self._fade_alpha = 0.0
            self._update_song_text_with_truncation(new_title, new_artist_album)
            self._fade_in_step()
        else:
            # Continue fade out
            self._apply_fade_alpha()
            self._fade_after_id = self.root.after(30, lambda: self._fade_out_step(new_title, new_artist_album))
    
    def _fade_in_step(self) -> None:
        """Perform one step of the fade in animation."""
        self._fade_alpha += 0.15  # Fade in in ~7 steps
        
        if self._fade_alpha >= 1.0:
            # Fade in complete
            self._fade_alpha = 1.0
            self._apply_fade_alpha()
            self._fade_after_id = None
        else:
            # Continue fade in
            self._apply_fade_alpha()
            self._fade_after_id = self.root.after(30, self._fade_in_step)
    
    def _apply_fade_alpha(self) -> None:
        """Apply the current fade alpha to the labels."""
        try:
            # Calculate color with alpha applied
            # Convert hex color to RGB, apply alpha, convert back
            primary_color = self.theme_manager.theme.text_primary
            secondary_color = self.theme_manager.theme.text_secondary
            bg_color = self.theme_manager.theme.bg_secondary
            
            # Simple alpha blending with background
            primary_faded = self._blend_colors(primary_color, bg_color, self._fade_alpha)
            secondary_faded = self._blend_colors(secondary_color, bg_color, self._fade_alpha)
            
            # Apply faded colors
            self.current_song_label.configure(foreground=primary_faded)
            self.current_artist_label.configure(foreground=secondary_faded)
            
        except Exception as e:
            logger.warning(f"Fade effect failed: {e}")
            # Fallback to no fade effect
            pass
    
    def _blend_colors(self, color1: str, color2: str, alpha: float) -> str:
        """Blend two hex colors with given alpha.
        
        Args:
            color1: Foreground color (hex)
            color2: Background color (hex)
            alpha: Alpha value (0.0 to 1.0)
            
        Returns:
            Blended color as hex string
        """
        try:
            # Convert hex to RGB
            c1_rgb = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
            c2_rgb = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))
            
            # Blend colors
            blended = tuple(int(c1 * alpha + c2 * (1 - alpha)) for c1, c2 in zip(c1_rgb, c2_rgb))
            
            # Convert back to hex
            return f"#{blended[0]:02x}{blended[1]:02x}{blended[2]:02x}"
        except Exception:
            # Fallback to original color
            return color1
    
    def _update_song_text_with_truncation(self, title: str, artist_album: str) -> None:
        """Update song text with proper truncation for the available space.
        
        Args:
            title: Song title text
            artist_album: Artist/album text
        """
        try:
            # Calculate available width for text (frame width minus padding)
            self.now_playing_frame.update_idletasks()
            available_width = (self.now_playing_frame.winfo_width() - 
                             (self.theme_manager.theme.spacing_medium * 2))
            
            if available_width > 50:  # Only truncate if we have reasonable width
                # Truncate title text
                title_font = self.theme_manager.theme.get_font(
                    self.theme_manager.theme.font_size_body, 
                    self.theme_manager.theme.font_weight_medium
                )
                truncated_title = self.theme_manager.truncate_text(title, available_width, title_font)
                
                # Truncate artist/album text
                artist_font = self.theme_manager.theme.get_font(self.theme_manager.theme.font_size_small)
                truncated_artist_album = self.theme_manager.truncate_text(artist_album, available_width, artist_font)
            else:
                # Use original text if width calculation fails
                truncated_title = title
                truncated_artist_album = artist_album
            
            # Update labels
            self.current_song_label.config(text=truncated_title)
            self.current_artist_label.config(text=truncated_artist_album)
            
        except Exception as e:
            logger.warning(f"Text truncation failed: {e}")
            # Fallback to simple text update
            self.current_song_label.config(text=title)
            self.current_artist_label.config(text=artist_album)
    
    def _update_playback_controls(self, state: Optional[PlaybackState] = None) -> None:
        """Update playback control button states with modern styling and visual feedback."""
        if state is None:
            state = self.player_engine.get_state()
        
        # Reset all buttons to normal control style first
        normal_style = "ModernControl.TButton"
        active_style = "ModernControlActive.TButton"
        
        # Update button states and styling based on playback state
        if state == PlaybackState.PLAYING:
            # Play button is active (currently playing), others are normal
            self.play_button.configure(style=active_style, state="normal")
            self.pause_button.configure(style=normal_style, state="normal")
            self.stop_button.configure(style=normal_style, state="normal")
        elif state == PlaybackState.PAUSED:
            # Pause button is active (currently paused), others are normal
            self.play_button.configure(style=normal_style, state="normal")
            self.pause_button.configure(style=active_style, state="normal")
            self.stop_button.configure(style=normal_style, state="normal")
        else:  # STOPPED or LOADING
            # All buttons normal, stop might be slightly highlighted if just stopped
            self.play_button.configure(style=normal_style, state="normal")
            self.pause_button.configure(style=normal_style, state="normal")
            if state == PlaybackState.STOPPED:
                self.stop_button.configure(style=active_style, state="normal")
            else:
                self.stop_button.configure(style=normal_style, state="normal")
        
        # Update navigation buttons based on playlist availability
        has_songs = not self.playlist_manager.is_empty()
        if has_songs:
            self.next_button.configure(style=normal_style, state="normal")
            self.previous_button.configure(style=normal_style, state="normal")
        else:
            # Use disabled state for navigation when no songs available
            self.next_button.configure(style=normal_style, state="disabled")
            self.previous_button.configure(style=normal_style, state="disabled")
    
    def _update_playlist_selection(self) -> None:
        """Update playlist selection to highlight selected song (not current playing song)."""
        # Update selection in the modern playlist widget
        if hasattr(self, 'playlist_widget'):
            songs_count = len(self.playlist_manager.get_songs())
            if self._selected_index is not None and 0 <= self._selected_index < songs_count:
                self.playlist_widget.set_selection(self._selected_index)
            else:
                self.playlist_widget.set_selection(None)
    
    def _update_music_note_indicator(self) -> None:
        """Update the music note indicator to follow the currently playing song."""
        if hasattr(self, 'playlist_widget'):
            current_index = self.playlist_manager.get_playlist().current_index
            self.playlist_widget.update_current_song(current_index)

    def _trigger_web_update(self) -> None:
        """Trigger an immediate web server update with current song and state."""
        # This method will be called by the main application's enhanced callbacks
        # The actual web update logic is handled in main.py through the enhanced callbacks
        # We just need to ensure the callbacks are triggered
        current_song = self.player_engine.get_current_song()
        current_state = self.player_engine.get_state()
        
        # Force trigger the callbacks that update the web server
        if hasattr(self, '_on_song_changed') and current_song:
            self._on_song_changed(current_song)
        if hasattr(self, '_on_playback_state_changed'):
            self._on_playback_state_changed(current_state)
        
        logger.debug("Triggered web update for play button press")

    def _cleanup_invalid_songs(self) -> None:
        """Clean up invalid songs from the playlist with user feedback."""
        try:
            removed_count = self.playlist_manager.cleanup_invalid_songs()
            if removed_count > 0:
                self._update_playlist_display()
                self._update_current_song_display()
                messagebox.showinfo(
                    "Cleanup Complete", 
                    f"Removed {removed_count} invalid song(s) from playlist",
                    parent=self.root
                )
                # Save the cleaned playlist
                self.playlist_manager.save_playlist()
            else:
                messagebox.showinfo(
                    "No Issues Found", 
                    "All songs in the playlist are valid",
                    parent=self.root
                )
        except Exception as e:
            logger.error(f"Error during playlist cleanup: {e}")
            messagebox.showerror(
                "Cleanup Error", 
                f"Failed to clean up playlist: {str(e)}",
                parent=self.root
            )
    
    # Window Management
    
    def _on_window_close(self) -> None:
        """Handle window close event."""
        # Cancel any pending fade animations
        if self._fade_after_id:
            self.root.after_cancel(self._fade_after_id)
            self._fade_after_id = None
        
        # Save playlist before closing
        self.playlist_manager.save_playlist()
        
        # Stop playback
        self.player_engine.stop()
        
        # Close window
        self.root.destroy()
        
        logger.info("Main window closed")
    
    def run(self, skip_player_updates=False) -> None:
        """Start the GUI main loop.
        
        Args:
            skip_player_updates: If True, don't start player update scheduling
                                (useful when main app handles updates)
        """
        logger.info("Starting GUI main loop")
        
        # Set up periodic updates for player engine (unless handled elsewhere)
        if not skip_player_updates:
            self._schedule_player_update()
        
        # Start main loop
        self.root.mainloop()
    
    def _schedule_player_update(self) -> None:
        """Schedule periodic player engine updates."""
        try:
            # Update player engine (processes pygame events)
            self.player_engine.update()
            
            # Schedule next update
            self.root.after(100, self._schedule_player_update)  # Update every 100ms
            
        except Exception as e:
            logger.error(f"Error in player update: {e}")
            # Continue scheduling updates even if there's an error
            self.root.after(100, self._schedule_player_update)
    
    def show(self) -> None:
        """Show the main window."""
        if self.root:
            self.root.deiconify()
            self.root.lift()
    
    def hide(self) -> None:
        """Hide the main window."""
        if self.root:
            self.root.withdraw()
    
    def destroy(self) -> None:
        """Destroy the main window."""
        if self.root:
            self.root.destroy()
            self.root = None
    
    def is_running(self) -> bool:
        """Check if the GUI is running."""
        return self.root is not None and self.root.winfo_exists()
    
    def get_root(self) -> Optional[tk.Tk]:
        """Get the root window for testing purposes."""
        return self.root
    
    def __str__(self) -> str:
        """String representation of the main window."""
        return f"MainWindow(songs={self.playlist_manager.get_song_count()})"
    
    def __repr__(self) -> str:
        """Developer representation of the main window."""
        return f"MainWindow(playlist_manager={self.playlist_manager}, player_engine={self.player_engine})"