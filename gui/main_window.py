"""
Main window GUI for the music player application.

This module provides the desktop GUI interface with playlist display,
playback controls, and file management functionality.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
import webbrowser
from typing import Optional, List, Callable
from pathlib import Path

from models.song import Song
from models.playlist import Playlist
from core.playlist_manager import PlaylistManager
from core.player_engine import PlayerEngine, PlaybackState

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
        self.playlist_listbox = None
        self.current_song_label = None
        self.play_button = None
        self.pause_button = None
        self.stop_button = None
        self.next_button = None
        self.previous_button = None
        self.volume_scale = None
        self.loop_var = None
        self.loop_checkbox = None
        
        # State tracking
        self._updating_gui = False
        self._drag_start_index = None
        
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
        self.root.title("Music Player")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Configure grid weights for resizing
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main components
        self._create_current_song_display()
        self._create_playlist_display()
        self._create_playback_controls()
        self._create_file_management()
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        logger.debug("GUI components created successfully")
    
    def _create_current_song_display(self) -> None:
        """Create the current song display area."""
        # Current song frame
        current_frame = ttk.LabelFrame(self.root, text="Now Playing", padding="10")
        current_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        current_frame.grid_columnconfigure(0, weight=1)
        
        # Current song label
        self.current_song_label = ttk.Label(
            current_frame, 
            text="No song selected",
            font=("Arial", 12, "bold"),
            anchor="center"
        )
        self.current_song_label.grid(row=0, column=0, sticky="ew")
    
    def _create_playlist_display(self) -> None:
        """Create the playlist display with drag-and-drop reordering."""
        # Playlist frame
        playlist_frame = ttk.LabelFrame(self.root, text="Playlist", padding="5")
        playlist_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        playlist_frame.grid_rowconfigure(0, weight=1)
        playlist_frame.grid_columnconfigure(0, weight=1)
        
        # Create listbox with scrollbar
        listbox_frame = ttk.Frame(playlist_frame)
        listbox_frame.grid(row=0, column=0, sticky="nsew")
        listbox_frame.grid_rowconfigure(0, weight=1)
        listbox_frame.grid_columnconfigure(0, weight=1)
        
        # Playlist listbox
        self.playlist_listbox = tk.Listbox(
            listbox_frame,
            selectmode=tk.SINGLE,
            font=("Arial", 10),
            activestyle="dotbox"
        )
        self.playlist_listbox.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.playlist_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.playlist_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Bind events for playlist interaction
        self.playlist_listbox.bind("<Double-Button-1>", self._on_playlist_double_click)
        self.playlist_listbox.bind("<Button-1>", self._on_playlist_click)
        self.playlist_listbox.bind("<B1-Motion>", self._on_playlist_drag)
        self.playlist_listbox.bind("<ButtonRelease-1>", self._on_playlist_drop)
    
    def _create_playback_controls(self) -> None:
        """Create playback control buttons and volume slider."""
        # Controls frame
        controls_frame = ttk.Frame(self.root)
        controls_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        controls_frame.grid_columnconfigure(5, weight=1)  # Volume slider column
        
        # Playback buttons
        self.previous_button = ttk.Button(
            controls_frame, 
            text="⏮", 
            width=3,
            command=self._on_previous_clicked
        )
        self.previous_button.grid(row=0, column=0, padx=2)
        
        self.play_button = ttk.Button(
            controls_frame, 
            text="▶", 
            width=3,
            command=self._on_play_clicked
        )
        self.play_button.grid(row=0, column=1, padx=2)
        
        self.pause_button = ttk.Button(
            controls_frame, 
            text="⏸", 
            width=3,
            command=self._on_pause_clicked
        )
        self.pause_button.grid(row=0, column=2, padx=2)
        
        self.stop_button = ttk.Button(
            controls_frame, 
            text="⏹", 
            width=3,
            command=self._on_stop_clicked
        )
        self.stop_button.grid(row=0, column=3, padx=2)
        
        self.next_button = ttk.Button(
            controls_frame, 
            text="⏭", 
            width=3,
            command=self._on_next_clicked
        )
        self.next_button.grid(row=0, column=4, padx=2)
        
        # Volume control
        ttk.Label(controls_frame, text="Volume:").grid(row=0, column=5, padx=(20, 5), sticky="e")
        
        self.volume_scale = ttk.Scale(
            controls_frame,
            from_=0.0,
            to=1.0,
            orient="horizontal",
            length=150,
            command=self._on_volume_changed
        )
        self.volume_scale.set(self.player_engine.get_volume())
        self.volume_scale.grid(row=0, column=6, padx=5, sticky="ew")
        
        # Loop checkbox
        self.loop_var = tk.BooleanVar()
        self.loop_var.set(self.playlist_manager.is_loop_enabled())
        self.loop_checkbox = ttk.Checkbutton(
            controls_frame,
            text="Loop",
            variable=self.loop_var,
            command=self._on_loop_toggled
        )
        self.loop_checkbox.grid(row=0, column=7, padx=(20, 0))
    
    def _create_file_management(self) -> None:
        """Create file management buttons."""
        # File management frame
        file_frame = ttk.Frame(self.root)
        file_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        
        # Add songs button
        add_button = ttk.Button(
            file_frame,
            text="Add Songs",
            command=self._on_add_songs_clicked
        )
        add_button.grid(row=0, column=0, padx=5)
        
        # Remove song button
        remove_button = ttk.Button(
            file_frame,
            text="Remove Song",
            command=self._on_remove_song_clicked
        )
        remove_button.grid(row=0, column=1, padx=5)
        
        # Clear playlist button
        clear_button = ttk.Button(
            file_frame,
            text="Clear Playlist",
            command=self._on_clear_playlist_clicked
        )
        clear_button.grid(row=0, column=2, padx=5)
        
        # Save playlist button
        save_button = ttk.Button(
            file_frame,
            text="Save Playlist",
            command=self._on_save_playlist_clicked
        )
        save_button.grid(row=0, column=3, padx=5)
        
        # Open web interface button
        web_button = ttk.Button(
            file_frame,
            text="🌐 Web Display",
            command=self._on_open_web_interface_clicked
        )
        web_button.grid(row=0, column=4, padx=5)
    
    # Event Handlers
    
    def _on_playlist_double_click(self, event) -> None:
        """Handle double-click on playlist item."""
        selection = self.playlist_listbox.curselection()
        if selection:
            index = selection[0]
            song = self.playlist_manager.set_current_song(index)
            if song:
                self.player_engine.play_song(song)
                logger.debug(f"Double-clicked to play: {song.get_display_name()}")
    
    def _on_playlist_click(self, event) -> None:
        """Handle single click on playlist item (start of drag)."""
        selection = self.playlist_listbox.curselection()
        if selection:
            self._drag_start_index = selection[0]
    
    def _on_playlist_drag(self, event) -> None:
        """Handle dragging of playlist items."""
        if self._drag_start_index is not None:
            # Visual feedback could be added here
            pass
    
    def _on_playlist_drop(self, event) -> None:
        """Handle dropping of playlist items (reordering)."""
        if self._drag_start_index is not None:
            # Get the drop target index
            drop_index = self.playlist_listbox.nearest(event.y)
            
            if drop_index != self._drag_start_index and 0 <= drop_index < self.playlist_listbox.size():
                # Perform reordering
                success = self.playlist_manager.reorder_songs(self._drag_start_index, drop_index)
                if success:
                    self._update_playlist_display()
                    # Select the moved item
                    self.playlist_listbox.selection_set(drop_index)
                    logger.debug(f"Reordered song from {self._drag_start_index} to {drop_index}")
        
        self._drag_start_index = None
    
    def _on_play_clicked(self) -> None:
        """Handle play button click."""
        if self.player_engine.is_paused():
            # Resume playback
            self.player_engine.play()
        else:
            # Start playing current song or first song in playlist
            current_song = self.playlist_manager.get_current_song()
            if current_song:
                self.player_engine.play_song(current_song)
            elif not self.playlist_manager.is_empty():
                # Play first song
                first_song = self.playlist_manager.set_current_song(0)
                if first_song:
                    self.player_engine.play_song(first_song)
    
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
    
    def _on_volume_changed(self, value) -> None:
        """Handle volume slider change."""
        try:
            volume = float(value)
            self.player_engine.set_volume(volume)
        except ValueError:
            logger.warning(f"Invalid volume value: {value}")
    
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
        selection = self.playlist_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a song to remove", parent=self.root)
            return
        
        index = selection[0]
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
        """Update the playlist listbox display."""
        # Clear current items
        self.playlist_listbox.delete(0, tk.END)
        
        # Add songs to listbox
        songs = self.playlist_manager.get_songs()
        for i, song in enumerate(songs):
            display_text = f"{i+1:2d}. {song.get_display_name()}"
            self.playlist_listbox.insert(tk.END, display_text)
        
        # Update selection
        self._update_playlist_selection()
    
    def _update_current_song_display(self) -> None:
        """Update the current song display."""
        current_song = self.playlist_manager.get_current_song()
        if current_song:
            text = f"{current_song.get_display_name()}"
            if current_song.album and current_song.album != "Unknown Album":
                text += f" - {current_song.album}"
        else:
            text = "No song selected"
        
        self.current_song_label.config(text=text)
    
    def _update_playback_controls(self, state: Optional[PlaybackState] = None) -> None:
        """Update playback control button states."""
        if state is None:
            state = self.player_engine.get_state()
        
        # Update button states based on playback state
        if state == PlaybackState.PLAYING:
            self.play_button.config(state="disabled")
            self.pause_button.config(state="normal")
            self.stop_button.config(state="normal")
        elif state == PlaybackState.PAUSED:
            self.play_button.config(state="normal")
            self.pause_button.config(state="disabled")
            self.stop_button.config(state="normal")
        else:  # STOPPED or LOADING
            self.play_button.config(state="normal")
            self.pause_button.config(state="disabled")
            self.stop_button.config(state="disabled")
        
        # Update navigation buttons
        has_songs = not self.playlist_manager.is_empty()
        self.next_button.config(state="normal" if has_songs else "disabled")
        self.previous_button.config(state="normal" if has_songs else "disabled")
    
    def _update_playlist_selection(self) -> None:
        """Update playlist selection to highlight current song."""
        # Clear current selection
        self.playlist_listbox.selection_clear(0, tk.END)
        
        # Highlight current song
        current_index = self.playlist_manager.get_playlist().current_index
        if 0 <= current_index < self.playlist_listbox.size():
            self.playlist_listbox.selection_set(current_index)
            self.playlist_listbox.see(current_index)  # Scroll to make it visible

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