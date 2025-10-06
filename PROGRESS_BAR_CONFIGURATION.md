# Music Player Display Configuration Guide

The music player now supports a **floating progress bar** and **configurable frame** that encompasses all display elements. Both features can be customized through the `data/config.json` file for a professional streaming appearance.

## Configuration Options

Add the following sections to your `data/config.json`:

```json
{
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

### Progress Bar Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `show` | boolean | `true` | Whether to display the progress bar |
| `position` | string | `"bottom"` | Where to place the progress bar: `"top"`, `"bottom"`, or `"inline"` |
| `width` | number | `80` | Width of the progress bar as percentage of screen width (1-100) |
| `height` | number | `6` | Height of the progress bar in pixels |
| `spacing` | number | `20` | Distance from screen edges (top/bottom) or margin around inline bar (pixels) |
| `background_color` | string | `"#333333"` | Background color of the progress bar (hex color) |
| `fill_color` | string | `"#ff6b6b"` | Color of the progress fill (hex color) |
| `border_radius` | number | `3` | Border radius in pixels for rounded corners |

### Title Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `font_family` | string | `"Arial"` | Font family for the song title |
| `font_size` | number | `32` | Font size for the song title in pixels |
| `font_weight` | string | `"bold"` | Font weight: "normal", "bold", "lighter", "bolder", or numeric (100-900) |
| `color` | string | `"#ffffff"` | Text color for the song title (hex color) |

### Artist Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `font_family` | string | `"Arial"` | Font family for the artist name |
| `font_size` | number | `24` | Font size for the artist name in pixels |
| `font_weight` | string | `"normal"` | Font weight: "normal", "bold", "lighter", "bolder", or numeric (100-900) |
| `color` | string | `"#cccccc"` | Text color for the artist name (hex color) |

### Frame Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `show` | boolean | `true` | Whether to display the frame around all elements |
| `thickness` | number | `2` | Thickness of the frame border in pixels |
| `corner_radius` | number | `10` | Corner radius of the frame in pixels |
| `frame_color` | string | `"#ffffff"` | Color of the frame border (hex color) |
| `fill_color` | string | `"transparent"` | Background fill color behind all elements (hex color or "transparent") |

### Position Options

- **`"top"`**: Progress bar appears at the very top of the screen
- **`"bottom"`**: Progress bar appears at the very bottom of the screen  
- **`"inline"`**: Progress bar appears inline with the song information

### Example Configurations

#### Minimal Progress Bar (Hidden)
```json
{
  "progress_bar": {
    "show": false
  }
}
```

#### Top Green Progress Bar (Full Width, No Spacing)
```json
{
  "progress_bar": {
    "show": true,
    "position": "top",
    "width": 100,
    "height": 6,
    "spacing": 0,
    "background_color": "#222222",
    "fill_color": "#4CAF50",
    "border_radius": 0
  }
}
```

#### Narrow Floating Blue Progress Bar (Large Spacing)
```json
{
  "progress_bar": {
    "show": true,
    "position": "bottom",
    "width": 50,
    "height": 8,
    "spacing": 40,
    "background_color": "#444444",
    "fill_color": "#2196F3",
    "border_radius": 4
  }
}
```

#### Wide Inline Progress Bar (Custom Spacing)
```json
{
  "progress_bar": {
    "show": true,
    "position": "inline",
    "width": 90,
    "height": 10,
    "spacing": 15,
    "background_color": "#1a1a1a",
    "fill_color": "#ff9800",
    "border_radius": 5
  }
}
```

#### Thin Floating Progress Bar (Minimal Spacing)
```json
{
  "progress_bar": {
    "show": true,
    "position": "bottom",
    "width": 60,
    "height": 2,
    "spacing": 5,
    "background_color": "#555555",
    "fill_color": "#ffffff",
    "border_radius": 1
  }
}
```

#### Frame Examples

#### Classic White Frame
```json
{
  "frame": {
    "show": true,
    "thickness": 2,
    "corner_radius": 10,
    "frame_color": "#ffffff",
    "fill_color": "transparent"
  }
}
```

#### Thick Gold Frame with Dark Fill
```json
{
  "frame": {
    "show": true,
    "thickness": 5,
    "corner_radius": 15,
    "frame_color": "#FFD700",
    "fill_color": "#1a1a1a"
  }
}
```

#### Minimal Rounded Frame
```json
{
  "frame": {
    "show": true,
    "thickness": 1,
    "corner_radius": 20,
    "frame_color": "#888888",
    "fill_color": "transparent"
  }
}
```

#### Sharp Gaming Frame with Accent Fill
```json
{
  "frame": {
    "show": true,
    "thickness": 3,
    "corner_radius": 0,
    "frame_color": "#00ff00",
    "fill_color": "#001100"
  }
}
```

#### Text Styling Examples

#### Bold Title with Subtle Artist
```json
{
  "title": {
    "font_family": "Arial",
    "font_size": 36,
    "font_weight": "bold",
    "color": "#ffffff"
  },
  "artist": {
    "font_family": "Arial",
    "font_size": 18,
    "font_weight": "normal",
    "color": "#888888"
  }
}
```

#### Elegant Serif Styling
```json
{
  "title": {
    "font_family": "Georgia, serif",
    "font_size": 28,
    "font_weight": "normal",
    "color": "#f0f0f0"
  },
  "artist": {
    "font_family": "Georgia, serif",
    "font_size": 20,
    "font_weight": "italic",
    "color": "#cccccc"
  }
}
```

#### Gaming/Streaming Style
```json
{
  "title": {
    "font_family": "Impact, sans-serif",
    "font_size": 32,
    "font_weight": "bold",
    "color": "#00ff00"
  },
  "artist": {
    "font_family": "Arial, sans-serif",
    "font_size": 16,
    "font_weight": "normal",
    "color": "#66ff66"
  }
}
```

#### Minimalist Modern
```json
{
  "title": {
    "font_family": "Helvetica, sans-serif",
    "font_size": 24,
    "font_weight": "300",
    "color": "#ffffff"
  },
  "artist": {
    "font_family": "Helvetica, sans-serif",
    "font_size": 16,
    "font_weight": "200",
    "color": "#aaaaaa"
  }
}
```

## How It Works

1. The progress bar automatically updates in real-time as songs play
2. Progress is calculated based on the current playback time vs. total song duration
3. The progress bar only appears when a song is actively playing
4. Configuration changes are applied immediately via WebSocket updates

## Testing

Run the test script to see different progress bar configurations:

```bash
python test_progress_bar.py
```

This will start the web server and cycle through different progress bar configurations so you can see how each setting affects the appearance and positioning.

## Integration with OBS

The progress bar works seamlessly with OBS Browser Sources:

1. Add a Browser Source in OBS
2. Set the URL to your web server (e.g., `http://localhost:8080`)
3. Configure the progress bar settings in `data/config.json`
4. The progress bar will update in real-time during stream/recording

## Troubleshooting

- **Progress bar not showing**: Check that `show` is set to `true` in the configuration
- **Progress not updating**: Ensure audio is playing through the web player component
- **Styling not applied**: Verify the configuration JSON is valid and the web server has restarted
- **Position not working**: Make sure `position` is one of: `"top"`, `"bottom"`, or `"inline"`