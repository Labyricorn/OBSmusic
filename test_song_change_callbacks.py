#!/usr/bin/env python3
"""
Test script to verify song change callbacks are working properly.
This will test if the player engine properly triggers callbacks during
song changes and natural progression.
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
from core.player_engine import PlayerEngine, PlaybackState
from web.server import WebServer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_song_change_callbacks():
    """Test that song change callbacks are properly triggered."""
    print("Testing song change callbacks...")
    
    # Initialize components
    playlist_manager = PlaylistManager("data/playlist.json", "data/artwork")
    player_engine = PlayerEngine()
    web_server = WebServer(host='127.0.0.1', port=8082)
    
    # Connect player engine with playlist
    player_engine.set_playlist(playlist_manager.get_playlist())
    
    # Track callback calls
    callback_calls = {
        'song_changed': 0,
        'state_changed': 0,
        'last_song': None,
        'last_state': None
    }
    
    def on_song_changed(song):
        """Track song change callbacks."""
        callback_calls['song_changed'] += 1
        callback_calls['last_song'] = song
        print(f"✓ Song changed callback #{callback_calls['song_changed']}: {song.get_display_name() if song else 'None'}")
        
        # Update web server
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
    
    def on_state_changed(state):
        """Track state change callbacks."""
        callback_calls['state_changed'] += 1
        callback_calls['last_state'] = state
        print(f"✓ State changed callback #{callback_calls['state_changed']}: {state.value}")
        
        # Update web server
        if web_server:
            current_song = player_engine.get_current_song()
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
    
    # Set up callbacks
    player_engine.set_on_song_changed(on_song_changed)
    player_engine.set_on_state_changed(on_state_changed)
    
    # Start web server
    if not web_server.start():
        print("Failed to start web server")
        return False
    
    print(f"Web server started at: {web_server.get_server_url()}")
    
    # Start player update thread (essential for pygame event processing)
    update_running = True
    def player_update_loop():
        while update_running:
            try:
                player_engine.update()
                time.sleep(0.1)
            except Exception as e:
                print(f"Error in player update: {e}")
                time.sleep(1)
    
    update_thread = threading.Thread(target=player_update_loop, daemon=True)
    update_thread.start()
    print("Player update thread started")
    
    try:
        # Check if we have songs in the playlist
        if playlist_manager.is_empty():
            print("❌ Playlist is empty - cannot test song changes")
            return False
        
        songs = playlist_manager.get_songs()
        print(f"Playlist has {len(songs)} songs:")
        for i, song in enumerate(songs):
            print(f"  {i+1}. {song.get_display_name()}")
        
        print("\n=== Testing Manual Song Changes ===")
        
        # Test 1: Play first song
        print("Test 1: Playing first song...")
        first_song = playlist_manager.set_current_song(0)
        if first_song and player_engine.play_song(first_song):
            print(f"✓ Started playing: {first_song.get_display_name()}")
            time.sleep(2)  # Let it play for a bit
        else:
            print("❌ Failed to start playing first song")
        
        # Test 2: Switch to next song manually
        print("\nTest 2: Switching to next song...")
        if player_engine.next_song():
            print("✓ Advanced to next song")
            time.sleep(2)
        else:
            print("❌ Failed to advance to next song")
        
        # Test 3: Switch to previous song
        print("\nTest 3: Switching to previous song...")
        if player_engine.previous_song():
            print("✓ Went to previous song")
            time.sleep(2)
        else:
            print("❌ Failed to go to previous song")
        
        # Test 4: Test state changes
        print("\nTest 4: Testing state changes...")
        if player_engine.is_playing():
            print("Pausing...")
            player_engine.pause()
            time.sleep(1)
            
            print("Resuming...")
            player_engine.play()
            time.sleep(1)
            
            print("Stopping...")
            player_engine.stop()
            time.sleep(1)
        
        print("\n=== Testing Natural Song Progression ===")
        print("Note: Natural progression requires songs to actually finish playing.")
        print("For a quick test, we'll simulate short playback periods.")
        
        # Enable auto-advance
        player_engine.set_auto_advance(True)
        print("Auto-advance enabled")
        
        # Play a song and let it run briefly
        if len(songs) > 1:
            print("Playing first song briefly...")
            first_song = playlist_manager.set_current_song(0)
            if first_song and player_engine.play_song(first_song):
                print(f"Playing: {first_song.get_display_name()}")
                print("Let it play for 5 seconds to test updates...")
                time.sleep(5)
        
        # Summary
        print(f"\n=== Test Results ===")
        print(f"Song changed callbacks: {callback_calls['song_changed']}")
        print(f"State changed callbacks: {callback_calls['state_changed']}")
        print(f"Last song: {callback_calls['last_song'].get_display_name() if callback_calls['last_song'] else 'None'}")
        print(f"Last state: {callback_calls['last_state'].value if callback_calls['last_state'] else 'None'}")
        
        if callback_calls['song_changed'] > 0 and callback_calls['state_changed'] > 0:
            print("✅ Callbacks are working! Web updates should be automatic.")
        else:
            print("❌ Callbacks not triggered properly. Web updates may not work.")
        
        print(f"\nWeb interface at: {web_server.get_server_url()}")
        print("Check the web page to see if it updated automatically during the test.")
        print("\nPress Ctrl+C to stop...")
        
        # Keep running for manual testing
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        update_running = False
        player_engine.stop()
        web_server.stop()
        player_engine.shutdown()
        print("Test cleanup completed")
    
    return True


if __name__ == "__main__":
    test_song_change_callbacks()