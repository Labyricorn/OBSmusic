"""
Modern playlist widget with alternating row colors and compact design.

This module provides a custom playlist display widget that supports
alternating row colors, modern selection highlighting, and compact
24px row height as specified in the GUI modernization requirements.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Callable, Any
import logging

logger = logging.getLogger(__name__)


class ModernPlaylistWidget(tk.Frame):
    """Custom playlist widget with modern styling and alternating row colors."""
    
    def __init__(self, parent: tk.Widget, theme_manager, **kwargs):
        """Initialize the modern playlist widget.
        
        Args:
            parent: Parent widget
            theme_manager: ThemeManager instance for styling
            **kwargs: Additional configuration options
        """
        super().__init__(parent, **kwargs)
        
        self.theme_manager = theme_manager
        self.theme = theme_manager.theme
        
        # Widget state
        self._songs = []
        self._current_index = None
        self._selected_index = None
        self._drag_start_index = None
        self._potential_drag_index = None
        self._click_x = 0
        self._click_y = 0
        
        # Callbacks
        self._selection_callback = None
        self._drag_drop_callback = None
        
        # Row widgets storage
        self._row_widgets = []
        
        # Configure the main frame
        self.configure(bg=self.theme.bg_secondary)
        
        # Create the scrollable content area
        self._create_scrollable_area()
        
        logger.debug("ModernPlaylistWidget initialized")
    
    def _create_scrollable_area(self):
        """Create the scrollable area for playlist items."""
        # Configure grid layout for the main frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create canvas for scrolling
        self.canvas = tk.Canvas(
            self,
            bg=self.theme.bg_secondary,
            highlightthickness=0,
            borderwidth=0
        )
        
        # Create scrollbar
        self.scrollbar = self.theme_manager.create_modern_scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview
        )
        
        # Create scrollable frame
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.theme.bg_secondary)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self._update_scroll_region()
        )
        
        # Create window in canvas
        self.canvas_window = self.canvas.create_window(
            (0, 0), 
            window=self.scrollable_frame, 
            anchor="nw"
        )
        
        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Bind mouse wheel scrolling to multiple widgets for better coverage
        self._bind_mousewheel_events()
        
        # Use grid instead of pack for better control
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind canvas resize to update scrollable frame width
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Force initial scroll region update
        self.after(1, self._update_scroll_region)
    
    def _on_canvas_configure(self, event):
        """Handle canvas resize to update scrollable frame width."""
        # Update the scrollable frame width to match canvas width
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        # Update scroll region after resize
        self.after_idle(self._update_scroll_region)
    
    def _update_scroll_region(self):
        """Update the canvas scroll region and scrollbar visibility."""
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox("all")
        
        if bbox:
            self.canvas.configure(scrollregion=bbox)
            
            # Show/hide scrollbar based on content height
            canvas_height = self.canvas.winfo_height()
            content_height = bbox[3] - bbox[1]
            
            if content_height > canvas_height:
                # Content is taller than canvas, show scrollbar
                self.scrollbar.grid(row=0, column=1, sticky="ns")
            else:
                # Content fits, hide scrollbar
                self.scrollbar.grid_remove()
        else:
            self.canvas.configure(scrollregion=(0, 0, 0, 0))
            self.scrollbar.grid_remove()
    
    def _bind_mousewheel_events(self):
        """Bind mouse wheel events to relevant widgets."""
        def on_mousewheel(event):
            # Check if there's content to scroll
            bbox = self.canvas.bbox("all")
            if bbox and bbox[3] > self.canvas.winfo_height():
                # Calculate scroll amount (3 units per wheel step for smooth scrolling)
                delta = -1 * (event.delta / 120) * 3
                self.canvas.yview_scroll(int(delta), "units")
                return "break"  # Prevent event propagation
        
        # Bind to main widget areas
        self.bind("<MouseWheel>", on_mousewheel)
        self.canvas.bind("<MouseWheel>", on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", on_mousewheel)
        
        # Store the mousewheel handler to bind to row widgets later
        self._mousewheel_handler = on_mousewheel
    
    def update_playlist(self, songs: List[Any], current_index: Optional[int] = None):
        """Update the playlist display with new songs.
        
        Args:
            songs: List of song objects
            current_index: Index of currently playing song
        """
        logger.debug(f"Updating playlist display with {len(songs)} songs, current_index: {current_index}")
        
        try:
            self._songs = songs
            self._current_index = current_index
            
            # Clear existing row widgets with error handling
            try:
                for widget_data in self._row_widgets:
                    try:
                        if 'frame' in widget_data and widget_data['frame']:
                            widget_data['frame'].destroy()
                    except Exception as e:
                        logger.warning(f"Failed to destroy row widget: {e}")
                self._row_widgets.clear()
                logger.debug("Existing row widgets cleared successfully")
            except Exception as e:
                logger.warning(f"Error clearing existing row widgets: {e}")
                self._row_widgets.clear()  # Clear the list even if destruction failed
            
            # Create new row widgets with error handling
            successful_rows = 0
            for i, song in enumerate(songs):
                try:
                    self._create_row_widget(i, song)
                    successful_rows += 1
                except Exception as e:
                    logger.error(f"Failed to create row widget for song {i}: {e}")
                    # Continue with other songs even if one fails
            
            logger.debug(f"Created {successful_rows} out of {len(songs)} row widgets")
            
            # Update canvas scroll region with error handling
            try:
                self._update_scroll_region()
            except Exception as e:
                logger.warning(f"Failed to update scroll region: {e}")
            
            logger.info(f"Updated playlist display with {successful_rows}/{len(songs)} songs successfully")
            
        except Exception as e:
            logger.error(f"Critical error updating playlist display: {e}")
            # Try to maintain a functional state
            try:
                self._songs = songs if songs else []
                self._current_index = current_index
            except Exception as e2:
                logger.error(f"Failed to maintain basic playlist state: {e2}")
                self._songs = []
                self._current_index = None
    
    def _create_row_widget(self, index: int, song: Any):
        """Create a row widget for a single song with comprehensive error handling.
        
        Args:
            index: Song index in playlist
            song: Song object
        """
        logger.debug(f"Creating row widget for song {index}")
        
        try:
            # Determine row colors (alternating) with error handling
            try:
                primary_color, alternate_color = self.theme_manager.get_alternating_row_colors()
                row_bg = alternate_color if index % 2 == 1 else primary_color
            except Exception as e:
                logger.warning(f"Failed to get alternating row colors: {e}")
                # Fallback colors
                row_bg = "#2b2b2b" if index % 2 == 0 else "#3c3c3c"
            
            # Create row frame with fixed height (24px) with error handling
            try:
                row_frame = tk.Frame(
                    self.scrollable_frame,
                    bg=row_bg,
                    height=self.theme.playlist_row_height,
                    cursor="hand2"
                )
                row_frame.pack(fill="x", pady=0)
                row_frame.pack_propagate(False)  # Maintain fixed height
                
                # Configure grid
                row_frame.grid_columnconfigure(1, weight=1)  # Song text column expands
                logger.debug(f"Row frame created successfully for song {index}")
            except Exception as e:
                logger.error(f"Failed to create row frame for song {index}: {e}")
                # Try with minimal configuration
                row_frame = tk.Frame(self.scrollable_frame, bg=row_bg)
                row_frame.pack(fill="x")
            
            # Music note indicator (if this is the current song) with error handling
            try:
                music_note_config = self.theme_manager.get_music_note_config()
                indicator_text = music_note_config["symbol"] if index == self._current_index else ""
                
                indicator_label = tk.Label(
                    row_frame,
                    text=indicator_text,
                    bg=row_bg,
                    fg=music_note_config["color"] if indicator_text else row_bg,
                    font=music_note_config["font"],
                    width=2,
                    anchor="center"
                )
                indicator_label.grid(row=0, column=0, sticky="nsew", padx=(4, 0))
                logger.debug(f"Music note indicator created for song {index}")
            except Exception as e:
                logger.warning(f"Failed to create music note indicator for song {index}: {e}")
                # Create fallback indicator
                try:
                    indicator_text = "♪" if index == self._current_index else ""
                    indicator_label = tk.Label(
                        row_frame,
                        text=indicator_text,
                        bg=row_bg,
                        fg="#00d084" if indicator_text else row_bg,
                        width=2,
                        anchor="center"
                    )
                    indicator_label.grid(row=0, column=0, sticky="nsew", padx=(4, 0))
                except Exception as e2:
                    logger.error(f"Failed to create fallback indicator for song {index}: {e2}")
                    # Create minimal indicator
                    indicator_label = tk.Label(row_frame, text="", bg=row_bg, width=2)
                    indicator_label.grid(row=0, column=0)
            
            # Song number and title with error handling
            try:
                # Get display name safely
                try:
                    display_name = song.get_display_name()
                except Exception as e:
                    logger.warning(f"Failed to get display name for song {index}: {e}")
                    display_name = str(song) if song else f"Song {index + 1}"
                
                display_text = f"{index+1:2d}. {display_name}"
                
                song_label = tk.Label(
                    row_frame,
                    text=display_text,
                    bg=row_bg,
                    fg=self.theme.text_primary,
                    font=(self.theme.font_family, 10, self.theme.font_weight_regular),  # 10px regular weight
                    anchor="w",
                    padx=4
                )
                song_label.grid(row=0, column=1, sticky="nsew")
                logger.debug(f"Song label created for song {index}")
            except Exception as e:
                logger.warning(f"Failed to create song label for song {index}: {e}")
                # Create fallback label
                try:
                    fallback_text = f"{index+1:2d}. Song {index + 1}"
                    song_label = tk.Label(
                        row_frame,
                        text=fallback_text,
                        bg=row_bg,
                        fg="#ffffff",
                        anchor="w"
                    )
                    song_label.grid(row=0, column=1, sticky="nsew")
                except Exception as e2:
                    logger.error(f"Failed to create fallback song label for song {index}: {e2}")
                    # Create minimal label
                    song_label = tk.Label(row_frame, text=f"Song {index + 1}", bg=row_bg)
                    song_label.grid(row=0, column=1)
            
            # Store references with error handling
            try:
                row_data = {
                    'frame': row_frame,
                    'indicator': indicator_label,
                    'label': song_label,
                    'index': index,
                    'original_bg': row_bg
                }
                self._row_widgets.append(row_data)
                logger.debug(f"Row data stored for song {index}")
            except Exception as e:
                logger.error(f"Failed to store row data for song {index}: {e}")
                # Store minimal data
                self._row_widgets.append({
                    'frame': row_frame,
                    'index': index,
                    'original_bg': row_bg
                })
            
            # Bind events for interaction with error handling
            try:
                self._bind_row_events(row_data)
                logger.debug(f"Events bound for song {index}")
            except Exception as e:
                logger.warning(f"Failed to bind events for song {index}: {e}")
                # Continue without events - widget will still be visible
            
        except Exception as e:
            logger.error(f"Critical error creating row widget for song {index}: {e}")
            raise  # Re-raise to let caller handle
    
    def _bind_row_events(self, row_data: dict):
        """Bind mouse events to a row widget.
        
        Args:
            row_data: Dictionary containing row widget information
        """
        widgets = [row_data['frame'], row_data['indicator'], row_data['label']]
        
        for widget in widgets:
            widget.bind("<Button-1>", lambda e, idx=row_data['index']: self._on_row_click(e, idx))
            widget.bind("<B1-Motion>", lambda e, idx=row_data['index']: self._on_row_drag(e, idx))
            widget.bind("<ButtonRelease-1>", lambda e, idx=row_data['index']: self._on_row_drop(e, idx))
            widget.bind("<Enter>", lambda e, data=row_data: self._on_row_enter(e, data))
            widget.bind("<Leave>", lambda e, data=row_data: self._on_row_leave(e, data))
            
            # Bind mouse wheel scrolling to each row widget
            if hasattr(self, '_mousewheel_handler'):
                widget.bind("<MouseWheel>", self._mousewheel_handler)
    
    def _on_row_click(self, event, index: int):
        """Handle row click event.
        
        Args:
            event: Mouse event
            index: Row index
        """
        # Update selection
        self._update_selection(index)
        
        # Store click position for drag detection
        self._click_x = event.x_root
        self._click_y = event.y_root
        self._potential_drag_index = index
        
        # Call selection callback
        if self._selection_callback:
            self._selection_callback(index)
        
        logger.debug(f"Selected playlist row {index}")
    
    def _on_row_drag(self, event, index: int):
        """Handle row drag event.
        
        Args:
            event: Mouse event
            index: Row index
        """
        if hasattr(self, '_potential_drag_index') and self._potential_drag_index is not None:
            # Check if mouse has moved enough to constitute a drag (threshold: 5 pixels)
            if hasattr(self, '_click_x') and hasattr(self, '_click_y'):
                dx = abs(event.x_root - self._click_x)
                dy = abs(event.y_root - self._click_y)
                if dx > 5 or dy > 5:
                    # Start actual drag operation
                    self._drag_start_index = self._potential_drag_index
                    self._potential_drag_index = None
                    logger.debug(f"Started drag operation from index {self._drag_start_index}")
    
    def _on_row_drop(self, event, index: int):
        """Handle row drop event.
        
        Args:
            event: Mouse event
            index: Row index
        """
        if self._drag_start_index is not None:
            # Find the drop target by checking which row the mouse is over
            drop_index = self._find_drop_target(event.y_root)
            
            if (drop_index is not None and 
                drop_index != self._drag_start_index and 
                0 <= drop_index < len(self._songs)):
                
                # Call drag-drop callback
                if self._drag_drop_callback:
                    self._drag_drop_callback(self._drag_start_index, drop_index)
                
                logger.debug(f"Dropped row from {self._drag_start_index} to {drop_index}")
        
        # Clean up drag state
        self._drag_start_index = None
        self._potential_drag_index = None
    
    def _find_drop_target(self, y_pos: int) -> Optional[int]:
        """Find the drop target index based on mouse Y position.
        
        Args:
            y_pos: Mouse Y position in screen coordinates
            
        Returns:
            Target index or None if not found
        """
        for i, row_data in enumerate(self._row_widgets):
            frame = row_data['frame']
            frame_y = frame.winfo_rooty()
            frame_height = frame.winfo_height()
            
            if frame_y <= y_pos <= frame_y + frame_height:
                return i
        
        return None
    
    def _on_row_enter(self, event, row_data: dict):
        """Handle mouse enter event for row hover effect.
        
        Args:
            event: Mouse event
            row_data: Row widget data
        """
        if row_data['index'] != self._selected_index:
            # Apply hover effect
            hover_color = self.theme.bg_tertiary
            row_data['frame'].configure(bg=hover_color)
            row_data['indicator'].configure(bg=hover_color)
            row_data['label'].configure(bg=hover_color)
    
    def _on_row_leave(self, event, row_data: dict):
        """Handle mouse leave event to remove hover effect.
        
        Args:
            event: Mouse event
            row_data: Row widget data
        """
        if row_data['index'] != self._selected_index:
            # Restore original background
            original_bg = row_data['original_bg']
            row_data['frame'].configure(bg=original_bg)
            row_data['indicator'].configure(bg=original_bg)
            row_data['label'].configure(bg=original_bg)
    
    def _update_selection(self, index: int):
        """Update the visual selection state.
        
        Args:
            index: Index to select
        """
        # Clear previous selection
        if self._selected_index is not None and self._selected_index < len(self._row_widgets):
            old_row = self._row_widgets[self._selected_index]
            original_bg = old_row['original_bg']
            old_row['frame'].configure(bg=original_bg)
            old_row['indicator'].configure(bg=original_bg)
            old_row['label'].configure(bg=original_bg)
        
        # Apply new selection
        self._selected_index = index
        if index < len(self._row_widgets):
            row_data = self._row_widgets[index]
            selection_color = self.theme.accent
            row_data['frame'].configure(bg=selection_color)
            row_data['indicator'].configure(bg=selection_color)
            row_data['label'].configure(bg=selection_color)
    
    def update_current_song(self, current_index: Optional[int]):
        """Update the music note indicator for the currently playing song.
        
        Args:
            current_index: Index of currently playing song
        """
        old_current = self._current_index
        
        # Validate current_index before setting it
        if current_index is not None:
            # For empty playlist, don't set current index
            if len(self._songs) == 0:
                current_index = None
            # For invalid index, don't set current index
            elif current_index < 0 or current_index >= len(self._songs):
                current_index = None
        
        self._current_index = current_index
        
        # Update music note indicators
        music_note_config = self.theme_manager.get_music_note_config()
        
        # Remove old indicator
        if old_current is not None and old_current < len(self._row_widgets):
            old_row = self._row_widgets[old_current]
            old_row['indicator'].configure(text="", fg=old_row['original_bg'])
        
        # Add new indicator
        if current_index is not None and current_index < len(self._row_widgets):
            new_row = self._row_widgets[current_index]
            new_row['indicator'].configure(
                text=music_note_config["symbol"],
                fg=music_note_config["color"]
            )
    
    def set_selection_callback(self, callback: Callable[[int], None]):
        """Set callback for selection events.
        
        Args:
            callback: Function to call when selection changes
        """
        self._selection_callback = callback
    
    def set_drag_drop_callback(self, callback: Callable[[int, int], None]):
        """Set callback for drag-drop events.
        
        Args:
            callback: Function to call when drag-drop occurs
        """
        self._drag_drop_callback = callback
    
    def get_selection(self) -> Optional[int]:
        """Get the currently selected index.
        
        Returns:
            Selected index or None
        """
        return self._selected_index
    
    def set_selection(self, index: Optional[int]):
        """Set the selection programmatically.
        
        Args:
            index: Index to select or None to clear selection
        """
        if index is None:
            if self._selected_index is not None:
                self._update_selection(-1)  # Clear selection
                self._selected_index = None
        else:
            self._update_selection(index)
    
    def handle_resize(self, width: int, height: int):
        """Handle resize events for responsive behavior with comprehensive error handling.
        
        Args:
            width: New width of the container
            height: New height available for the playlist
        """
        logger.debug(f"Handling playlist resize to {width}x{height}")
        
        try:
            # Update canvas size if needed with error handling
            try:
                scrollbar_width = 20  # Account for scrollbar width
                new_canvas_width = max(100, width - scrollbar_width)  # Minimum width
                new_canvas_height = max(50, height)  # Minimum height
                
                self.canvas.configure(width=new_canvas_width, height=new_canvas_height)
                logger.debug(f"Canvas resized to {new_canvas_width}x{new_canvas_height}")
            except Exception as e:
                logger.warning(f"Failed to resize canvas: {e}")
                # Continue with text truncation even if canvas resize failed
            
            # Update text truncation for all visible rows based on new width
            try:
                available_text_width = max(100, width - 60)  # Account for music note indicator and padding, minimum 100px
                successful_updates = 0
                
                for row_data in self._row_widgets:
                    try:
                        if (row_data.get('index', -1) < len(self._songs) and 
                            'label' in row_data and row_data['label']):
                            
                            song = self._songs[row_data['index']]
                            
                            # Get display name safely
                            try:
                                display_name = song.get_display_name()
                            except Exception as e:
                                logger.warning(f"Failed to get display name for resize: {e}")
                                display_name = f"Song {row_data['index'] + 1}"
                            
                            display_text = f"{row_data['index']+1:2d}. {display_name}"
                            
                            # Truncate text if needed with error handling
                            try:
                                truncated_text = self.theme_manager.truncate_text(
                                    display_text,
                                    available_text_width,
                                    (self.theme.font_family, 10, self.theme.font_weight_regular)
                                )
                            except Exception as e:
                                logger.warning(f"Failed to truncate text, using original: {e}")
                                truncated_text = display_text
                            
                            # Update label text
                            try:
                                row_data['label'].configure(text=truncated_text)
                                successful_updates += 1
                            except Exception as e:
                                logger.warning(f"Failed to update label text for row {row_data.get('index', '?')}: {e}")
                                
                    except Exception as e:
                        logger.warning(f"Failed to process row data during resize: {e}")
                        continue
                
                logger.debug(f"Updated text truncation for {successful_updates} out of {len(self._row_widgets)} rows")
                
            except Exception as e:
                logger.warning(f"Error updating text truncation during resize: {e}")
            
            # Update scroll region with error handling
            try:
                self._update_scroll_region()
                logger.debug("Scroll region updated after resize")
            except Exception as e:
                logger.warning(f"Failed to update scroll region after resize: {e}")
            
            logger.info(f"Playlist widget resize completed: {width}x{height}")
            
        except Exception as e:
            logger.error(f"Critical error handling playlist resize: {e}")
            # Try to maintain basic functionality
            try:
                self._update_scroll_region()
            except Exception as e2:
                logger.error(f"Failed to maintain basic scroll region after resize error: {e2}")
    
    def clear(self):
        """Clear all playlist items."""
        self._songs.clear()
        self._current_index = None
        self._selected_index = None
        
        for widget in self._row_widgets:
            widget['frame'].destroy()
        self._row_widgets.clear()
        
        # Update canvas scroll region
        self._update_scroll_region()