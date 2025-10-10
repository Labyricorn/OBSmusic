"""
Modern theme system for the music player GUI.

This module provides a comprehensive theme system with color palettes,
typography, spacing definitions, and utilities for consistent styling
across all GUI components.
"""

import tkinter as tk
from tkinter import ttk
import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
import platform

logger = logging.getLogger(__name__)


@dataclass
class ModernTheme:
    """Modern theme configuration for GUI components.
    
    Provides a comprehensive design system with colors, typography,
    spacing, and component dimensions for consistent modern styling.
    """
    
    # Color Palette
    bg_primary: str = "#2b2b2b"          # Dark charcoal background
    bg_secondary: str = "#3c3c3c"        # Medium gray secondary background
    bg_tertiary: str = "#4a4a4a"         # Lighter gray for hover states
    accent: str = "#4a9eff"              # Modern blue accent
    text_primary: str = "#ffffff"        # White primary text
    text_secondary: str = "#b0b0b0"      # Light gray secondary text
    success: str = "#00d084"             # Green for success/playing states
    warning: str = "#ff6b35"             # Orange for warnings
    error: str = "#ff4757"               # Red for errors
    
    # Typography
    font_family: str = "Segoe UI"        # Primary font family
    font_family_fallback: str = "Arial"  # Fallback font
    font_size_title: int = 14            # Title text size
    font_size_body: int = 11             # Body text size
    font_size_small: int = 9             # Small text size
    font_weight_regular: str = "normal"  # Regular font weight
    font_weight_medium: str = "bold"     # Medium font weight (bold in Tkinter)
    font_weight_bold: str = "bold"       # Bold font weight
    
    # Spacing System (8px base unit)
    spacing_xs: int = 2                  # Extra small spacing
    spacing_small: int = 4               # Small spacing
    spacing_medium: int = 8              # Medium spacing
    spacing_large: int = 16              # Large spacing
    spacing_xl: int = 24                 # Extra large spacing
    
    # Component Dimensions
    window_width: int = 400              # Default window width
    window_height: int = 300             # Default window height
    window_min_width: int = 350          # Minimum window width
    window_min_height: int = 250         # Minimum window height
    
    # Component Heights
    now_playing_height: int = 60         # Now playing display height
    controls_height: int = 30            # Control panel height
    file_panel_height: int = 30          # File management panel height
    playlist_row_height: int = 24        # Playlist row height
    
    # Button Dimensions
    control_button_size: int = 24        # Control button size (24x24px)
    file_button_width: int = 80          # File management button width
    file_button_height: int = 24         # File management button height
    
    # Border and Corner Radius
    border_radius: int = 8               # Standard border radius
    border_width: int = 1                # Standard border width
    
    # Animation and Transitions
    transition_duration: int = 200       # Standard transition duration (ms)
    
    def get_font(self, size: int = None, weight: str = None) -> Tuple[str, int, str]:
        """Get font tuple for Tkinter components.
        
        Args:
            size: Font size (defaults to body size)
            weight: Font weight (defaults to regular)
            
        Returns:
            Tuple of (family, size, weight) for Tkinter font configuration
        """
        if size is None:
            size = self.font_size_body
        if weight is None:
            weight = self.font_weight_regular
            
        return (self.font_family, size, weight)
    
    def get_fallback_font(self, size: int = None, weight: str = None) -> Tuple[str, int, str]:
        """Get fallback font tuple for Tkinter components.
        
        Args:
            size: Font size (defaults to body size)
            weight: Font weight (defaults to regular)
            
        Returns:
            Tuple of (family, size, weight) for Tkinter font configuration
        """
        if size is None:
            size = self.font_size_body
        if weight is None:
            weight = self.font_weight_regular
            
        return (self.font_family_fallback, size, weight)


class ThemeManager:
    """Manages theme application and provides utilities for consistent styling."""
    
    def __init__(self, theme: Optional[ModernTheme] = None):
        """Initialize the theme manager.
        
        Args:
            theme: ModernTheme instance (creates default if None)
        """
        self.theme = theme or ModernTheme()
        self._style = None
        self._root = None
        self._theme_applied = False
        
        # Platform-specific adjustments
        self._adjust_theme_for_platform()
        
        logger.debug("ThemeManager initialized")
    
    def _adjust_theme_for_platform(self) -> None:
        """Adjust theme settings based on the current platform."""
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            self.theme.font_family = "SF Pro Display"
        elif system == "linux":
            self.theme.font_family = "Ubuntu"
        # Windows uses Segoe UI by default
        
        logger.debug(f"Adjusted theme for platform: {system}")
    
    def apply_theme(self, root: tk.Tk) -> bool:
        """Apply the modern theme to the root window and configure ttk styles.
        
        Args:
            root: Root Tkinter window
            
        Returns:
            True if theme was applied successfully, False otherwise
        """
        try:
            self._root = root
            logger.debug("Starting theme application process")
            
            # Configure root window with error handling
            if not self._configure_root_window():
                logger.warning("Root window configuration failed, continuing with fallback")
            
            # Configure ttk styles with error handling
            if not self._configure_ttk_styles():
                logger.warning("TTK styles configuration failed, continuing with fallback")
            
            # Configure standard Tkinter widget defaults with error handling
            if not self._configure_tk_defaults():
                logger.warning("Tkinter defaults configuration failed, continuing with fallback")
            
            self._theme_applied = True
            logger.info("Modern theme applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Critical failure during theme application: {e}")
            self._apply_fallback_theme()
            return False
    
    def _configure_root_window(self) -> bool:
        """Configure the root window with theme settings.
        
        Returns:
            True if configuration was successful, False otherwise
        """
        if not self._root:
            logger.error("No root window available for configuration")
            return False
            
        try:
            # Set window background with fallback
            try:
                self._root.configure(bg=self.theme.bg_primary)
            except Exception as e:
                logger.warning(f"Failed to set window background color: {e}")
                try:
                    self._root.configure(bg="#2b2b2b")  # Fallback color
                except Exception as e2:
                    logger.error(f"Failed to set fallback background color: {e2}")
                    return False
            
            # Set window size and constraints with error handling
            try:
                self._root.geometry(f"{self.theme.window_width}x{self.theme.window_height}")
            except Exception as e:
                logger.warning(f"Failed to set window geometry: {e}")
                try:
                    self._root.geometry("400x300")  # Fallback size
                except Exception as e2:
                    logger.error(f"Failed to set fallback geometry: {e2}")
            
            try:
                self._root.minsize(self.theme.window_min_width, self.theme.window_min_height)
            except Exception as e:
                logger.warning(f"Failed to set minimum window size: {e}")
                try:
                    self._root.minsize(350, 250)  # Fallback minimum size
                except Exception as e2:
                    logger.error(f"Failed to set fallback minimum size: {e2}")
            
            logger.debug("Root window configured with theme settings")
            return True
            
        except Exception as e:
            logger.error(f"Critical error configuring root window: {e}")
            return False
    
    def _configure_ttk_styles(self) -> bool:
        """Configure ttk widget styles with modern theme.
        
        Returns:
            True if configuration was successful, False otherwise
        """
        if not self._root:
            logger.error("No root window available for TTK style configuration")
            return False
            
        try:
            self._style = ttk.Style(self._root)
        except Exception as e:
            logger.error(f"Failed to create TTK Style object: {e}")
            return False
        
        # Configure ttk theme base with comprehensive error handling
        try:
            # Try to use a modern ttk theme as base
            available_themes = self._style.theme_names()
            logger.debug(f"Available TTK themes: {available_themes}")
            
            if "clam" in available_themes:
                self._style.theme_use("clam")
                logger.debug("Using 'clam' TTK theme as base")
            elif "alt" in available_themes:
                self._style.theme_use("alt")
                logger.debug("Using 'alt' TTK theme as base")
            elif "default" in available_themes:
                self._style.theme_use("default")
                logger.debug("Using 'default' TTK theme as base")
            else:
                logger.warning("No suitable TTK base theme found, using system default")
        except Exception as e:
            logger.warning(f"Could not set ttk base theme: {e}, continuing with system default")
        
        # Configure Frame styles with error handling
        try:
            self._style.configure(
                "Modern.TFrame",
                background=self.theme.bg_primary,
                borderwidth=0
            )
            
            self._style.configure(
                "ModernSecondary.TFrame",
                background=self.theme.bg_secondary,
                borderwidth=self.theme.border_width,
                relief="solid"
            )
            logger.debug("Frame styles configured successfully")
        except Exception as e:
            logger.warning(f"Failed to configure Frame styles: {e}")
            # Apply basic fallback frame styles
            try:
                self._style.configure("Modern.TFrame", background="#2b2b2b")
                self._style.configure("ModernSecondary.TFrame", background="#3c3c3c")
            except Exception as e2:
                logger.error(f"Failed to apply fallback Frame styles: {e2}")
        
        # Configure LabelFrame styles
        self._style.configure(
            "Modern.TLabelframe",
            background=self.theme.bg_primary,
            foreground=self.theme.text_primary,
            borderwidth=self.theme.border_width,
            relief="solid",
            labelmargins=(self.theme.spacing_medium, 0, 0, 0)
        )
        
        self._style.configure(
            "Modern.TLabelframe.Label",
            background=self.theme.bg_primary,
            foreground=self.theme.text_secondary,
            font=self.theme.get_font(self.theme.font_size_small, self.theme.font_weight_medium)
        )
        
        # Configure Label styles
        self._style.configure(
            "Modern.TLabel",
            background=self.theme.bg_primary,
            foreground=self.theme.text_primary,
            font=self.theme.get_font()
        )
        
        self._style.configure(
            "ModernTitle.TLabel",
            background=self.theme.bg_primary,
            foreground=self.theme.text_primary,
            font=self.theme.get_font(self.theme.font_size_title, self.theme.font_weight_medium)
        )
        
        self._style.configure(
            "ModernSecondary.TLabel",
            background=self.theme.bg_primary,
            foreground=self.theme.text_secondary,
            font=self.theme.get_font(self.theme.font_size_small)
        )
        
        # Configure Now Playing display label style
        self._style.configure(
            "ModernNowPlaying.TLabel",
            background=self.theme.bg_secondary,
            foreground=self.theme.text_primary,
            font=self.theme.get_font(self.theme.font_size_body, self.theme.font_weight_medium),
            anchor="w",
            padding=(self.theme.spacing_medium, self.theme.spacing_small)
        )
        
        # Configure Button styles
        self._style.configure(
            "Modern.TButton",
            background=self.theme.bg_secondary,
            foreground=self.theme.text_primary,
            borderwidth=self.theme.border_width,
            relief="flat",
            font=self.theme.get_font(self.theme.font_size_small),
            focuscolor="none"
        )
        
        self._style.map(
            "Modern.TButton",
            background=[
                ("active", self.theme.bg_tertiary),
                ("pressed", self.theme.accent),
                ("disabled", self.theme.bg_primary)
            ],
            foreground=[
                ("disabled", self.theme.text_secondary)
            ]
        )
        
        # Configure Control Button styles (specialized for playback controls)
        self._style.configure(
            "ModernControl.TButton",
            background=self.theme.bg_secondary,
            foreground=self.theme.text_primary,
            borderwidth=self.theme.border_width,
            relief="flat",
            font=self.theme.get_font(self.theme.font_size_body),
            focuscolor="none",
            width=3,  # Fixed width for consistent button sizing
            padding=(2, 2)  # Compact padding for 24x24px buttons
        )
        
        self._style.map(
            "ModernControl.TButton",
            background=[
                ("active", self.theme.bg_tertiary),
                ("pressed", self.theme.accent),
                ("disabled", self.theme.bg_primary),
                ("selected", self.theme.accent)  # For active/current state
            ],
            foreground=[
                ("disabled", self.theme.text_secondary),
                ("selected", self.theme.text_primary)
            ]
        )
        
        # Configure Active Control Button style (for currently active button)
        self._style.configure(
            "ModernControlActive.TButton",
            background=self.theme.accent,
            foreground=self.theme.text_primary,
            borderwidth=self.theme.border_width,
            relief="flat",
            font=self.theme.get_font(self.theme.font_size_body),
            focuscolor="none",
            width=3,
            padding=(2, 2)
        )
        
        self._style.map(
            "ModernControlActive.TButton",
            background=[
                ("active", self.theme.accent),
                ("pressed", self.theme.bg_tertiary),
                ("disabled", self.theme.bg_primary)
            ],
            foreground=[
                ("disabled", self.theme.text_secondary)
            ]
        )
        
        # Configure File Management Button styles (compact 80x24px with modern flat design)
        self._style.configure(
            "ModernFile.TButton",
            background=self.theme.bg_secondary,
            foreground=self.theme.text_primary,
            borderwidth=self.theme.border_width,
            relief="flat",
            font=self.theme.get_font(self.theme.font_size_small),
            focuscolor="none",
            width=10,  # Character width for 80px buttons
            padding=(4, 2)  # Compact padding for 24px height
        )
        
        self._style.map(
            "ModernFile.TButton",
            background=[
                ("active", self.theme.bg_tertiary),  # Smooth hover effect
                ("pressed", self.theme.accent),
                ("disabled", self.theme.bg_primary)
            ],
            foreground=[
                ("disabled", self.theme.text_secondary)
            ],
            bordercolor=[
                ("active", self.theme.bg_tertiary),  # Subtle border on hover
                ("pressed", self.theme.accent)
            ]
        )
        
        # Configure Checkbutton styles
        self._style.configure(
            "Modern.TCheckbutton",
            background=self.theme.bg_primary,
            foreground=self.theme.text_primary,
            font=self.theme.get_font(self.theme.font_size_small),
            focuscolor="none"
        )
        
        self._style.map(
            "Modern.TCheckbutton",
            background=[("active", self.theme.bg_primary)],
            indicatorcolor=[
                ("selected", self.theme.accent),
                ("!selected", self.theme.bg_secondary)
            ]
        )
        
        # Configure Scrollbar styles
        self._style.configure(
            "Modern.Vertical.TScrollbar",
            background=self.theme.bg_secondary,
            troughcolor=self.theme.bg_primary,
            borderwidth=0,
            arrowcolor=self.theme.text_secondary,
            darkcolor=self.theme.bg_secondary,
            lightcolor=self.theme.bg_secondary
        )
        
        self._style.map(
            "Modern.Vertical.TScrollbar",
            background=[("active", self.theme.bg_tertiary)]
        )
        
        logger.debug("TTK styles configured")
        return True
    
    def _configure_tk_defaults(self) -> bool:
        """Configure default options for standard Tkinter widgets.
        
        Returns:
            True if configuration was successful, False otherwise
        """
        if not self._root:
            logger.error("No root window available for Tkinter defaults configuration")
            return False
            
        try:
            # Configure default options for Listbox with error handling
            try:
                self._root.option_add("*Listbox.background", self.theme.bg_secondary)
                self._root.option_add("*Listbox.foreground", self.theme.text_primary)
                self._root.option_add("*Listbox.selectBackground", self.theme.accent)
                self._root.option_add("*Listbox.selectForeground", self.theme.text_primary)
                self._root.option_add("*Listbox.font", f'"{self.theme.font_family}" {self.theme.font_size_small}')
                self._root.option_add("*Listbox.borderWidth", "0")
                self._root.option_add("*Listbox.highlightThickness", "0")
                logger.debug("Listbox defaults configured successfully")
            except Exception as e:
                logger.warning(f"Failed to configure Listbox defaults: {e}")
                # Apply basic fallback options
                try:
                    self._root.option_add("*Listbox.background", "#3c3c3c")
                    self._root.option_add("*Listbox.foreground", "#ffffff")
                    self._root.option_add("*Listbox.selectBackground", "#4a9eff")
                except Exception as e2:
                    logger.error(f"Failed to apply fallback Listbox defaults: {e2}")
            
            logger.debug("Tkinter defaults configured")
            return True
            
        except Exception as e:
            logger.error(f"Critical error configuring Tkinter defaults: {e}")
            return False
    
    def _apply_fallback_theme(self) -> None:
        """Apply a basic fallback theme if the main theme fails."""
        logger.warning("Applying fallback theme due to main theme failure")
        
        try:
            if self._root:
                # Basic dark theme fallback with comprehensive error handling
                try:
                    self._root.configure(bg="#2b2b2b")
                    logger.debug("Fallback root background applied")
                except Exception as e:
                    logger.error(f"Failed to set fallback root background: {e}")
                
                # Basic ttk configuration with error handling
                try:
                    if not self._style:
                        self._style = ttk.Style(self._root)
                    
                    # Apply minimal fallback styles
                    fallback_styles = [
                        ("TFrame", {"background": "#2b2b2b"}),
                        ("TLabel", {"background": "#2b2b2b", "foreground": "#ffffff"}),
                        ("TButton", {"background": "#3c3c3c", "foreground": "#ffffff"}),
                        ("Modern.TFrame", {"background": "#2b2b2b"}),
                        ("ModernSecondary.TFrame", {"background": "#3c3c3c"}),
                        ("Modern.TLabel", {"background": "#2b2b2b", "foreground": "#ffffff"}),
                        ("Modern.TButton", {"background": "#3c3c3c", "foreground": "#ffffff"}),
                    ]
                    
                    for style_name, config in fallback_styles:
                        try:
                            self._style.configure(style_name, **config)
                        except Exception as e:
                            logger.warning(f"Failed to apply fallback style {style_name}: {e}")
                    
                    logger.debug("Fallback TTK styles applied")
                    
                except Exception as e:
                    logger.error(f"Failed to configure fallback TTK styles: {e}")
                
                # Apply basic Tkinter option database fallbacks
                try:
                    fallback_options = [
                        ("*Listbox.background", "#3c3c3c"),
                        ("*Listbox.foreground", "#ffffff"),
                        ("*Listbox.selectBackground", "#4a9eff"),
                        ("*Listbox.selectForeground", "#ffffff"),
                    ]
                    
                    for option, value in fallback_options:
                        try:
                            self._root.option_add(option, value)
                        except Exception as e:
                            logger.warning(f"Failed to apply fallback option {option}: {e}")
                    
                    logger.debug("Fallback Tkinter options applied")
                    
                except Exception as e:
                    logger.error(f"Failed to configure fallback Tkinter options: {e}")
                
                # Mark theme as applied even if it's just the fallback
                self._theme_applied = True
                logger.info("Fallback theme applied successfully")
                
        except Exception as e:
            logger.error(f"Critical failure applying fallback theme: {e}")
            # Last resort: mark theme as not applied
            self._theme_applied = False
    
    def get_listbox_config(self) -> Dict[str, Any]:
        """Get configuration dictionary for Listbox widgets.
        
        Returns:
            Dictionary of configuration options for Listbox widgets
        """
        try:
            # Try to create a proper font tuple
            font_config = (self.theme.font_family, self.theme.font_size_small)
        except Exception:
            # Fallback to string format
            font_config = f'"{self.theme.font_family}" {self.theme.font_size_small}'
            
        return {
            "bg": self.theme.bg_secondary,
            "fg": self.theme.text_primary,
            "selectbackground": self.theme.accent,
            "selectforeground": self.theme.text_primary,
            "font": font_config,
            "borderwidth": 0,
            "highlightthickness": 0,
            "activestyle": "none"
        }
    
    def get_hyperlink_config(self) -> Dict[str, Any]:
        """Get configuration dictionary for hyperlink labels.
        
        Returns:
            Dictionary of configuration options for hyperlink labels
        """
        return {
            "bg": self.theme.bg_primary,
            "fg": self.theme.accent,
            "font": (self.theme.font_family, self.theme.font_size_small),
            "cursor": "hand2"
        }
    
    def get_music_note_config(self) -> Dict[str, Any]:
        """Get configuration for music note indicator.
        
        Returns:
            Dictionary with music note styling configuration
        """
        return {
            "symbol": "♪",
            "color": self.theme.success,
            "font": (self.theme.font_family, self.theme.font_size_small, self.theme.font_weight_medium)
        }
    
    def get_alternating_row_colors(self) -> Tuple[str, str]:
        """Get alternating row colors for better readability.
        
        Returns:
            Tuple of (primary_row_color, alternate_row_color)
        """
        return (self.theme.bg_secondary, self.theme.bg_primary)
    
    def create_modern_frame(self, parent: tk.Widget, **kwargs) -> ttk.Frame:
        """Create a frame with modern styling.
        
        Args:
            parent: Parent widget
            **kwargs: Additional configuration options
            
        Returns:
            Configured ttk.Frame with modern styling
        """
        style = kwargs.pop("style", "Modern.TFrame")
        frame = ttk.Frame(parent, style=style, **kwargs)
        return frame
    
    def create_modern_label(self, parent: tk.Widget, text: str = "", style_type: str = "normal", **kwargs) -> ttk.Label:
        """Create a label with modern styling.
        
        Args:
            parent: Parent widget
            text: Label text
            style_type: Style type ("normal", "title", "secondary", "now_playing")
            **kwargs: Additional configuration options
            
        Returns:
            Configured ttk.Label with modern styling
        """
        style_map = {
            "normal": "Modern.TLabel",
            "title": "ModernTitle.TLabel",
            "secondary": "ModernSecondary.TLabel",
            "now_playing": "ModernNowPlaying.TLabel"
        }
        
        style = kwargs.pop("style", style_map.get(style_type, "Modern.TLabel"))
        label = ttk.Label(parent, text=text, style=style, **kwargs)
        return label
    
    def create_modern_button(self, parent: tk.Widget, text: str = "", **kwargs) -> ttk.Button:
        """Create a button with modern styling.
        
        Args:
            parent: Parent widget
            text: Button text
            **kwargs: Additional configuration options
            
        Returns:
            Configured ttk.Button with modern styling
        """
        style = kwargs.pop("style", "Modern.TButton")
        button = ttk.Button(parent, text=text, style=style, **kwargs)
        return button
    
    def create_modern_control_button(self, parent: tk.Widget, text: str = "", **kwargs) -> ttk.Button:
        """Create a control button with specialized modern styling for playback controls.
        
        Args:
            parent: Parent widget
            text: Button text (usually Unicode symbols for playback controls)
            **kwargs: Additional configuration options
            
        Returns:
            Configured ttk.Button with modern control styling
        """
        style = kwargs.pop("style", "ModernControl.TButton")
        button = ttk.Button(parent, text=text, style=style, **kwargs)
        return button
    
    def create_modern_file_button(self, parent: tk.Widget, text: str = "", **kwargs) -> ttk.Button:
        """Create a file management button with compact modern styling (80x24px).
        
        Args:
            parent: Parent widget
            text: Button text
            **kwargs: Additional configuration options
            
        Returns:
            Configured ttk.Button with modern file management styling
        """
        style = kwargs.pop("style", "ModernFile.TButton")
        button = ttk.Button(parent, text=text, style=style, **kwargs)
        return button
    
    def create_modern_checkbutton(self, parent: tk.Widget, text: str = "", **kwargs) -> ttk.Checkbutton:
        """Create a checkbutton with modern styling.
        
        Args:
            parent: Parent widget
            text: Checkbutton text
            **kwargs: Additional configuration options
            
        Returns:
            Configured ttk.Checkbutton with modern styling
        """
        style = kwargs.pop("style", "Modern.TCheckbutton")
        checkbutton = ttk.Checkbutton(parent, text=text, style=style, **kwargs)
        return checkbutton
    
    def create_modern_listbox(self, parent: tk.Widget, **kwargs) -> tk.Listbox:
        """Create a listbox with modern styling and compact row height.
        
        Args:
            parent: Parent widget
            **kwargs: Additional configuration options
            
        Returns:
            Configured tk.Listbox with modern styling
        """
        try:
            # Create listbox with basic configuration first
            listbox = tk.Listbox(parent, **kwargs)
            logger.debug("Basic listbox created successfully")
        except Exception as e:
            logger.error(f"Failed to create basic listbox: {e}")
            # Return a minimal listbox as fallback
            try:
                return tk.Listbox(parent)
            except Exception as e2:
                logger.error(f"Failed to create fallback listbox: {e2}")
                raise
        
        # Apply modern styling with compact font size (10px as per requirements)
        try:
            # Try to apply full modern styling
            font_config = (self.theme.font_family, 10, self.theme.font_weight_regular)
            listbox.configure(
                bg=self.theme.bg_secondary,
                fg=self.theme.text_primary,
                selectbackground=self.theme.accent,
                selectforeground=self.theme.text_primary,
                font=font_config,  # 10px regular weight
                borderwidth=0,
                highlightthickness=0,
                activestyle="none"
            )
            logger.debug("Full listbox styling applied successfully")
        except Exception as e:
            logger.warning(f"Could not apply full listbox styling: {e}")
            # Apply fallback styling step by step
            fallback_configs = [
                ("bg", self.theme.bg_secondary, "#3c3c3c"),
                ("fg", self.theme.text_primary, "#ffffff"),
                ("selectbackground", self.theme.accent, "#4a9eff"),
                ("selectforeground", self.theme.text_primary, "#ffffff"),
                ("borderwidth", 0, 0),
                ("highlightthickness", 0, 0),
                ("activestyle", "none", "none")
            ]
            
            for config_name, theme_value, fallback_value in fallback_configs:
                try:
                    listbox.configure(**{config_name: theme_value})
                except Exception as e2:
                    logger.warning(f"Failed to set {config_name} to theme value, trying fallback: {e2}")
                    try:
                        listbox.configure(**{config_name: fallback_value})
                    except Exception as e3:
                        logger.warning(f"Failed to set {config_name} to fallback value: {e3}")
            
            # Try to apply font separately
            try:
                listbox.configure(font=(self.theme.font_family, 10))
            except Exception as e:
                logger.warning(f"Failed to set theme font, trying fallback: {e}")
                try:
                    listbox.configure(font=("Arial", 10))
                except Exception as e2:
                    logger.warning(f"Failed to set fallback font: {e2}")
        
        return listbox
    
    def create_modern_scrollbar(self, parent: tk.Widget, **kwargs) -> ttk.Scrollbar:
        """Create a scrollbar with modern styling.
        
        Args:
            parent: Parent widget
            **kwargs: Additional configuration options
            
        Returns:
            Configured ttk.Scrollbar with modern styling
        """
        style = kwargs.pop("style", "Modern.Vertical.TScrollbar")
        scrollbar = ttk.Scrollbar(parent, style=style, **kwargs)
        return scrollbar
    
    def create_modern_playlist_widget(self, parent: tk.Widget, **kwargs):
        """Create a modern playlist widget with alternating row colors and compact design.
        
        Args:
            parent: Parent widget
            **kwargs: Additional configuration options
            
        Returns:
            Custom playlist widget with modern styling
        """
        from gui.modern_playlist import ModernPlaylistWidget
        return ModernPlaylistWidget(parent, self, **kwargs)
    
    def create_modern_hyperlink(self, parent: tk.Widget, text: str = "", url: str = "", **kwargs) -> tk.Label:
        """Create a hyperlink label with modern styling and interaction support.
        
        Args:
            parent: Parent widget
            text: Display text for the hyperlink
            url: URL that the hyperlink points to
            **kwargs: Additional configuration options
            
        Returns:
            Configured tk.Label styled as a hyperlink with click and context menu support
        """
        try:
            # Get hyperlink configuration with error handling
            try:
                config = self.get_hyperlink_config()
                config.update(kwargs)
                logger.debug("Hyperlink configuration retrieved successfully")
            except Exception as e:
                logger.warning(f"Failed to get hyperlink config, using fallback: {e}")
                config = {
                    "bg": "#2b2b2b",
                    "fg": "#4a9eff",
                    "font": ("Arial", 9),
                    "cursor": "hand2"
                }
                config.update(kwargs)
            
            # Create the label with error handling
            try:
                hyperlink = tk.Label(parent, text=text, **config)
                logger.debug("Hyperlink label created successfully")
            except Exception as e:
                logger.warning(f"Failed to create hyperlink with full config, trying minimal: {e}")
                # Try with minimal configuration
                hyperlink = tk.Label(parent, text=text, fg="#4a9eff", cursor="hand2")
            
            # Store the URL as an attribute for later use
            hyperlink.url = url
            
            # Add underline to indicate it's clickable with error handling
            try:
                font_config = list(config.get("font", (self.theme.font_family, self.theme.font_size_small)))
                if len(font_config) == 2:
                    font_config.append("underline")
                elif len(font_config) == 3:
                    # Add underline to existing weight
                    font_config[2] = f"{font_config[2]} underline"
                else:
                    font_config = (self.theme.font_family, self.theme.font_size_small, "underline")
                
                hyperlink.configure(font=font_config)
                logger.debug("Hyperlink underline styling applied successfully")
            except Exception as e:
                logger.warning(f"Failed to apply hyperlink underline styling: {e}")
                # Try fallback underline font
                try:
                    hyperlink.configure(font=("Arial", 9, "underline"))
                except Exception as e2:
                    logger.warning(f"Failed to apply fallback underline font: {e2}")
            
            return hyperlink
            
        except Exception as e:
            logger.error(f"Critical error creating hyperlink: {e}")
            # Last resort: create a basic label
            try:
                hyperlink = tk.Label(parent, text=text, fg="blue")
                hyperlink.url = url
                return hyperlink
            except Exception as e2:
                logger.error(f"Failed to create fallback hyperlink: {e2}")
                raise
    
    def create_now_playing_frame(self, parent: tk.Widget, **kwargs) -> ttk.Frame:
        """Create a specialized frame for the Now Playing display with modern styling.
        
        Args:
            parent: Parent widget
            **kwargs: Additional configuration options
            
        Returns:
            Configured ttk.Frame optimized for Now Playing display
        """
        # Use secondary background frame style for the Now Playing area
        style = kwargs.pop("style", "ModernSecondary.TFrame")
        frame = ttk.Frame(parent, style=style, **kwargs)
        return frame
    
    def is_theme_applied(self) -> bool:
        """Check if the theme has been successfully applied.
        
        Returns:
            True if theme is applied, False otherwise
        """
        return self._theme_applied
    
    def get_theme(self) -> ModernTheme:
        """Get the current theme instance.
        
        Returns:
            Current ModernTheme instance
        """
        return self.theme
    
    def truncate_text(self, text: str, max_width: int, font_config: tuple = None) -> str:
        """Truncate text to fit within specified width with ellipsis.
        
        Args:
            text: Text to truncate
            max_width: Maximum width in pixels
            font_config: Font configuration tuple (family, size, weight)
            
        Returns:
            Truncated text with ellipsis if needed
        """
        if not text or not self._root:
            return text
            
        try:
            # Use provided font or default
            if font_config is None:
                font_config = self.theme.get_font()
            
            # Create a temporary label to measure text width
            temp_label = tk.Label(self._root, font=font_config)
            
            # Check if text fits
            temp_label.config(text=text)
            temp_label.update_idletasks()
            text_width = temp_label.winfo_reqwidth()
            
            if text_width <= max_width:
                temp_label.destroy()
                return text
            
            # Binary search for optimal truncation point
            left, right = 0, len(text)
            best_text = text
            
            while left <= right:
                mid = (left + right) // 2
                truncated = text[:mid] + "..." if mid < len(text) else text
                
                temp_label.config(text=truncated)
                temp_label.update_idletasks()
                truncated_width = temp_label.winfo_reqwidth()
                
                if truncated_width <= max_width:
                    best_text = truncated
                    left = mid + 1
                else:
                    right = mid - 1
            
            temp_label.destroy()
            return best_text
            
        except Exception as e:
            logger.warning(f"Text truncation failed: {e}")
            # Enhanced fallback with multiple strategies
            try:
                # Strategy 1: Simple character-based truncation based on max_width
                if max_width > 0:
                    # Rough estimate: 8 pixels per character for most fonts
                    max_chars = max(10, max_width // 8)
                    if len(text) > max_chars:
                        return text[:max_chars-3] + "..."
                
                # Strategy 2: Fixed character limit fallback
                if len(text) > 50:
                    return text[:47] + "..."
                    
                return text
                
            except Exception as e2:
                logger.error(f"Fallback text truncation also failed: {e2}")
                # Last resort: return first 30 characters
                return text[:30] if len(text) > 30 else text
    
    def __str__(self) -> str:
        """String representation of the theme manager."""
        return f"ThemeManager(theme_applied={self._theme_applied})"
    
    def __repr__(self) -> str:
        """Developer representation of the theme manager."""
        return f"ThemeManager(theme={self.theme}, applied={self._theme_applied})"


# Global theme manager instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance.
    
    Returns:
        Global ThemeManager instance
    """
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def apply_modern_theme(root: tk.Tk, theme: Optional[ModernTheme] = None) -> bool:
    """Apply modern theme to a Tkinter root window.
    
    Args:
        root: Root Tkinter window
        theme: Optional ModernTheme instance (uses default if None)
        
    Returns:
        True if theme was applied successfully, False otherwise
    """
    global _theme_manager
    
    if theme:
        _theme_manager = ThemeManager(theme)
    else:
        _theme_manager = get_theme_manager()
    
    return _theme_manager.apply_theme(root)


def create_modern_widget(widget_type: str, parent: tk.Widget, **kwargs):
    """Factory function to create modern-styled widgets.
    
    Args:
        widget_type: Type of widget to create
        parent: Parent widget
        **kwargs: Widget configuration options
        
    Returns:
        Configured widget with modern styling
    """
    theme_manager = get_theme_manager()
    
    widget_creators = {
        "frame": theme_manager.create_modern_frame,
        "label": theme_manager.create_modern_label,
        "button": theme_manager.create_modern_button,
        "checkbutton": theme_manager.create_modern_checkbutton,
        "listbox": theme_manager.create_modern_listbox,
        "scrollbar": theme_manager.create_modern_scrollbar
    }
    
    creator = widget_creators.get(widget_type.lower())
    if creator:
        return creator(parent, **kwargs)
    else:
        raise ValueError(f"Unsupported widget type: {widget_type}")