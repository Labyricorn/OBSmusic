# Music Player Configuration Settings

This document provides a comprehensive overview of all configuration settings available in the `data/config.json` file for the Music Player web display.

## Configuration File Location

The configuration file is located at: `data/config.json`

## Available Configuration Settings

### Font Settings

#### `font_family`
- **Type**: String
- **Default**: `"Arial"`
- **Description**: Sets the font family for all text elements
- **Example Values**: `"Arial"`, `"Helvetica"`, `"Times New Roman"`, `"Courier New"`

#### `font_size`
- **Type**: Number (pixels)
- **Default**: `18`
- **Description**: Sets the base font size for the song title
- **Example Values**: `12`, `16`, `18`, `24`, `32`

#### `artist_font_size`
- **Type**: Number (pixels)
- **Default**: `14`
- **Description**: Sets the font size specifically for the artist text (independent of the main font size)
- **Example Values**: `10`, `12`, `14`, `16`, `20`

#### `font_weight`
- **Type**: String
- **Default**: `"normal"`
- **Description**: Sets the font weight for text elements
- **Available Values**: `"normal"`, `"bold"`, `"lighter"`, `"bolder"`
- **Note**: Currently supported in server defaults but may need implementation in display template

### Color Settings

#### `background_color`
- **Type**: String (hex color)
- **Default**: `"#000000"`
- **Description**: Sets the background color of the display
- **Example Values**: `"#000000"` (black), `"#ffffff"` (white), `"#1a1a1a"` (dark gray)

#### `text_color`
- **Type**: String (hex color)
- **Default**: `"#ffffff"`
- **Description**: Sets the color for song title and artist text
- **Example Values**: `"#ffffff"` (white), `"#000000"` (black), `"#ff6b6b"` (red)

#### `accent_color`
- **Type**: String (hex color)
- **Default**: `"#ff6b6b"`
- **Description**: Sets the accent color for status indicators and other UI elements
- **Example Values**: `"#ff6b6b"` (red), `"#4ecdc4"` (teal), `"#45b7d1"` (blue)
- **Note**: Currently supported in server defaults but may need implementation in display template

### Layout Settings

#### `layout`
- **Type**: String
- **Default**: `"vertical"`
- **Description**: Controls the overall layout arrangement of elements
- **Available Values**:
  - `"vertical"`: Elements stacked vertically and centered (default)
  - `"horizontal"`: Album artwork on the left, text on the right in a row
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
- **Default**: `200`
- **Description**: Sets the maximum width and height of the album artwork (maintains aspect ratio)
- **Example Values**: `50`, `100`, `150`, `200`, `300`

### Status Display Settings

#### `show_status`
- **Type**: Boolean
- **Default**: `false`
- **Description**: Controls whether the playback status indicator is displayed
- **Available Values**: `true`, `false`

## Example Configuration Files

### Minimal Configuration
```json
{
  "font_family": "Arial",
  "font_size": 18,
  "background_color": "#000000",
  "text_color": "#ffffff",
  "layout": "vertical",
  "show_artwork": true
}
```

### Complete Configuration with All Options
```json
{
  "font_family": "Helvetica",
  "font_size": 24,
  "artist_font_size": 18,
  "font_weight": "normal",
  "background_color": "#1a1a1a",
  "text_color": "#ffffff",
  "accent_color": "#4ecdc4",
  "show_status": true,
  "artwork_size": 150,
  "layout": "horizontal",
  "show_artwork": true
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

## Notes

- All color values should be in hexadecimal format (e.g., `#ffffff`)
- Font sizes are specified in pixels
- Boolean values should be `true` or `false` (lowercase, no quotes)
- The configuration file must be valid JSON format
- If a setting is omitted, the default value will be used
- Some settings from the server defaults (like `font_weight` and `accent_color`) may require additional implementation in the display template

## Troubleshooting

- If the configuration doesn't load, check the browser console for errors
- Ensure the JSON syntax is valid (use a JSON validator if needed)
- Verify that color codes are properly formatted with the `#` prefix
- Check that boolean values are lowercase (`true`/`false`)
- Ensure numeric values are not enclosed in quotes