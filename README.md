# OBSmusic - Music Player with OBS Integration

Made with Amazon's Kiro (https://kiro.dev/)

A Python-based music player application that can play MP3 files with playlist management capabilities and serves a web interface for OBS streaming integration.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Issues](https://img.shields.io/github/issues/Labyricorn/OBSmusic.svg)](https://github.com/Labyricorn/OBSmusic/issues)

## 🎵 Overview

OBSmusic is a comprehensive music player designed specifically for content creators who want to integrate music into their OBS Studio streams. It provides both a desktop GUI for playlist management and a web interface that can be used as a browser source in OBS.

## Features

### Core Functionality
- MP3 playbook with playlist management
- Desktop GUI for playlist and playback control
- Web interface for OBS browser source integration
- Real-time song information updates
- Loop functionality for continuous playback

### Modern GUI Features (New!)
- **Modern Flat Design**: Clean, contemporary interface with rounded corners and proper spacing
- **Responsive Layout**: Adaptive design that works across different window sizes
- **Dynamic Hyperlinks**: Automatically updating web interface URLs based on server configuration
- **Integrated Branding**: OBSmusic branding with icon support and graceful fallbacks
- **Enhanced User Experience**: Hover effects, visual feedback, and smooth interactions
- **Comprehensive Error Handling**: Robust error recovery and graceful degradation
- **Backward Compatibility**: All existing functionality preserved during modernization

## Project Structure

```
OBSmusic/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── activate_env.bat        # Convenience script to activate virtual environment
├── obsmusic/               # Virtual environment (created by python -m venv)
├── models/                 # Data models
│   ├── __init__.py
│   ├── playlist.py
│   └── song.py
├── core/                   # Core functionality
│   ├── __init__.py
│   ├── config_manager.py
│   ├── player_engine.py
│   └── playlist_manager.py
├── gui/                    # Desktop GUI (Modernized)
│   ├── __init__.py
│   ├── main_window.py      # Main GUI with modern design
│   ├── theme.py            # Modern theme system
│   ├── branding_config.py  # Branding and icon management
│   └── hyperlink_config.py # Dynamic URL generation
├── web/                    # Web server and templates
│   ├── __init__.py
│   ├── server.py
│   ├── controls_server.py
│   ├── templates/          # HTML templates
│   │   ├── display.html
│   │   ├── controls.html
│   │   └── config.html
│   └── static/             # CSS and JavaScript (placeholder files)
│       ├── css/
│       └── js/
├── tests/                  # Unit tests
│   ├── __init__.py
│   └── [various test files]
└── data/                   # Data storage
    ├── artwork/            # Cached album artwork
    ├── config.json         # Configuration file
    ├── playlist.json       # Playlist data
    └── .gitkeep
```

## Installation

1. Install Python 3.8 or higher
2. Create and activate the virtual environment:
   ```bash
   # Create virtual environment
   python -m venv obsmusic
   
   # Activate virtual environment
   # On Windows:
   obsmusic\Scripts\activate
   # On macOS/Linux:
   source obsmusic/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Make sure the virtual environment is activated, then run the application:
```bash
# Activate virtual environment first (if not already activated)
obsmusic\Scripts\activate  # Windows
# source obsmusic/bin/activate  # macOS/Linux

# Run the application
python main.py
```

### Command Line Options

- `--config-dir PATH`: Custom directory for configuration files
- `--debug`: Enable debug logging
- `--port PORT`: Web server port (default: 8080)

## Development Status

**Latest Update: GUI Modernization Complete! 🎉**

The OBSmusic application now features a completely modernized GUI with:
- Modern flat design with responsive layout
- Dynamic hyperlink system for web interfaces
- Integrated branding with icon support
- Comprehensive error handling and graceful fallbacks
- Full backward compatibility with existing functionality

All 113 tests pass, ensuring reliability and stability.

## Requirements

- Python 3.8+
- pygame (audio playback)
- mutagen (MP3 metadata extraction)
- flask (web server)
- flask-socketio (real-time updates)
- Pillow (image processing)
- requests (HTTP client)- 
psutil (performance monitoring)

### Additional Command Line Options

```bash
python main.py [OPTIONS]

Additional Options:
  --no-gui             Run in headless mode (web server only)
  --no-web             Run without web server (GUI only)
  --log-file PATH      Save logs to file
  --version            Show version information
  --help               Show help message
```

### Examples

```bash
# Start with default settings
python main.py

# Enable debug logging on custom port
python main.py --debug --port 9090

# Run in headless mode for server deployment
python main.py --no-gui

# Use custom config directory
python main.py --config-dir ./my_config
```

## OBS Integration

1. Start the music player application
2. In OBS Studio, add a **Browser Source**
3. Set URL to: `http://localhost:8080` (main display) or `http://localhost:8081` (controls interface)
4. Set dimensions (e.g., 800x600)
5. Customize appearance by editing `data/config.json` (see [Configuration Settings](configuration_settings.md))

The display will update in real-time as songs change!

### Available Interfaces

- **Main Display** (`http://localhost:8080`): Shows song information, artwork, progress bar, and frame
- **Controls Interface** (`http://localhost:8081`): Provides playback controls with customizable background

## Testing

Run the test suite to verify functionality:

```bash
# Basic tests
python run_tests.py

# Comprehensive test suite
python test_suite.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Configuration

The music player supports extensive customization through the `data/config.json` file. You can configure:

- Background colors for both main display and controls interface
- Text styling (fonts, sizes, colors, weights)
- Layout options (vertical, horizontal, justified)
- Artwork display and sizing
- Progress bar appearance and positioning
- Frame styling around all elements

For complete configuration details, see [Configuration Settings](configuration_settings.md).

## Support

If you encounter any issues or have questions:
- Check the [Issues](https://github.com/Labyricorn/OBSmusic/issues) page
- Review the [Configuration Settings](configuration_settings.md) for customization options
- Check the [Progress Bar Configuration](PROGRESS_BAR_CONFIGURATION.md) for advanced progress bar setup
- Review the [Testing Documentation](TESTING_DOCUMENTATION.md)
- Check the [OBS Integration Manual](OBS_INTEGRATION_MANUAL_TESTS.md)

## Acknowledgments

- Built with Python and modern web technologies
- Designed for content creators and streamers
- Comprehensive testing suite included
