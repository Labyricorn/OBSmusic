# OBS Integration Manual Testing Scenarios

## Overview

This document provides detailed manual testing procedures specifically for OBS Studio integration with the Music Player Application. These tests ensure the web display works correctly as a browser source in OBS.

## Prerequisites

### Software Requirements
- OBS Studio (version 27.0 or later recommended)
- Music Player Application running
- Web browser (Chrome/Firefox recommended)
- Sample MP3 files with various metadata

### Setup Checklist
- [ ] Music Player Application installed and running
- [ ] Web server accessible at http://localhost:8080
- [ ] OBS Studio installed and configured
- [ ] Test MP3 files available with different metadata scenarios
- [ ] Network connectivity verified

## Test Scenarios

### Scenario 1: Basic OBS Browser Source Setup

#### Objective
Verify the web display can be added as a browser source in OBS and displays correctly.

#### Steps
1. **Start Music Player Application**
   ```
   - Launch the music player application
   - Verify web server starts successfully
   - Note the web server URL (default: http://localhost:8080)
   ```

2. **Add Browser Source in OBS**
   ```
   - Open OBS Studio
   - Create new scene or use existing scene
   - Add new source → Browser
   - Name: "Music Player Display"
   - URL: http://localhost:8080
   - Width: 800, Height: 600 (adjust as needed)
   - Check "Shutdown source when not visible" (optional)
   - Check "Refresh browser when scene becomes active" (optional)
   ```

3. **Verify Initial Display**
   ```
   - Browser source should load without errors
   - Default/placeholder content should be visible
   - No JavaScript errors in OBS log
   ```

#### Expected Results
- ✅ Browser source loads successfully
- ✅ No error messages in OBS log
- ✅ Placeholder content displays correctly
- ✅ Source fits within specified dimensions

#### Troubleshooting
- **Source shows blank**: Check URL accessibility in regular browser
- **Connection refused**: Verify music player web server is running
- **Layout issues**: Adjust browser source dimensions

---

### Scenario 2: Real-Time Song Information Display

#### Objective
Verify song information updates in real-time when music plays.

#### Steps
1. **Prepare Playlist**
   ```
   - Add 5-10 MP3 files with different metadata:
     * Song with complete metadata (title, artist, album, artwork)
     * Song with partial metadata (title only)
     * Song with no metadata (filename fallback)
     * Song with special characters in metadata
     * Song with very long title/artist names
   ```

2. **Start Playback**
   ```
   - Start playing first song in playlist
   - Observe OBS browser source display
   - Note update timing and accuracy
   ```

3. **Test Song Changes**
   ```
   - Use Next/Previous buttons to change songs
   - Observe real-time updates in OBS
   - Verify information accuracy for each song
   - Test rapid song changes (skip quickly through playlist)
   ```

4. **Test Playback States**
   ```
   - Test Play → Pause → Play transitions
   - Test Stop → Play transitions
   - Verify display updates appropriately for each state
   ```

#### Expected Results
- ✅ Song information appears within 1 second of song change
- ✅ Title and artist display correctly
- ✅ Artwork loads and displays (when available)
- ✅ Fallback behavior works for missing metadata
- ✅ Special characters display correctly
- ✅ Long text handles gracefully (truncation/wrapping)
- ✅ Playback state changes reflect in display

#### Test Data Validation
Record results for each test song:
```
Song 1 (Complete metadata):
- Title displayed: ✅/❌
- Artist displayed: ✅/❌
- Artwork displayed: ✅/❌
- Update timing: ___ seconds

Song 2 (Partial metadata):
- Fallback behavior: ✅/❌
- Missing fields handled: ✅/❌

[Continue for all test songs]
```

---

### Scenario 3: Display Configuration Testing

#### Objective
Verify configuration changes apply immediately and work correctly in OBS.

#### Steps
1. **Access Configuration Interface**
   ```
   - Open http://localhost:8080/config in web browser
   - Verify configuration form loads correctly
   - Note current settings
   ```

2. **Test Font Configuration**
   ```
   - Change font family (Arial → Times New Roman → Helvetica)
   - Modify font size (24 → 36 → 18)
   - Adjust font weight (normal → bold → light)
   - Observe changes in OBS browser source
   ```

3. **Test Color Configuration**
   ```
   - Change background color (black → blue → transparent)
   - Modify text color (white → yellow → red)
   - Adjust accent color for highlights
   - Verify color changes appear in OBS
   ```

4. **Test Layout Configuration**
   ```
   - Switch between layout modes:
     * Horizontal (side-by-side)
     * Vertical (stacked)
     * Overlay (text over artwork)
   - Adjust element positioning
   - Test artwork size settings
   ```

5. **Test Display Options**
   ```
   - Toggle artwork display on/off
   - Show/hide different information fields
   - Test animation/transition settings (if available)
   ```

#### Expected Results
- ✅ Configuration changes apply immediately (< 2 seconds)
- ✅ No page refresh required in OBS
- ✅ Font changes render correctly
- ✅ Colors display accurately
- ✅ Layout changes work properly
- ✅ Artwork toggle functions correctly
- ✅ Settings persist after application restart

#### Configuration Test Matrix
```
Font Family: Arial ✅ | Times ✅ | Helvetica ✅
Font Size: 18px ✅ | 24px ✅ | 36px ✅
Background: Black ✅ | Blue ✅ | Transparent ✅
Text Color: White ✅ | Yellow ✅ | Red ✅
Layout: Horizontal ✅ | Vertical ✅ | Overlay ✅
```

---

### Scenario 4: Long-Duration Streaming Test

#### Objective
Verify stability and performance during extended streaming sessions.

#### Steps
1. **Setup Extended Playlist**
   ```
   - Create playlist with 30+ songs
   - Enable loop mode
   - Mix of different file sizes and metadata
   ```

2. **Start Long-Duration Test**
   ```
   - Begin playback with OBS recording/streaming
   - Monitor for 2+ hours continuously
   - Document any issues or anomalies
   ```

3. **Monitor Performance Metrics**
   ```
   - CPU usage of music player application
   - Memory usage over time
   - Network activity
   - OBS performance impact
   ```

4. **Test Interruption Recovery**
   ```
   - Temporarily disconnect network
   - Pause/resume OBS recording
   - Minimize/restore OBS window
   - Change scenes in OBS
   ```

#### Expected Results
- ✅ No memory leaks over extended period
- ✅ Consistent display updates throughout test
- ✅ No crashes or freezes
- ✅ Graceful recovery from interruptions
- ✅ Stable CPU/memory usage
- ✅ No degradation in OBS performance

#### Performance Monitoring Log
```
Time | CPU % | Memory MB | Issues Noted
0:00 | 5%    | 45MB      | None
1:00 | 5%    | 47MB      | None
2:00 | 6%    | 48MB      | None
[Continue monitoring...]
```

---

### Scenario 5: Multiple Browser Sources Test

#### Objective
Test multiple instances of the display in different OBS scenes or sources.

#### Steps
1. **Create Multiple Browser Sources**
   ```
   - Scene 1: Full display (http://localhost:8080)
   - Scene 2: Config view (http://localhost:8080/config)
   - Scene 3: Same display with different dimensions
   ```

2. **Test Scene Switching**
   ```
   - Switch between scenes rapidly
   - Verify each source loads correctly
   - Check for resource conflicts
   ```

3. **Test Concurrent Updates**
   ```
   - Have multiple sources visible simultaneously
   - Change songs and verify all update together
   - Monitor resource usage
   ```

#### Expected Results
- ✅ Multiple sources work without conflicts
- ✅ All instances update simultaneously
- ✅ No significant performance impact
- ✅ Scene switching works smoothly

---

### Scenario 6: Network and Error Conditions

#### Objective
Test behavior under various error conditions and network issues.

#### Steps
1. **Test Network Interruption**
   ```
   - Start playback with OBS display active
   - Temporarily disable network connection
   - Re-enable network connection
   - Verify recovery behavior
   ```

2. **Test Server Restart**
   ```
   - Stop music player application
   - Observe OBS browser source behavior
   - Restart application
   - Verify automatic reconnection
   ```

3. **Test Port Conflicts**
   ```
   - Start another application on port 8080
   - Start music player (should use alternative port)
   - Update OBS browser source URL
   - Verify functionality continues
   ```

#### Expected Results
- ✅ Graceful handling of network interruptions
- ✅ Automatic reconnection when possible
- ✅ Clear error states when server unavailable
- ✅ Recovery without manual intervention

---

## Test Results Documentation

### Test Execution Checklist
For each test scenario, document:
- [ ] Test completed successfully
- [ ] Issues encountered (if any)
- [ ] Performance observations
- [ ] Screenshots/recordings of issues
- [ ] Workarounds applied

### Issue Reporting Template
```
Issue: [Brief description]
Scenario: [Which test scenario]
Steps to Reproduce:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Expected Result: [What should happen]
Actual Result: [What actually happened]
Environment:
- OS: [Operating System]
- OBS Version: [Version number]
- Browser: [If applicable]
- Music Player Version: [Version]

Screenshots: [Attach if relevant]
Workaround: [If found]
```

### Success Criteria Summary
All scenarios should meet these criteria:
- ✅ Display loads correctly in OBS
- ✅ Real-time updates work reliably
- ✅ Configuration changes apply immediately
- ✅ Stable performance over extended periods
- ✅ Graceful error handling
- ✅ No negative impact on OBS performance

## Additional Testing Notes

### Browser Compatibility in OBS
OBS uses Chromium Embedded Framework (CEF). Test considerations:
- JavaScript ES6+ features should work
- WebSocket support is available
- CSS3 features are supported
- Local storage works for configuration

### Performance Optimization Tips
- Use efficient CSS animations
- Minimize DOM updates
- Optimize image loading
- Consider lazy loading for artwork

### Accessibility Considerations
- Ensure text contrast meets standards
- Test with different font sizes
- Verify keyboard navigation (if applicable)
- Consider screen reader compatibility

This manual testing guide ensures comprehensive validation of OBS integration functionality and provides clear procedures for identifying and documenting any issues.