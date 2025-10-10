"""
Branding configuration for the OBSmusic application.

This module provides branding configuration including icon paths,
application titles, and branding-related utilities.
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class BrandingConfig:
    """Configuration for application branding and icons."""
    
    app_title: str = "OBSmusic"
    icon_path: str = "OBSmusic.ico"
    window_icon_size: Tuple[int, int] = (32, 32)
    favicon_size: Tuple[int, int] = (16, 16)
    
    def get_icon_path(self) -> Path:
        """Get absolute path to icon file."""
        return Path(self.icon_path).resolve()
    
    def icon_exists(self) -> bool:
        """Check if icon file exists."""
        return self.get_icon_path().exists()
    
    def get_icon_path_str(self) -> str:
        """Get icon path as string for Tkinter."""
        return str(self.get_icon_path())


class BrandingManager:
    """Manages application branding including icons and titles."""
    
    def __init__(self, config: Optional[BrandingConfig] = None):
        """Initialize the branding manager.
        
        Args:
            config: BrandingConfig instance (creates default if None)
        """
        self.config = config or BrandingConfig()
        logger.debug("BrandingManager initialized")
    
    def apply_window_branding(self, window) -> bool:
        """Apply branding to a Tkinter window.
        
        Args:
            window: Tkinter window (Tk or Toplevel)
            
        Returns:
            True if branding was applied successfully, False otherwise
        """
        success = True
        
        # Set window title
        try:
            window.title(self.config.app_title)
            logger.debug(f"Window title set to: {self.config.app_title}")
        except Exception as e:
            logger.error(f"Failed to set window title: {e}")
            success = False
        
        # Set window icon
        if not self._set_window_icon(window):
            success = False
        
        return success
    
    def _set_window_icon(self, window) -> bool:
        """Set window icon with graceful fallback.
        
        Args:
            window: Tkinter window
            
        Returns:
            True if icon was set successfully, False otherwise
        """
        if not self.config.icon_exists():
            logger.warning(f"Icon file not found: {self.config.get_icon_path()}")
            return False
        
        try:
            # Try to set the icon
            icon_path = self.config.get_icon_path_str()
            window.iconbitmap(icon_path)
            logger.debug(f"Window icon set to: {icon_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set window icon: {e}")
            
            # Try alternative method for some systems
            try:
                import tkinter as tk
                if hasattr(tk, 'PhotoImage'):
                    # This might work on some systems where iconbitmap fails
                    photo = tk.PhotoImage(file=self.config.get_icon_path_str())
                    window.iconphoto(True, photo)
                    logger.debug("Window icon set using iconphoto method")
                    return True
            except Exception as e2:
                logger.error(f"Alternative icon method also failed: {e2}")
            
            return False
    
    def get_favicon_data(self) -> Optional[bytes]:
        """Get favicon data for web servers.
        
        Returns:
            Icon file data as bytes, or None if not available
        """
        if not self.config.icon_exists():
            logger.warning("Icon file not found for favicon")
            return None
        
        try:
            with open(self.config.get_icon_path(), 'rb') as f:
                data = f.read()
            logger.debug("Favicon data loaded successfully")
            return data
        except Exception as e:
            logger.error(f"Failed to read icon file for favicon: {e}")
            return None
    
    def get_favicon_path(self) -> Optional[str]:
        """Get favicon file path for web servers.
        
        Returns:
            Path to icon file as string, or None if not available
        """
        if not self.config.icon_exists():
            return None
        return self.config.get_icon_path_str()


# Global branding manager instance
_branding_manager = None


def get_branding_manager() -> BrandingManager:
    """Get the global branding manager instance.
    
    Returns:
        BrandingManager instance
    """
    global _branding_manager
    if _branding_manager is None:
        _branding_manager = BrandingManager()
    return _branding_manager


def apply_window_branding(window) -> bool:
    """Apply branding to a window using the global branding manager.
    
    Args:
        window: Tkinter window
        
    Returns:
        True if branding was applied successfully, False otherwise
    """
    return get_branding_manager().apply_window_branding(window)