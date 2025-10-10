# Design Document

## Overview

The GUI modernization will transform the existing Tkinter-based music player interface from a dated 800x600 window to a compact, modern 400x300 interface. The design focuses on contemporary visual aesthetics, improved space utilization, and enhanced user experience while maintaining full backward compatibility with existing functionality.

The modernization will implement a clean, flat design with modern color schemes, improved typography, and better visual hierarchy. The music note indicator will be redesigned to properly track the currently playing song, and web interface access will be converted from buttons to elegant hyperlinked text with dynamic port detection.

**Update**: This design now includes dynamic hyperlink URL generation based on runtime port configuration and integration of the OBSmusic.ico file for consistent branding across GUI and web interfaces.

## Architecture

### Design System Foundation

**Color Palette:**
- Primary Background: `#2b2b2b` (Dark charcoal)
- Secondary Background: `#3c3c3c` (Medium gray)
- Accent Color: `#4a9eff` (Modern blue)
- Text Primary: `#ffffff` (White)
- Text Secondary: `#b0b0b0` (Light gray)
- Success/Playing: `#00d084` (Green)
- Warning: `#ff6b35` (Orange)

**Typography:**
- Primary Font: `Segoe UI` (Windows), `SF Pro Display` (macOS), `Ubuntu` (Linux)
- Font Sizes: Title (14px), Body (11px), Small (9px)
- Font Weights: Regular (400), Medium (500), Bold (600)

**Spacing System:**
- Base unit: 8px
- Small: 4px, Medium: 8px, Large: 16px, XLarge: 24px

### Layout Architecture

**Compact Grid System (400x300px):**
```
┌─────────────────────────────────────────┐
│ Now Playing (60px height)              │
├─────────────────────────────────────────┤
│                                         │
│ Playlist Area (180px height)           │
│                                         │
├─────────────────────────────────────────┤
│ Controls (30px height)                  │
├─────────────────────────────────────────┤
│ File Mgmt + Web Links (30px height)    │
└─────────────────────────────────────────┘
```

**Responsive Behavior:**
- Minimum window size: 350x250px
- All components scale proportionally
- Playlist area gets priority for extra space
- Controls maintain fixed heights for usability

### Web Interface Integration Architecture

**Icon Serving Strategy:**
- Favicon route: `/favicon.ico` on both web and controls servers
- Icon processing: Convert OBSmusic.ico to appropriate web formats
- Caching: Browser-friendly cache headers for icon resources
- Fallback: Default favicon if OBSmusic.ico unavailable

**Dynamic Port Communication:**
- Port discovery: Query server objects for current listening ports
- Update triggers: Server start/stop events, port changes
- Refresh mechanism: Periodic URL validation and update
- Error resilience: Graceful handling of server communication failures

**Server Integration Points:**
```python
# Web server integration
web_server.get_current_port() -> int
web_server.is_running() -> bool
web_server.add_favicon_route(icon_path: str)

# Controls server integration  
controls_server.get_current_port() -> int
controls_server.is_running() -> bool
controls_server.add_favicon_route(icon_path: str)
```

## Components and Interfaces

### 0. Application Window Component

**Design Specifications:**
- Window title: "OBSmusic" (updated from "Music Player")
- Window icon: OBSmusic.ico file from project root
- Icon fallback: Default system icon if file missing/corrupted
- Icon size: 32x32 pixels for window display

**Implementation Interface:**
```python
class ModernMainWindow:
    def __init__(self, root, branding_config: BrandingConfig)
    def set_window_icon(self, icon_path: str)
    def set_window_title(self, title: str)
    def handle_icon_loading_errors(self)
```

### 1. Now Playing Display Component

**Design Specifications:**
- Height: 60px fixed
- Background: Primary background with subtle gradient
- Border: 1px solid secondary background
- Corner radius: 8px
- Padding: 12px

**Content Layout:**
- Song title: Primary text, medium weight, 12px
- Artist/Album: Secondary text, regular weight, 10px
- Truncation: Ellipsis for overflow text
- Animation: Subtle fade transition on song changes

**Implementation Interface:**
```python
class ModernNowPlayingDisplay:
    def __init__(self, parent, **style_options)
    def update_song_info(self, song: Song)
    def set_no_song_state(self)
    def apply_modern_styling(self)
```

### 2. Modern Playlist Component

**Design Specifications:**
- Compact row height: 24px (reduced from ~30px)
- Alternating row colors for better readability
- Modern selection highlighting with rounded corners
- Music note indicator: `♪` symbol with accent color
- Font: 10px regular weight

**Music Note Indicator Logic:**
- Position: 2px left margin from song number
- Color: Success/Playing color (`#00d084`)
- Animation: Subtle pulse effect when playing
- Behavior: Follows `playlist.current_index` exactly

**Row Format:**
```
[♪] 01. Song Title - Artist
    02. Another Song - Artist
    03. Third Song - Artist
```

**Implementation Interface:**
```python
class ModernPlaylistDisplay:
    def __init__(self, parent, **style_options)
    def update_playlist_display(self, songs: List[Song], current_index: int)
    def update_music_note_position(self, current_index: int)
    def handle_selection_change(self, callback: Callable)
    def handle_drag_drop_reorder(self, callback: Callable)
```

### 3. Compact Control Panel

**Design Specifications:**
- Height: 30px fixed
- Button size: 24x24px
- Button spacing: 4px
- Modern flat buttons with hover effects
- Icon-based design with Unicode symbols

**Button Layout (Left to Right):**
- Previous: `⏮` (12px from left)
- Play: `▶` / Pause: `⏸` (dynamic)
- Stop: `⏹`
- Next: `⏭`
- Loop checkbox: Compact toggle switch design (right-aligned)

**Implementation Interface:**
```python
class ModernControlPanel:
    def __init__(self, parent, **style_options)
    def update_button_states(self, state: PlaybackState)
    def set_button_callbacks(self, callbacks: Dict[str, Callable])
    def apply_modern_button_styling(self)
```

### 4. Dynamic Web Interface Links Component

**Design Specifications:**
- Real-time URL generation based on server port configuration
- Display format: Full URLs (e.g., "http://localhost:8080", "http://localhost:8081")
- Port detection: Query running web and controls servers for current ports
- Update mechanism: Refresh URLs when server ports change
- Error handling: Show placeholder URLs when servers not running

**URL Generation Logic:**
- Web Display URL: `http://localhost:{web_server.port}`
- Web Controls URL: `http://localhost:{controls_server.port}`
- Fallback URLs: Use configured default ports if servers not accessible

**Implementation Interface:**
```python
class DynamicWebLinks:
    def __init__(self, parent, hyperlink_config: HyperlinkConfig)
    def update_from_servers(self, web_server, controls_server)
    def get_current_urls(self) -> Dict[str, str]
    def refresh_hyperlink_display(self)
    def handle_server_unavailable(self)
```

### 5. File Management & Web Links Panel

**Design Specifications:**
- Height: 30px fixed
- Split layout: File buttons (left) | Web links (right)
- Compact button design: 80x24px
- Hyperlink styling for web access

**File Management Buttons:**
- Add Songs, Remove, Clear, Save
- Modern flat design with subtle borders
- Hover effects with color transitions

**Web Interface Links:**
- Display: Dynamic URL based on web server port (e.g., `http://localhost:8080`)
- Controls: Dynamic URL based on controls server port (e.g., `http://localhost:8081`)
- Styling: Underlined hyperlinks with accent color
- Behavior: Left-click opens, right-click shows context menu
- URL Generation: Real-time port detection from running servers

**Implementation Interface:**
```python
class ModernFileManagementPanel:
    def __init__(self, parent, **style_options)
    def create_file_buttons(self, callbacks: Dict[str, Callable])
    def create_web_hyperlinks(self, web_server, controls_server)
    def update_hyperlink_urls(self, web_server, controls_server)
    def handle_hyperlink_interactions(self)
```

## Data Models

### Style Configuration Model

```python
@dataclass
class ModernTheme:
    """Modern theme configuration for GUI components."""
    
    # Colors
    bg_primary: str = "#2b2b2b"
    bg_secondary: str = "#3c3c3c"
    accent: str = "#4a9eff"
    text_primary: str = "#ffffff"
    text_secondary: str = "#b0b0b0"
    success: str = "#00d084"
    warning: str = "#ff6b35"
    
    # Typography
    font_family: str = "Segoe UI"
    font_size_title: int = 14
    font_size_body: int = 11
    font_size_small: int = 9
    
    # Spacing
    spacing_small: int = 4
    spacing_medium: int = 8
    spacing_large: int = 16
    
    # Component dimensions
    window_width: int = 400
    window_height: int = 300
    now_playing_height: int = 60
    controls_height: int = 30
    file_panel_height: int = 30
```

### Music Note Indicator State

```python
@dataclass
class MusicNoteState:
    """State management for music note indicator."""
    
    current_position: Optional[int] = None
    is_playing: bool = False
    animation_active: bool = False
    
    def update_position(self, new_index: Optional[int]) -> bool:
        """Update position and return True if changed."""
        if self.current_position != new_index:
            self.current_position = new_index
            return True
        return False
```

### Dynamic Hyperlink Configuration

```python
@dataclass
class HyperlinkConfig:
    """Configuration for dynamic hyperlink URL generation."""
    
    web_server_port: int = 8080
    controls_server_port: int = 8081
    host: str = "localhost"
    
    def get_display_url(self) -> str:
        """Generate display URL based on current web server port."""
        return f"http://{self.host}:{self.web_server_port}"
    
    def get_controls_url(self) -> str:
        """Generate controls URL based on current controls server port."""
        return f"http://{self.host}:{self.controls_server_port}"
    
    def update_ports(self, web_port: int, controls_port: int) -> bool:
        """Update ports and return True if changed."""
        changed = (self.web_server_port != web_port or 
                  self.controls_server_port != controls_port)
        self.web_server_port = web_port
        self.controls_server_port = controls_port
        return changed
```

### Application Branding Configuration

```python
@dataclass
class BrandingConfig:
    """Configuration for application branding and icons."""
    
    app_title: str = "OBSmusic"
    icon_path: str = "OBSmusic.ico"
    window_icon_size: tuple = (32, 32)
    favicon_size: tuple = (16, 16)
    
    def get_icon_path(self) -> Path:
        """Get absolute path to icon file."""
        return Path(__file__).parent / self.icon_path
    
    def icon_exists(self) -> bool:
        """Check if icon file exists."""
        return self.get_icon_path().exists()
```

## Error Handling

### Theme Application Errors

**Fallback Strategy:**
- If modern theme fails to load, fall back to system default
- Log theme application errors for debugging
- Graceful degradation to basic styling

**Error Types:**
- Font loading failures
- Color parsing errors
- Style application exceptions

### Layout Constraint Violations

**Minimum Size Enforcement:**
- Prevent window resize below 350x250px
- Maintain component proportions at minimum size
- Hide non-essential elements if space is insufficient

**Component Overflow Handling:**
- Text truncation with ellipsis
- Scrollable playlist when content exceeds available space
- Responsive button sizing

### Hyperlink Interaction Errors

**Browser Launch Failures:**
- Show error dialog with manual URL instructions
- Log browser launch attempts for debugging
- Provide clipboard copy as fallback

**Context Menu Errors:**
- Fallback to simple URL display dialog
- Manual copy instructions if clipboard access fails

### Icon Loading and Integration Errors

**Icon File Errors:**
- Missing icon file: Log warning and use default system icon
- Corrupted icon file: Log error and fall back to default icon
- Invalid icon format: Attempt format conversion or use default

**Web Interface Icon Integration:**
- Favicon serving errors: Log and serve default favicon
- Icon size conversion failures: Use original size or default
- Web server icon route errors: Graceful degradation to no favicon

### Dynamic Port Detection Errors

**Server Communication Failures:**
- Server not running: Display default port URLs with visual indicator
- Port query timeout: Use last known ports or defaults
- Invalid port responses: Fall back to configured default ports

**URL Generation Errors:**
- Invalid port numbers: Use default ports and log error
- Network interface issues: Fall back to localhost
- URL formatting errors: Use simple fallback URL format

## Testing Strategy

### Visual Regression Testing

**Screenshot Comparisons:**
- Capture before/after screenshots of each component
- Automated visual diff detection
- Manual review of design consistency

**Cross-Platform Testing:**
- Windows, macOS, Linux appearance verification
- Font rendering consistency checks
- Color accuracy across different displays

### Functional Testing

**Music Note Indicator Testing:**
```python
def test_music_note_follows_current_song():
    """Test that music note indicator tracks current song correctly."""
    # Test cases:
    # - Note appears when song starts playing
    # - Note moves when song changes
    # - Note disappears when playback stops
    # - Note follows song during playlist reordering
```

**Hyperlink Interaction Testing:**
```python
def test_web_interface_hyperlinks():
    """Test hyperlink behavior for web interfaces."""
    # Test cases:
    # - Left-click opens browser
    # - Right-click shows context menu
    # - Copy URL functionality works
    # - Error handling for browser failures
```

**Dynamic Port Detection Testing:**
```python
def test_dynamic_hyperlink_urls():
    """Test dynamic URL generation based on server ports."""
    # Test cases:
    # - URLs update when servers start with different ports
    # - Fallback to default URLs when servers not running
    # - URL refresh when server ports change at runtime
    # - Error handling for server communication failures
```

**Icon Integration Testing:**
```python
def test_application_branding():
    """Test icon and branding integration."""
    # Test cases:
    # - GUI window displays OBSmusic.ico as window icon
    # - Window title shows "OBSmusic" instead of "Music Player"
    # - Web interfaces serve OBSmusic.ico as favicon
    # - Graceful fallback when icon file missing or corrupted
```

### Performance Testing

**Rendering Performance:**
- Measure GUI update times with large playlists
- Test smooth animations and transitions
- Memory usage monitoring during extended use

**Responsiveness Testing:**
- Window resize performance
- Component update latency
- User interaction response times

### Integration Testing

**Backward Compatibility:**
- All existing functionality preserved
- Same callback interfaces maintained
- Configuration persistence works correctly

**Player Engine Integration:**
- Music note indicator responds to playback state changes
- GUI updates reflect player engine state accurately
- Error handling integration works properly