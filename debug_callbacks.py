#!/usr/bin/env python3
"""
Debug script to check if player callbacks are working properly.
Run this while music is playing to see if callbacks are triggered.
"""

import sys
import time
import threading
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.playlist_manager import PlaylistManager
from core.player_engine import PlayerEngine

def debug_callbacks():
    """Debug callback functionality."""
    print("🔍 Debugging player callbacks...")
    
    # Initialize components
    playlist_manager = PlaylistManager("data/playlist.json", "data/artwork")
    player_engine = PlayerEngine()
    player_engine.set_playlist(playlist_manager.get_playlist())
    
    # Track callbacks
    callback_count = {'song': 0, 'state': 0}
    
    def on_song_changed(song):
        callback_count['song'] += 1
        print(f"🎵 CALLBACK #{callback_count['song']}: Song changed to {song.get_display_name() if song else 'None'}")
    
    def on_state_changed(state):
        callback_count['state'] += 1
        print(f"🔄 CALLBACK #{callback_count['state']}: State changed to {state.value}")
    
    # Set up callbacks
    player_engine.set_on_song_changed(on_song_changed)
    player_engine.set_on_state_changed(on_state_changed)
    player_engine.set_auto_advance(True)
    
    # Start update loop (CRITICAL for pygame events)
    update_running = True
    def update_loop():
        print("🔄 Starting pygame event processing loop...")
        while update_running:
            try:
                player_engine.update()  # Process pygame events
                time.sleep(0.05)  # 20 FPS
            except Exception as e:
                print(f"❌ Update error: {e}")
                time.sleep(1)
        print("🔄 Update loop stopped")
    
    update_thread = threading.Thread(target=update_loop, daemon=True)
    update_thread.start()
    
    try:
        if playlist_manager.is_empty():
            print("❌ No songs in playlist")
            return
        
        songs = playlist_manager.get_songs()
        print(f"📋 Found {len(songs)} songs in playlist")
        
        # Start playing
        first_song = playlist_manager.set_current_song(0)
        if first_song and player_engine.play_song(first_song):
            print(f"▶️  Started: {first_song.get_display_name()}")
        else:
            print("❌ Failed to start playback")
            return
        
        print("\n🎧 Music should be playing now...")
        print("🔍 Watching for callbacks (song changes, state changes)...")
        print("⏭️  Try manually changing songs in your GUI to test callbacks")
        print("🔄 Or wait for songs to finish naturally")
        print("📊 Press Ctrl+C to stop\n")
        
        last_check = time.time()
        while True:
            time.sleep(1)
            
            # Status every 5 seconds
            if time.time() - last_check >= 5:
                current = player_engine.get_current_song()
                state = player_engine.get_state()
                pos = player_engine.get_position()
                dur = player_engine.get_duration()
                
                print(f"📊 Status: {current.get_display_name() if current else 'None'} | "
                      f"{state.value} | {pos:.1f}s/{dur:.1f}s | "
                      f"Callbacks: {callback_count['song']} song, {callback_count['state']} state")
                
                last_check = time.time()
    
    except KeyboardInterrupt:
        print("\n⏹️  Stopping...")
    finally:
        update_running = False
        player_engine.stop()
        player_engine.shutdown()
        print("🧹 Done")

if __name__ == "__main__":
    debug_callbacks()