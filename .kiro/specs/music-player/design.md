# Design Document

## Overview

The music player application will be built as a Python desktop application with an embedded web server. The architecture separates concerns between audio playback, playlist management, web serving, and configuration management. The application will use pygame for audio playback, mutagen for MP3 metadata extraction, Flask for the web server, and tkinter for the desktop GUI.

## Architecture

The application follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Desktop GUI   │    │   Web Server    │    │ Configuration   │
│   (tkinter)     │    │   (Flask)       │    │   Manager       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Music Player   │
                    │    Engine       │
                    └─────────────────┘
                             │
                    ┌─────────────────┐
                    │   Playlist      │
                    │   Manager       │
                    └─────────────────┘
```

## Components and Interfaces

### 1. Music Player Engine
**Responsibility:** Core audio playback functionality
**Technology:** pygame.mixer
**Key Methods:**
- `play(file_path)`: Start playing an MP3 file
- `pause()`: Pause current playback
- `stop()`: Stop playback
- `set_volume(level)`: Adjust playback volume
- `is_playing()`: Check playback status

### 2. Playlist Manager
**Responsibility:** Manage playlist operations and persistence
**Technology:** JSON file storage with mutagen for metadata
**Key Methods:**
- `add_song(file_path)`: Add MP3 to playlist with metadata extraction
- `remove_song(index)`: Remove song from playlist
- `reorder_songs(old_index, new_index)`: Reorder playlist
- `get_current_song()`: Get currently playing song info
- `next_song()`: Advance to next song
- `previous_song()`: Go to previous song
- `save_playlist()`: Persist playlist to disk
- `load_playlist()`: Load playlist from disk

### 3. Desktop GUI
**Responsibility:** User interface for playlist management and playback controls
**Technology:** tkinter
**Components:**
- Playlist display (Listbox with drag-and-drop reordering)
- Playback controls (Play, Pause, Stop, Next, Previous)
- Volume slider
- Loop checkbox
- Add/Remove song buttons
- Current song display

### 4. Web Server
**Responsibility:** Serve real-time song information for OBS integration
**Technology:** Flask with WebSocket for real-time updates
**Endpoints:**
- `GET /`: Main display page for OBS
- `GET /config`: Configuration interface
- `POST /config`: Update display configuration
- `WebSocket /updates`: Real-time song change notifications

### 5. Configuration Manager
**Responsibility:** Handle web display customization settings
**Technology:** JSON configuration files
**Settings Categories:**
- Font settings (family, size, weight)
- Color settings (background, text, accent colors)
- Layout settings (positioning, spacing, alignment)
- Display settings (show/hide elements, artwork size)

## Data Models

### Song Model
```python
@dataclass
class Song:
    file_path: str
    title: str
    artist: str
    album: str
    artwork_path: Optional[str]
    duration: float
```

### Playlist Model
```python
@dataclass
class Playlist:
    songs: List[Song]
    current_index: int
    loop_enabled: bool
    
    def to_dict(self) -> dict
    def from_dict(cls, data: dict) -> 'Playlist'
```

### Configuration Model
```python
@dataclass
class WebDisplayConfig:
    font_family: str = "Arial"
    font_size: int = 24
    font_weight: str = "normal"
    background_color: str = "#000000"
    text_color: str = "#ffffff"
    accent_color: str = "#ff6b6b"
    show_artwork: bool = True
    artwork_size: int = 200
    layout: str = "horizontal"  # horizontal, vertical, overlay
```

## Error Handling

### File System Errors
- Missing MP3 files: Skip and continue to next song
- Corrupted playlist file: Create new empty playlist
- Inaccessible artwork: Use default placeholder image

### Audio Playback Errors
- Unsupported format: Log error and skip to next song
- Audio device issues: Display error message and retry
- Corrupted MP3: Skip to next song with user notification

### Web Server Errors
- Port conflicts: Try alternative ports (8080, 8081, 8082)
- Configuration errors: Fall back to default settings
- WebSocket connection issues: Graceful degradation to polling

### Network Errors
- Web server startup failure: Continue with desktop-only mode
- Configuration save failure: Keep settings in memory only

## Testing Strategy

### Unit Tests
- **Playlist Manager:** Test add/remove/reorder operations, persistence
- **Music Player Engine:** Test playback state management, volume control
- **Configuration Manager:** Test settings validation and persistence
- **Song Model:** Test metadata extraction and validation

### Integration Tests
- **GUI + Playlist:** Test playlist operations through GUI
- **Web Server + Player:** Test real-time updates when songs change
- **Configuration + Web Display:** Test configuration changes reflect in web page

### End-to-End Tests
- **Complete Playback Flow:** Add songs, play playlist, verify web display updates
- **Loop Functionality:** Test playlist looping behavior
- **Configuration Persistence:** Test settings survive application restart

### Manual Testing Scenarios
- **OBS Integration:** Verify web page works as browser source
- **File Format Support:** Test various MP3 files with different metadata
- **Error Recovery:** Test behavior with missing files, corrupted data
- **Performance:** Test with large playlists (100+ songs)

## Implementation Notes

### Threading Considerations
- Audio playback runs in separate thread to prevent GUI blocking
- Web server runs in separate thread from main application
- WebSocket updates use thread-safe queues for communication

### File Organization
```
music_player/
├── main.py                 # Application entry point
├── models/
│   ├── song.py            # Song data model
│   └── playlist.py        # Playlist data model
├── core/
│   ├── player_engine.py   # Audio playback logic
│   ├── playlist_manager.py # Playlist operations
│   └── config_manager.py  # Configuration handling
├── gui/
│   └── main_window.py     # Desktop GUI
├── web/
│   ├── server.py          # Flask web server
│   ├── templates/
│   │   ├── display.html   # OBS display page
│   │   └── config.html    # Configuration interface
│   └── static/
│       ├── css/
│       └── js/
├── data/
│   ├── playlist.json      # Saved playlist
│   ├── config.json        # Web display configuration
│   └── artwork/           # Cached album artwork
└── requirements.txt       # Python dependencies
```

### Dependencies
- `pygame`: Audio playback
- `mutagen`: MP3 metadata extraction
- `flask`: Web server framework
- `flask-socketio`: Real-time web updates
- `tkinter`: Desktop GUI (included with Python)
- `Pillow`: Image processing for artwork
- `requests`: HTTP client for artwork downloads