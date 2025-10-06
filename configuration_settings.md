# Music Player Configuration Settings

This document provides a comprehensive overview of all configuration settings available in the `data/config.json` file for the Music Player web display and controls interface.

## Configuration File Location

The configuration file is located at: `data/config.json`

## Complete Configuration Reference

### Background Settings

#### `background_color`
- **Type**: String (hex color)
- **Default**: `"#000000"`
- **Description**: Sets the background color of the main display interface
- **Example Values**: `"#000000"` (black), `"#ffffff"` (white), `"#1a1a1a"` (dark gray)

#### `player_background_color`
- **Type**: String (CSS background value)
- **Default**: `"linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)"`
- **Description**: Sets the background color/gradient specifically for the HTML controls interface
- **Example Values**: 
  - `"#ff0000"` (solid red)
  - `"linear-gradient(45deg, #ff6b6b, #4ecdc4)"` (gradient)
  - `"url('path/to/image.jpg')"` (background image)

### Text Styling Settings

#### `title` (Object)
Contains styling settings for the song title:

- **`font_family`** (String, default: `"Arial"`): Font family for the song title
- **`font_size`** (Number, default: `32`): Font size in pixels for the song title
- **`font_weight`** (String, default: `"bold"`): Font weight ("normal", "bold", "lighter", "bolder", or numeric 100-900)
- **`color`** (String, default: `"#ffffff"`): Text color for the song title (hex color)

#### `artist` (Object)
Contains styling settings for the artist name:

- **`font_family`** (String, default: `"Arial"`): Font family for the artist name
- **`font_size`** (Number, default: `24`): Font size in pixels for the artist name
- **`font_weight`** (String, default: `"normal"`): Font weight ("normal", "bold", "lighter", "bolder", or numeric 100-900)
- **`color`** (String, default: `"#cccccc"`): Text color for the artist name (hex color)

### Layout Settings

#### `layout`
- **Type**: String
- **Default**: `"horizontal"`
- **Description**: Controls the overall layout arrangement of elements
- **Available Values**:
  - `"vertical"`: Elements stacked vertically and centered
  - `"horizontal"`: Album artwork on the left, text on the right in a row (default)
  - `"left-justified"`: Elements stacked vertically but aligned to the left side
  - `"right-justified"`: Elements stacked vertically but aligned to the right side

### Artwork Settings

#### `show_artwork`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Controls whether album artwork is displayed
- **Available Values**: `true`, `false`

#### `artwork_size`
- **Type**: Number (pixels)
- **Default**: `80`
- **Description**: Sets the maximum width and height of the album artwork (maintains aspect ratio)
- **Example Values**: `50`, `80`, `100`, `150`, `200`, `300`

### Status Display Settings

#### `show_status`
- **Type**: Boolean
- **Default**: `false`
- **Description**: Controls whether the playback status indicator is displayed
- **Available Values**: `true`, `false`

### Progress Bar Settings

#### `progress_bar` (Object)
Contains all progress bar configuration options:

- **`show`** (Boolean, default: `true`): Whether to display the progress bar
- **`position`** (String, default: `"bottom"`): Position of the progress bar ("top", "bottom", or "inline")
- **`width`** (Number, default: `80`): Width as percentage of screen width (1-100)
- **`height`** (Number, default: `6`): Height of the progress bar in pixels
- **`spacing`** (Number, default: `20`): Distance from screen edges or margin around inline bar (pixels)
- **`background_color`** (String, default: `"#333333"`): Background color of the progress bar (hex color)
- **`fill_color`** (String, default: `"#ff6b6b"`): Color of the progress fill (hex color)
- **`border_radius`** (Number, default: `3`): Border radius in pixels for rounded corners

### Frame Settings

#### `frame` (Object)
Contains frame configuration options that encompass all display elements:

- **`show`** (Boolean, default: `true`): Whether to display the frame around all elements
- **`thickness`** (Number, default: `2`): Thickness of the frame border in pixels
- **`corner_radius`** (Number, default: `10`): Corner radius of the frame in pixels
- **`frame_color`** (String, default: `"#ffffff"`): Color of the frame border (hex color)
- **`fill_color`** (String, default: `"transparent"`): Background fill color behind all elements (hex color or "transparent")

## Example Configuration Files

### Current Default Configuration
```json
{
  "background_color": "#000000",
  "player_background_color": "linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)",
  "show_artwork": true,
  "artwork_size": 80,
  "layout": "horizontal",
  "show_status": false,
  "title": {
    "font_family": "Arial",
    "font_size": 32,
    "font_weight": "bold",
    "color": "#ffffff"
  },
  "artist": {
    "font_family": "Arial",
    "font_size": 24,
    "font_weight": "normal",
    "color": "#cccccc"
  },
  "progress_bar": {
    "show": true,
    "position": "bottom",
    "width": 80,
    "height": 6,
    "spacing": 20,
    "background_color": "#333333",
    "fill_color": "#ff6b6b",
    "border_radius": 3
  },
  "frame": {
    "show": true,
    "thickness": 2,
    "corner_radius": 10,
    "frame_color": "#ffffff",
    "fill_color": "transparent"
  }
}
```

### Minimal Configuration
```json
{
  "background_color": "#000000",
  "player_background_color": "#333333",
  "show_artwork": false,
  "layout": "vertical",
  "show_status": false,
  "title": {
    "font_family": "Arial",
    "font_size": 18,
    "color": "#ffffff"
  },
  "artist": {
    "font_family": "Arial", 
    "font_size": 14,
    "color": "#cccccc"
  },
  "progress_bar": {
    "show": false
  },
  "frame": {
    "show": false
  }
}
```

### Gaming/Streaming Style Configuration
```json
{
  "background_color": "#000000",
  "player_background_color": "linear-gradient(45deg, #ff0000, #000000)",
  "show_artwork": true,
  "artwork_size": 120,
  "layout": "horizontal",
  "show_status": true,
  "title": {
    "font_family": "Impact, sans-serif",
    "font_size": 28,
    "font_weight": "bold",
    "color": "#00ff00"
  },
  "artist": {
    "font_family": "Arial, sans-serif",
    "font_size": 18,
    "font_weight": "normal",
    "color": "#66ff66"
  },
  "progress_bar": {
    "show": true,
    "position": "bottom",
    "width": 100,
    "height": 8,
    "spacing": 0,
    "background_color": "#222222",
    "fill_color": "#00ff00",
    "border_radius": 0
  },
  "frame": {
    "show": true,
    "thickness": 3,
    "corner_radius": 0,
    "frame_color": "#00ff00",
    "fill_color": "#001100"
  }
}
```

### Left-Aligned Layout Example
```json
{
  "font_family": "Arial",
  "font_size": 20,
  "artist_font_size": 16,
  "background_color": "#000000",
  "text_color": "#ffffff",
  "show_status": false,
  "artwork_size": 120,
  "layout": "left-justified",
  "show_artwork": true
}
```

### Minimal Display (No Artwork, Right-Aligned)
```json
{
  "font_family": "Courier New",
  "font_size": 16,
  "artist_font_size": 12,
  "background_color": "#000000",
  "text_color": "#00ff00",
  "show_status": true,
  "layout": "right-justified",
  "show_artwork": false
}
```

## Layout Behavior Details

### Vertical Layout (`"layout": "vertical"`)
- Elements are stacked vertically
- All content is centered horizontally
- Default spacing and margins apply
- Best for: Standard OBS browser source overlays

### Horizontal Layout (`"layout": "horizontal"`)
- Album artwork appears on the left
- Song title and artist text appear on the right
- Elements are arranged side-by-side
- Best for: Wide display areas, lower thirds

### Left-Justified Layout (`"layout": "left-justified"`)
- Elements are stacked vertically
- All content is aligned to the left side
- 50px left padding is applied
- Artwork aligns to the left edge
- Best for: Left-side overlays, corner displays

### Right-Justified Layout (`"layout": "right-justified"`)
- Elements are stacked vertically
- All content is aligned to the right side
- 50px right padding is applied
- Artwork aligns to the right edge
- Best for: Right-side overlays, corner displays

## Configuration Updates

Configuration changes can be applied in two ways:

1. **File Update**: Modify the `data/config.json` file directly and refresh the browser
2. **API Update**: Use the `/api/config` POST endpoint to update configuration programmatically

Changes are automatically broadcast to all connected browser sources via WebSocket when updated through the API.

## Interface-Specific Settings

### Main Display Interface
- Uses `background_color` for the main display background
- All `title`, `artist`, `progress_bar`, and `frame` settings apply
- Artwork and layout settings control the main display appearance

### HTML Controls Interface  
- Uses `player_background_color` specifically for the controls interface background
- Independent styling from the main display
- Accessible via separate web server port (typically 8081)

## Notes

- All color values should be in hexadecimal format (e.g., `#ffffff`) or valid CSS values
- Font sizes are specified in pixels
- Boolean values should be `true` or `false` (lowercase, no quotes)
- The configuration file must be valid JSON format
- If a setting is omitted, the default value will be used
- The `player_background_color` supports CSS gradients and background images
- Nested objects (title, artist, progress_bar, frame) can be partially configured - missing properties will use defaults

## Troubleshooting

- If the configuration doesn't load, check the browser console for errors
- Ensure the JSON syntax is valid (use a JSON validator if needed)
- Verify that color codes are properly formatted with the `#` prefix
- Check that boolean values are lowercase (`true`/`false`)
- Ensure numeric values are not enclosed in quotes