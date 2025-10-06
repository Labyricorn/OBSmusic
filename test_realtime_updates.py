#!/usr/bin/env python3
"""
Test script to verify real-time web updates during actual music playback.
This will test if song changes are properly detected and broadcast to the web interface.
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_realtime_updates():
    """Test real-time web updates during actual playback."""
    print("Testing real-time web updates during playback...")
    
    # Initialize components
    playlist_manager = PlaylistManager("data/playlist.json", "data/artwork")
    player_engine = PlayerEngine()
    web_server = WebServer(host='127.0.0.1', port=8083)
    
    # Connect player engine with playlist
    player_engine.set_playlist(playlist_manager.get_playlist())
    
    # Track callback activity
    callback_stats = {
        'song_changes': 0,
        'state_changes': 0,
        'last_update': time.time()
    }
    
    def on_song_changed(song):
        """Handle song change events and update web display."""
        callback_stats['song_changes'] += 1
        callback_stats['last_update'] = time.time()
        
        print(f"🎵 Song changed #{callback_stats['song_changes']}: {song.get_display_name() if song else 'None'}")
        
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
            print(f"✅ Web display updated: {song.get_display_name()}")
    
    def on_state_changed(state):
        """Handle playback state changes and update web display."""
        callback_stats['state_changes'] += 1
        callback_stats['last_update'] = time.time()
        
        print(f"🔄 State changed #{callback_stats['state_changes']}: {state.value}")
        
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
            print(f"✅ Web display state updated: {state.value}")
    
    # Set up callbacks
    player_engine.set_on_song_changed(on_song_changed)
    player_engine.set_on_state_changed(on_state_changed)
    
    # Enable auto-advance for testing
    player_engine.set_auto_advance(True)
    
    # Start web server
    if not web_server.start():
        print("❌ Failed to start web server")
        return False
    
    print(f"🌐 Web server started at: {web_server.get_server_url()}")
    
    # CRITICAL: Start player update thread for pygame event processing
    update_running = True
    def player_update_loop():
        print("🔄 Player update thread started")
        while update_running:
            try:
                player_engine.update()  # This processes pygame events including song end
                time.sleep(0.05)  # Update every 50ms for responsive event processing
            except Exception as e:
                print(f"❌ Error in player update: {e}")
                time.sleep(1)
        print("🔄 Player update thread stopped")
    
    update_thread = threading.Thread(target=player_update_loop, daemon=True)
    update_thread.start()
    
    try:
        # Check if we have songs
        if playlist_manager.is_empty():
            print("❌ Playlist is empty - cannot test")
            return False
        
        songs = playlist_manager.get_songs()
        print(f"📋 Playlist has {len(songs)} songs:")
        for i, song in enumerate(songs):
            print(f"  {i+1}. {song.get_display_name()}")
        
        print(f"\n🌐 Open {web_server.get_server_url()} in your browser to see real-time updates")
        print("🎵 Starting playback test...")
        
        # Start playing the first song
        first_song = playlist_manager.set_current_song(0)
        if first_song and player_engine.play_song(first_song):
            print(f"▶️  Started playing: {first_song.get_display_name()}")
        else:
            print("❌ Failed to start playback")
            return False
        
        print("\n📊 Monitoring for automatic song changes...")
        print("   - Songs should advance automatically when they finish")
        print("   - Web page should update in real-time")
        print("   - Press Ctrl+C to stop")
        
        # Monitor for activity
        last_stats_time = time.time()
        
        while True:
            time.sleep(1)
            
            # Print periodic status
            current_time = time.time()
            if current_time - last_stats_time >= 10:  # Every 10 seconds
                current_song = player_engine.get_current_song()
                state = player_engine.get_state()
                position = player_engine.get_position()
                duration = player_engine.get_duration()
                
                print(f"\n📊 Status Update:")
                print(f"   Current: {current_song.get_display_name() if current_song else 'None'}")
                print(f"   State: {state.value}")
                print(f"   Position: {position:.1f}s / {duration:.1f}s")
                print(f"   Song changes: {callback_stats['song_changes']}")
                print(f"   State changes: {callback_stats['state_changes']}")
                print(f"   Last callback: {current_time - callback_stats['last_update']:.1f}s ago")
                
                last_stats_time = current_time
            
            # Check if playback stopped unexpectedly
            if not player_engine.is_playing() and not player_engine.is_paused():
                current_song = player_engine.get_current_song()
                if current_song:
                    print(f"⚠️  Playback stopped. Current song: {current_song.get_display_name()}")
                    # Try to continue if there are more songs
                    if playlist_manager.get_playlist().current_index < len(songs) - 1:
                        print("🔄 Attempting to continue to next song...")
                        time.sleep(1)  # Give it a moment
                    else:
                        print("📋 Reached end of playlist")
                        break
                else:
                    print("⏹️  Playback finished")
                    break
        
        print(f"\n📊 Final Statistics:")
        print(f"   Song changes detected: {callback_stats['song_changes']}")
        print(f"   State changes detected: {callback_stats['state_changes']}")
        
        if callback_stats['song_changes'] > 0:
            print("✅ Song change callbacks are working!")
            print("✅ Web updates should be happening in real-time")
        else:
            print("❌ No song changes detected - callbacks may not be working")
            print("❌ This could explain why the web page doesn't update")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    finally:
        update_running = False
        player_engine.stop()
        web_server.stop()
        player_engine.shutdown()
        print("🧹 Cleanup completed")
    
    return True


if __name__ == "__main__":
    test_realtime_updates()