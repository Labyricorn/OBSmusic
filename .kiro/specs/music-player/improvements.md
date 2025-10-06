# Improvements Document

## Introduction

This feature involves editing an existing Python-based MP3 music player application. The applications primary features are a music player gui and web interface showing song information in a format suitable for use in OBS Studio. The existing application is in need of repair and improvement.

## Requirements

### Requirement 1

**User Story:** The album artwork is not properly loading from the mp3 file into the html page.

#### Acceptance Criteria

1. WHEN play is pressed the application will show the art extracted from the MP3 file.
2. WHEN no art is present in the mp3 file a standar placeholder image will be used.

### Requirement 2

**User Story:** The playing status does not show properly in the html page. Additionally I would like to see the play progress as a visual progress bar that can be configured like the other components of the html page.

#### Acceptance Criteria

1. WHEN configured to show in config.json the status of the player (Play, Paused, Stopped) will show in the html web page.
2. WHEN configured to show in the config.json a progress bar based on the play time of the mp3 file will show and progress as the audio plays.

### Requirement 3

**User Story:** An error ("ERROR:core.player_engine:Error in player update: video system not initialized") repeats in the terminal window while the application runs.

#### Acceptance Criteria

1. WHEN the application is running only pertinent infomrmation will be echoed into the terminal.

