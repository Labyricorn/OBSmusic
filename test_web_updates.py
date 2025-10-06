#!/usr/bin/env python3
"""
Test script to verify web interface automatic updates.
This script will test if song changes and playback state changes
are properly propagated to the web interface.
"""

import sys
import time
import threading
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.playlist_manager import PlaylistManager
from core.player_engine import PlayerEngine
from web.server import WebServer
from models.song import Song

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_web_updates():
    """Test automatic web updates for song changes and playback state."""
    print("Testing web interface automatic updates...")
    
    # Initialize components
    playlist_manager = PlaylistManager("data/playlist.json", "data/artwork")
    player_engine = PlayerEngine()
    web_server = WebServer(host='127.0.0.1', port=8081)
    
    # Connect player engine with playlist
    player_engine.set_playlist(playlist_manager.get_playlist())
    
    # Set up web integration callbacks
    def on_song_changed(song):
        """Handle song change events and update web display."""
        print(f"Song changed callback triggered: {song.get_display_name() if song else 'None'}")
        if web_server and song:
            artwork_url = "/static/artwork/placeholder.jpg"
            if song.artwork_path:
                artwork_filename = Path(song.artwork_path).name
                artwork_url = f"/static/artwork/{artwork_filename}"
            
            web_server.update_song_data(
                title=song.title,
                artist=song.artist,
                artwork_url=artwork_url,
                is_playing=player_engine.is_playing()
            )
            print(f"Updated web display: {song.get_display_name()}")
    
    def on_state_changed(state):
        """Handle playback state changes and update web display."""
        print(f"State changed callback triggered: {state.value}")
        current_song = player_engine.get_current_song()
        if web_server:
            if current_song:
                web_server.update_song_data(
                    title=current_song.title,
                    artist=current_song.artist,
                    artwork_url=web_server.current_song_data.get('artwork_url', '/static/artwork/placeholder.jpg'),
                    is_playing=player_engine.is_playing()
                )
            else:
                web_server.update_song_data(
                    title="No song playing",
                    artist="Music Player",
                    artwork_url="/static/artwork/placeholder.jpg",
                    is_playing=False
                )
            print(f"Updated web display state: {state.value}")
    
    # Set up callbacks
    player_engine.set_on_song_changed(on_song_changed)
    player_engine.set_on_state_changed(on_state_changed)
    
    # Start web server
    if not web_server.start():
        print("Failed to start web server")
        return False
    
    print(f"Web server started at: {web_server.get_server_url()}")
    print("Open the web interface in your browser to see updates")
    
    # Add some test songs if playlist is empty
    if playlist_manager.is_empty():
        print("Playlist is empty, adding test song...")
        if Path("test_song_file.mp3").exists():
            playlist_manager.add_song("test_song_file.mp3")
        else:
            print("No test song file found, creating a dummy song for testing...")
            # Create a dummy song for testing callbacks
            dummy_song = Song(
                file_path="test_song.mp3",
                title="Test Song",
                artist="Test Artist",
                album="Test Album"
            )
            playlist_manager.get_playlist().songs.append(dummy_song)
            playlist_manager.get_playlist().current_index = 0
    
    try:
        # Test automatic updates
        print("\nTesting automatic updates...")
        
        # Test 1: Song change
        print("Test 1: Triggering song change...")
        current_song = playlist_manager.get_current_song()
        if current_song:
            # Manually trigger the song changed callback
            on_song_changed(current_song)
            time.sleep(2)
        
        # Test 2: State changes
        print("Test 2: Triggering state changes...")
        from core.player_engine import PlaybackState
        
        # Simulate playing state
        on_state_changed(PlaybackState.PLAYING)
        time.sleep(2)
        
        # Simulate paused state
        on_state_changed(PlaybackState.PAUSED)
        time.sleep(2)
        
        # Simulate stopped state
        on_state_changed(PlaybackState.STOPPED)
        time.sleep(2)
        
        # Test 3: Multiple song changes
        print("Test 3: Testing multiple song changes...")
        for i in range(3):
            test_song = Song(
                file_path=f"test_song_{i}.mp3",
                title=f"Test Song {i+1}",
                artist=f"Test Artist {i+1}",
                album=f"Test Album {i+1}"
            )
            on_song_changed(test_song)
            time.sleep(3)
        
        print("\nTest completed. Check your web browser to see if updates appeared automatically.")
        print("The web interface should have updated in real-time without manual refresh.")
        print("\nPress Ctrl+C to stop the test server...")
        
        # Keep server running for manual testing
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        web_server.stop()
        player_engine.shutdown()
        print("Test cleanup completed")
    
    return True


if __name__ == "__main__":
    test_web_updates()