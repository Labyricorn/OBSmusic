"""
Configuration manager for web display settings.
Handles persistence and validation of web display configuration.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class WebDisplayConfig:
    """Configuration settings for web display appearance."""
    font_family: str = "Arial"
    font_size: int = 24
    font_weight: str = "normal"
    background_color: str = "#000000"
    text_color: str = "#ffffff"
    accent_color: str = "#ff6b6b"
    show_artwork: bool = True
    artwork_size: int = 200
    layout: str = "horizontal"  # horizontal, vertical, overlay

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebDisplayConfig':
        """Create configuration from dictionary with validation."""
        # Create default config first
        config = cls()
        
        # Update with provided data, validating each field
        if 'font_family' in data and isinstance(data['font_family'], str):
            config.font_family = data['font_family']
        
        if 'font_size' in data and isinstance(data['font_size'], int) and data['font_size'] > 0:
            config.font_size = data['font_size']
        
        if 'font_weight' in data and data['font_weight'] in ['normal', 'bold', 'lighter', 'bolder']:
            config.font_weight = data['font_weight']
        
        if 'background_color' in data and isinstance(data['background_color'], str):
            if cls._is_valid_color(data['background_color']):
                config.background_color = data['background_color']
        
        if 'text_color' in data and isinstance(data['text_color'], str):
            if cls._is_valid_color(data['text_color']):
                config.text_color = data['text_color']
        
        if 'accent_color' in data and isinstance(data['accent_color'], str):
            if cls._is_valid_color(data['accent_color']):
                config.accent_color = data['accent_color']
        
        if 'show_artwork' in data and isinstance(data['show_artwork'], bool):
            config.show_artwork = data['show_artwork']
        
        if 'artwork_size' in data and isinstance(data['artwork_size'], int) and data['artwork_size'] > 0:
            config.artwork_size = data['artwork_size']
        
        if 'layout' in data and data['layout'] in ['horizontal', 'vertical', 'overlay']:
            config.layout = data['layout']
        
        return config

    @staticmethod
    def _is_valid_color(color: str) -> bool:
        """Validate hex color format."""
        if not color.startswith('#'):
            return False
        if len(color) not in [4, 7]:  # #RGB or #RRGGBB
            return False
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False


class ConfigManager:
    """Manages web display configuration persistence and validation."""
    
    def __init__(self, config_file: str = "data/config.json"):
        """Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self._config: Optional[WebDisplayConfig] = None
        self._ensure_data_directory()

    def _ensure_data_directory(self) -> None:
        """Ensure data directory exists."""
        data_dir = os.path.dirname(self.config_file)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)

    def load_config(self) -> WebDisplayConfig:
        """Load configuration from file or return default with error recovery.
        
        Returns:
            WebDisplayConfig: Loaded or default configuration
        """
        if self._config is not None:
            return self._config

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Validate the loaded data
                if not isinstance(data, dict):
                    raise ValueError("Configuration file contains invalid data format")
                
                self._config = WebDisplayConfig.from_dict(data)
                logger.info(f"Loaded configuration from {self.config_file}")
                
                # Validate the configuration after loading
                if not self._validate_config(self._config):
                    logger.warning("Loaded configuration contains invalid values, using defaults")
                    self._config = WebDisplayConfig()
                    self._create_backup_and_reset()
                    
            else:
                self._config = WebDisplayConfig()
                logger.info("Configuration file not found, using default configuration")
                
        except json.JSONDecodeError as e:
            logger.error(f"Configuration file is corrupted (JSON decode error): {e}")
            self._config = WebDisplayConfig()
            self._create_backup_and_reset()
            
        except (IOError, OSError) as e:
            logger.error(f"Failed to read configuration file: {e}")
            self._config = WebDisplayConfig()
            
        except Exception as e:
            logger.error(f"Unexpected error loading configuration: {e}")
            self._config = WebDisplayConfig()
            self._create_backup_and_reset()

        return self._config

    def save_config(self, config: WebDisplayConfig) -> bool:
        """Save configuration to file.
        
        Args:
            config: Configuration to save
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            self._ensure_data_directory()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2)
            self._config = config
            logger.info(f"Saved configuration to {self.config_file}")
            return True
        except IOError as e:
            logger.error(f"Failed to save configuration: {e}")
            return False

    def update_config(self, **kwargs) -> WebDisplayConfig:
        """Update configuration with new values.
        
        Args:
            **kwargs: Configuration fields to update
            
        Returns:
            WebDisplayConfig: Updated configuration
        """
        current_config = self.load_config()
        config_dict = current_config.to_dict()
        config_dict.update(kwargs)
        
        new_config = WebDisplayConfig.from_dict(config_dict)
        self.save_config(new_config)
        return new_config

    def get_config(self) -> WebDisplayConfig:
        """Get current configuration.
        
        Returns:
            WebDisplayConfig: Current configuration
        """
        return self.load_config()

    def reset_to_defaults(self) -> WebDisplayConfig:
        """Reset configuration to defaults.
        
        Returns:
            WebDisplayConfig: Default configuration
        """
        default_config = WebDisplayConfig()
        self.save_config(default_config)
        return default_config

    def _validate_config(self, config: WebDisplayConfig) -> bool:
        """Validate configuration values.
        
        Args:
            config: Configuration to validate
            
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        try:
            # Check font size is reasonable
            if not (8 <= config.font_size <= 200):
                logger.warning(f"Invalid font size: {config.font_size}")
                return False
            
            # Check artwork size is reasonable
            if not (50 <= config.artwork_size <= 1000):
                logger.warning(f"Invalid artwork size: {config.artwork_size}")
                return False
            
            # Check colors are valid
            if not (WebDisplayConfig._is_valid_color(config.background_color) and
                    WebDisplayConfig._is_valid_color(config.text_color) and
                    WebDisplayConfig._is_valid_color(config.accent_color)):
                logger.warning("Invalid color values in configuration")
                return False
            
            # Check font weight is valid
            if config.font_weight not in ['normal', 'bold', 'lighter', 'bolder']:
                logger.warning(f"Invalid font weight: {config.font_weight}")
                return False
            
            # Check layout is valid
            if config.layout not in ['horizontal', 'vertical', 'overlay']:
                logger.warning(f"Invalid layout: {config.layout}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return False

    def _create_backup_and_reset(self) -> None:
        """Create backup of corrupted config file and reset to defaults."""
        try:
            if os.path.exists(self.config_file):
                # Create backup with timestamp
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{self.config_file}.backup_{timestamp}"
                
                # Copy corrupted file to backup
                import shutil
                shutil.copy2(self.config_file, backup_path)
                logger.info(f"Created backup of corrupted config: {backup_path}")
                
                # Remove corrupted file
                os.remove(self.config_file)
                logger.info(f"Removed corrupted config file: {self.config_file}")
                
        except Exception as e:
            logger.error(f"Failed to create backup of corrupted config: {e}")

    def get_config_status(self) -> Dict[str, Any]:
        """Get configuration file status and health information.
        
        Returns:
            Dict containing configuration status information
        """
        try:
            status = {
                'config_file_exists': os.path.exists(self.config_file),
                'config_file_path': self.config_file,
                'is_valid': True,
                'error_message': None,
                'backup_files': []
            }
            
            if status['config_file_exists']:
                try:
                    # Try to load and validate
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, dict):
                        config = WebDisplayConfig.from_dict(data)
                        status['is_valid'] = self._validate_config(config)
                    else:
                        status['is_valid'] = False
                        status['error_message'] = "Invalid data format"
                        
                except json.JSONDecodeError as e:
                    status['is_valid'] = False
                    status['error_message'] = f"JSON decode error: {str(e)}"
                except Exception as e:
                    status['is_valid'] = False
                    status['error_message'] = f"Unexpected error: {str(e)}"
            
            # Find backup files
            config_dir = os.path.dirname(self.config_file)
            if os.path.exists(config_dir):
                config_name = os.path.basename(self.config_file)
                backup_pattern = f"{config_name}.backup_"
                
                for file in os.listdir(config_dir):
                    if file.startswith(backup_pattern):
                        backup_path = os.path.join(config_dir, file)
                        status['backup_files'].append(backup_path)
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting config status: {e}")
            return {
                'config_file_exists': False,
                'config_file_path': self.config_file,
                'is_valid': False,
                'error_message': f"Status check failed: {str(e)}",
                'backup_files': []
            }