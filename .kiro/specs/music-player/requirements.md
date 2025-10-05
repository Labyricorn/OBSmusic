# Requirements Document

## Introduction

This feature involves creating a Python-based music player application that can play MP3 files with playlist management capabilities. The application will serve a web interface that displays current song information (title, artist, artwork) in a format suitable for use as an OBS streaming source. The web interface will be highly configurable to allow customization of the visual presentation.

## Requirements

### Requirement 1

**User Story:** As a streamer, I want to play MP3 files from a playlist, so that I can have continuous music during my streams without manual intervention.

#### Acceptance Criteria

1. WHEN the application starts THEN the system SHALL load and display the current playlist
2. WHEN a user selects a song from the playlist THEN the system SHALL begin playing that MP3 file
3. WHEN a song finishes playing THEN the system SHALL automatically advance to the next song in the playlist
4. WHEN the playlist reaches the end AND loop is disabled THEN the system SHALL stop playback
5. WHEN the playlist reaches the end AND loop is enabled THEN the system SHALL restart from the first song

### Requirement 2

**User Story:** As a user, I want to easily edit my playlist, so that I can add, remove, or reorder songs without technical complexity.

#### Acceptance Criteria

1. WHEN a user adds an MP3 file THEN the system SHALL include it in the playlist with proper metadata extraction
2. WHEN a user removes a song from the playlist THEN the system SHALL update the playlist and continue playback if currently playing
3. WHEN a user reorders songs in the playlist THEN the system SHALL maintain the new order for subsequent playback
4. WHEN playlist changes are made THEN the system SHALL persist the changes for future sessions
5. IF a playlist file becomes corrupted or missing THEN the system SHALL create a new empty playlist

### Requirement 3

**User Story:** As a streamer, I want a loop option for my playlist, so that music continues playing indefinitely during long streaming sessions.

#### Acceptance Criteria

1. WHEN the loop checkbox is checked THEN the system SHALL enable playlist looping
2. WHEN the loop checkbox is unchecked THEN the system SHALL disable playlist looping
3. WHEN loop is enabled AND the last song finishes THEN the system SHALL restart playback from the first song
4. WHEN loop setting changes THEN the system SHALL persist the setting for future sessions

### Requirement 4

**User Story:** As a streamer, I want a web page that displays current song information, so that I can use it as an OBS browser source for my stream overlay.

#### Acceptance Criteria

1. WHEN the web server starts THEN the system SHALL serve a web page accessible via HTTP
2. WHEN a song is playing THEN the web page SHALL display the current song title
3. WHEN a song is playing THEN the web page SHALL display the current artist name
4. WHEN a song is playing AND artwork is available THEN the web page SHALL display the album artwork
5. WHEN no song is playing THEN the web page SHALL display appropriate placeholder content
6. WHEN song changes THEN the web page SHALL update the displayed information in real-time

### Requirement 5

**User Story:** As a streamer, I want the web page appearance to be highly configurable, so that it matches my stream's visual branding and layout requirements.

#### Acceptance Criteria

1. WHEN configuration options are changed THEN the web page SHALL reflect the new styling immediately
2. WHEN the system starts THEN the web page SHALL load saved configuration settings
3. IF no configuration exists THEN the system SHALL use sensible default styling
4. WHEN font settings are modified THEN the web page SHALL update text appearance accordingly
5. WHEN color settings are modified THEN the web page SHALL update background and text colors accordingly
6. WHEN layout settings are modified THEN the web page SHALL update element positioning and sizing accordingly
7. WHEN artwork display settings are modified THEN the web page SHALL update image presentation accordingly

### Requirement 6

**User Story:** As a user, I want the application to handle MP3 files reliably, so that playback is smooth and metadata is accurately displayed.

#### Acceptance Criteria

1. WHEN an MP3 file is loaded THEN the system SHALL extract title, artist, and album artwork metadata
2. WHEN metadata is missing or corrupted THEN the system SHALL use filename as fallback for title
3. WHEN an MP3 file cannot be played THEN the system SHALL skip to the next song and log the error
4. WHEN playback encounters an error THEN the system SHALL attempt to continue with the next song
5. IF no valid MP3 files exist in the playlist THEN the system SHALL display an appropriate message

### Requirement 7

**User Story:** As a user, I want basic playback controls, so that I can manage music playback during use.

#### Acceptance Criteria

1. WHEN the play button is clicked THEN the system SHALL start or resume playback
2. WHEN the pause button is clicked THEN the system SHALL pause current playback
3. WHEN the stop button is clicked THEN the system SHALL stop playback and reset to beginning
4. WHEN the next button is clicked THEN the system SHALL advance to the next song in the playlist
5. WHEN the previous button is clicked THEN the system SHALL go to the previous song in the playlist
6. WHEN volume controls are adjusted THEN the system SHALL change playback volume accordingly