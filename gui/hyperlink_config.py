"""
Dynamic hyperlink configuration system for web interface URLs.

This module provides dynamic URL generation based on runtime port configuration
and server availability, supporting the modernized GUI hyperlink system.
"""

import logging
from dataclasses import dataclass
from typing import Optional, Dict, Tuple
import socket

logger = logging.getLogger(__name__)


@dataclass
class HyperlinkConfig:
    """Configuration for dynamic hyperlink URL generation.
    
    Manages port configuration and provides dynamic URL generation
    based on current web server and controls server ports.
    """
    
    web_server_port: int = 8080
    controls_server_port: int = 8081
    host: str = "localhost"
    
    def get_display_url(self) -> str:
        """Generate display URL based on current web server port.
        
        Returns:
            Complete URL for the web display interface
        """
        return f"http://{self.host}:{self.web_server_port}"
    
    def get_controls_url(self) -> str:
        """Generate controls URL based on current controls server port.
        
        Returns:
            Complete URL for the web controls interface
        """
        return f"http://{self.host}:{self.controls_server_port}"
    
    def update_ports(self, web_port: int, controls_port: int) -> bool:
        """Update ports and return True if changed.
        
        Args:
            web_port: New web server port
            controls_port: New controls server port
            
        Returns:
            True if ports were changed, False if they remained the same
        """
        changed = (self.web_server_port != web_port or 
                  self.controls_server_port != controls_port)
        self.web_server_port = web_port
        self.controls_server_port = controls_port
        return changed
    
    def get_urls(self) -> Dict[str, str]:
        """Get both URLs as a dictionary.
        
        Returns:
            Dictionary with 'display' and 'controls' URLs
        """
        return {
            'display': self.get_display_url(),
            'controls': self.get_controls_url()
        }


class DynamicHyperlinkManager:
    """Manages dynamic hyperlink URL generation and server port detection.
    
    Provides real-time URL generation based on server port configuration
    and handles fallback scenarios when servers are not accessible.
    """
    
    def __init__(self, config: Optional[HyperlinkConfig] = None):
        """Initialize the dynamic hyperlink manager.
        
        Args:
            config: HyperlinkConfig instance (creates default if None)
        """
        self.config = config or HyperlinkConfig()
        self._last_known_ports = (self.config.web_server_port, self.config.controls_server_port)
        
        logger.debug("DynamicHyperlinkManager initialized")
    
    def detect_server_ports(self, web_server=None, controls_server=None) -> Tuple[int, int]:
        """Detect current server ports from running server instances.
        
        Args:
            web_server: WebServer instance (optional)
            controls_server: ControlsServer instance (optional)
            
        Returns:
            Tuple of (web_port, controls_port)
        """
        web_port = self.config.web_server_port  # Default fallback
        controls_port = self.config.controls_server_port  # Default fallback
        
        try:
            # Try to get port from web server instance
            if web_server and hasattr(web_server, 'port'):
                if web_server.is_running:
                    web_port = web_server.port
                    logger.debug(f"Detected web server port: {web_port}")
                else:
                    logger.debug("Web server not running, using configured port")
            elif web_server and hasattr(web_server, 'get_current_port'):
                # Alternative method if server has get_current_port method
                try:
                    detected_port = web_server.get_current_port()
                    if detected_port:
                        web_port = detected_port
                        logger.debug(f"Detected web server port via get_current_port: {web_port}")
                except Exception as e:
                    logger.warning(f"Failed to get web server port via get_current_port: {e}")
            
            # Try to get port from controls server instance
            if controls_server and hasattr(controls_server, 'port'):
                if controls_server.is_running:
                    controls_port = controls_server.port
                    logger.debug(f"Detected controls server port: {controls_port}")
                else:
                    logger.debug("Controls server not running, using configured port")
            elif controls_server and hasattr(controls_server, 'get_current_port'):
                # Alternative method if server has get_current_port method
                try:
                    detected_port = controls_server.get_current_port()
                    if detected_port:
                        controls_port = detected_port
                        logger.debug(f"Detected controls server port via get_current_port: {controls_port}")
                except Exception as e:
                    logger.warning(f"Failed to get controls server port via get_current_port: {e}")
            
        except Exception as e:
            logger.warning(f"Error during server port detection: {e}")
            # Fall back to last known ports or defaults
            web_port, controls_port = self._last_known_ports
        
        # Store as last known ports for future fallback
        self._last_known_ports = (web_port, controls_port)
        
        return web_port, controls_port
    
    def update_from_servers(self, web_server=None, controls_server=None) -> bool:
        """Update hyperlink configuration from server instances.
        
        Args:
            web_server: WebServer instance (optional)
            controls_server: ControlsServer instance (optional)
            
        Returns:
            True if URLs were updated, False if they remained the same
        """
        try:
            web_port, controls_port = self.detect_server_ports(web_server, controls_server)
            changed = self.config.update_ports(web_port, controls_port)
            
            if changed:
                logger.info(f"Updated hyperlink URLs - Display: {self.config.get_display_url()}, "
                           f"Controls: {self.config.get_controls_url()}")
            else:
                logger.debug("Hyperlink URLs unchanged after server update")
            
            return changed
            
        except Exception as e:
            logger.error(f"Error updating hyperlink configuration from servers: {e}")
            return False
    
    def get_current_urls(self) -> Dict[str, str]:
        """Get current URLs based on configuration.
        
        Returns:
            Dictionary with 'display' and 'controls' URLs
        """
        return self.config.get_urls()
    
    def refresh_hyperlink_display(self, hyperlink_widgets: Dict[str, any]) -> None:
        """Refresh hyperlink display widgets with current URLs.
        
        Args:
            hyperlink_widgets: Dictionary of hyperlink widgets to update
                              Expected keys: 'display', 'controls'
        """
        try:
            current_urls = self.get_current_urls()
            
            # Update display hyperlink
            if 'display' in hyperlink_widgets and hyperlink_widgets['display']:
                display_widget = hyperlink_widgets['display']
                display_url = current_urls['display']
                display_widget.configure(text=display_url)
                display_widget.url = display_url
                logger.debug(f"Updated display hyperlink to: {display_url}")
            
            # Update controls hyperlink
            if 'controls' in hyperlink_widgets and hyperlink_widgets['controls']:
                controls_widget = hyperlink_widgets['controls']
                controls_url = current_urls['controls']
                controls_widget.configure(text=controls_url)
                controls_widget.url = controls_url
                logger.debug(f"Updated controls hyperlink to: {controls_url}")
            
            logger.debug("Hyperlink display refreshed successfully")
            
        except Exception as e:
            logger.error(f"Error refreshing hyperlink display: {e}")
    
    def handle_server_unavailable(self) -> Dict[str, str]:
        """Handle scenario when servers are not running.
        
        Returns:
            Dictionary with fallback URLs based on default ports
        """
        try:
            # Use configured default ports as fallback
            fallback_urls = {
                'display': f"http://{self.config.host}:{self.config.web_server_port}",
                'controls': f"http://{self.config.host}:{self.config.controls_server_port}"
            }
            
            logger.info(f"Using fallback URLs - servers not available: {fallback_urls}")
            return fallback_urls
            
        except Exception as e:
            logger.error(f"Error generating fallback URLs: {e}")
            # Last resort fallback
            return {
                'display': "http://localhost:8080",
                'controls': "http://localhost:8081"
            }
    
    def is_port_available(self, port: int, host: str = None) -> bool:
        """Check if a port is available for binding.
        
        Args:
            port: Port number to check
            host: Host to check (defaults to config host)
            
        Returns:
            True if port is available, False if in use
        """
        if host is None:
            host = self.config.host
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                return True
        except OSError:
            return False
    
    def find_available_ports(self, start_web_port: int = 8080, start_controls_port: int = 8081) -> Tuple[int, int]:
        """Find available ports for web and controls servers.
        
        Args:
            start_web_port: Starting port for web server search
            start_controls_port: Starting port for controls server search
            
        Returns:
            Tuple of (available_web_port, available_controls_port)
        """
        web_port = start_web_port
        controls_port = start_controls_port
        
        # Find available web server port
        for port in range(start_web_port, start_web_port + 50):
            if self.is_port_available(port):
                web_port = port
                break
        
        # Find available controls server port (ensure it's different from web port)
        for port in range(start_controls_port, start_controls_port + 50):
            if port != web_port and self.is_port_available(port):
                controls_port = port
                break
        
        logger.debug(f"Found available ports - Web: {web_port}, Controls: {controls_port}")
        return web_port, controls_port
    
    def get_config(self) -> HyperlinkConfig:
        """Get the current hyperlink configuration.
        
        Returns:
            Current HyperlinkConfig instance
        """
        return self.config
    
    def __str__(self) -> str:
        """String representation of the hyperlink manager."""
        return f"DynamicHyperlinkManager(display={self.config.get_display_url()}, controls={self.config.get_controls_url()})"
    
    def __repr__(self) -> str:
        """Developer representation of the hyperlink manager."""
        return f"DynamicHyperlinkManager(config={self.config})"