#!/usr/bin/env python3
"""
Performance Tests for Music Player Application

Tests performance characteristics with large playlists and high-load scenarios.
"""

import unittest
import time
import tempfile
import os
import json
import threading
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.song import Song
from models.playlist import Playlist
from core.playlist_manager import PlaylistManager
from core.player_engine import PlayerEngine
from core.config_manager import ConfigManager


class TestPerformance(unittest.TestCase):
    """Performance tests for large playlist handling and system load."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_mp3_path = os.path.join(self.temp_dir, "test_song.mp3")
        
        # Create a minimal MP3 file for testing
        with open(self.test_mp3_path, 'wb') as f:
            # Write minimal MP3 header
            f.write(b'\xff\xfb\x90\x00' + b'\x00' * 1000)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_large_playlist_creation_performance(self):
        """Test performance of creating large playlists (1000+ songs)."""
        print("\n🔄 Testing large playlist creation performance...")
        
        start_time = time.time()
        
        # Create 1000 mock songs
        songs = []
        for i in range(1000):
            song = Song(
                file_path=f"/fake/path/song_{i}.mp3",
                title=f"Test Song {i}",
                artist=f"Test Artist {i % 100}",  # 100 different artists
                album=f"Test Album {i % 50}",     # 50 different albums
                artwork_path=None,
                duration=180.0 + (i % 120)  # Varying durations
            )
            songs.append(song)
        
        playlist = Playlist(songs=songs, current_index=0, loop_enabled=False)
        
        creation_time = time.time() - start_time
        
        # Performance assertions
        self.assertLess(creation_time, 1.0, "Large playlist creation should take less than 1 second")
        self.assertEqual(len(playlist.songs), 1000, "All songs should be added to playlist")
        
        print(f"✅ Created 1000-song playlist in {creation_time:.3f} seconds")
    
    def test_playlist_serialization_performance(self):
        """Test performance of serializing/deserializing large playlists."""
        print("\n🔄 Testing playlist serialization performance...")
        
        # Create large playlist
        songs = []
        for i in range(500):
            song = Song(
                file_path=f"/fake/path/song_{i}.mp3",
                title=f"Test Song {i}",
                artist=f"Test Artist {i % 50}",
                album=f"Test Album {i % 25}",
                artwork_path=f"/fake/artwork_{i % 10}.jpg" if i % 3 == 0 else None,
                duration=180.0 + (i % 120)
            )
            songs.append(song)
        
        playlist = Playlist(songs=songs, current_index=42, loop_enabled=True)
        
        # Test serialization performance
        start_time = time.time()
        playlist_dict = playlist.to_dict()
        serialization_time = time.time() - start_time
        
        # Test deserialization performance
        start_time = time.time()
        restored_playlist = Playlist.from_dict(playlist_dict)
        deserialization_time = time.time() - start_time
        
        # Performance assertions
        self.assertLess(serialization_time, 0.5, "Serialization should take less than 0.5 seconds")
        self.assertLess(deserialization_time, 0.5, "Deserialization should take less than 0.5 seconds")
        
        # Correctness assertions
        self.assertEqual(len(restored_playlist.songs), 500)
        self.assertEqual(restored_playlist.current_index, 42)
        self.assertEqual(restored_playlist.loop_enabled, True)
        
        print(f"✅ Serialized 500-song playlist in {serialization_time:.3f} seconds")
        print(f"✅ Deserialized 500-song playlist in {deserialization_time:.3f} seconds")
    
    def test_playlist_manager_large_operations(self):
        """Test PlaylistManager performance with large playlists."""
        print("\n🔄 Testing PlaylistManager large operations performance...")
        
        playlist_file = os.path.join(self.temp_dir, "large_playlist.json")
        manager = PlaylistManager(playlist_file)
        
        # Add many songs quickly
        start_time = time.time()
        for i in range(200):
            with patch('mutagen.File') as mock_mutagen:
                mock_file = Mock()
                mock_file.info.length = 180.0 + (i % 60)
                mock_file.get.return_value = [f"Test Value {i}"]
                mock_mutagen.return_value = mock_file
                
                manager.add_song(f"/fake/path/song_{i}.mp3")
        
        add_time = time.time() - start_time
        
        # Test playlist navigation performance
        start_time = time.time()
        for _ in range(100):
            manager.next_song()
        navigation_time = time.time() - start_time
        
        # Test reordering performance
        start_time = time.time()
        for i in range(50):
            old_index = i
            new_index = (i + 50) % 200
            manager.reorder_songs(old_index, new_index)
        reorder_time = time.time() - start_time
        
        # Performance assertions
        self.assertLess(add_time, 2.0, "Adding 200 songs should take less than 2 seconds")
        self.assertLess(navigation_time, 0.1, "100 navigation operations should take less than 0.1 seconds")
        self.assertLess(reorder_time, 0.5, "50 reorder operations should take less than 0.5 seconds")
        
        print(f"✅ Added 200 songs in {add_time:.3f} seconds")
        print(f"✅ Performed 100 navigation operations in {navigation_time:.3f} seconds")
        print(f"✅ Performed 50 reorder operations in {reorder_time:.3f} seconds")
    
    def test_concurrent_playlist_access(self):
        """Test thread safety and performance under concurrent access."""
        print("\n🔄 Testing concurrent playlist access performance...")
        
        playlist_file = os.path.join(self.temp_dir, "concurrent_playlist.json")
        manager = PlaylistManager(playlist_file)
        
        # Add initial songs
        for i in range(50):
            with patch('mutagen.File') as mock_mutagen:
                mock_file = Mock()
                mock_file.info.length = 180.0
                mock_file.get.return_value = [f"Test Song {i}"]
                mock_mutagen.return_value = mock_file
                
                manager.add_song(f"/fake/path/song_{i}.mp3")
        
        results = []
        errors = []
        
        def navigation_worker():
            """Worker function for navigation operations."""
            try:
                for _ in range(20):
                    manager.next_song()
                    time.sleep(0.001)  # Small delay to increase contention
                results.append("navigation_complete")
            except Exception as e:
                errors.append(f"Navigation error: {e}")
        
        def reorder_worker():
            """Worker function for reorder operations."""
            try:
                for i in range(10):
                    old_index = i % 50
                    new_index = (i + 25) % 50
                    manager.reorder_songs(old_index, new_index)
                    time.sleep(0.002)  # Small delay to increase contention
                results.append("reorder_complete")
            except Exception as e:
                errors.append(f"Reorder error: {e}")
        
        def info_worker():
            """Worker function for info retrieval operations."""
            try:
                for _ in range(30):
                    current = manager.get_current_song()
                    playlist_info = manager.get_playlist_info()
                    time.sleep(0.001)
                results.append("info_complete")
            except Exception as e:
                errors.append(f"Info error: {e}")
        
        # Start concurrent operations
        start_time = time.time()
        threads = []
        
        # Create multiple threads of each type
        for _ in range(3):
            threads.append(threading.Thread(target=navigation_worker))
            threads.append(threading.Thread(target=reorder_worker))
            threads.append(threading.Thread(target=info_worker))
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        concurrent_time = time.time() - start_time
        
        # Performance and correctness assertions
        self.assertLess(concurrent_time, 5.0, "Concurrent operations should complete within 5 seconds")
        self.assertEqual(len(errors), 0, f"No errors should occur during concurrent access: {errors}")
        self.assertEqual(len(results), 9, "All worker threads should complete successfully")
        
        print(f"✅ Completed concurrent operations in {concurrent_time:.3f} seconds")
        print(f"✅ No thread safety issues detected")
    
    def test_memory_usage_large_playlist(self):
        """Test memory usage with large playlists."""
        print("\n🔄 Testing memory usage with large playlists...")
        
        import psutil
        import gc
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create large playlist
        songs = []
        for i in range(2000):
            song = Song(
                file_path=f"/fake/path/very_long_filename_to_test_memory_usage_song_{i}.mp3",
                title=f"Very Long Song Title To Test Memory Usage Song Number {i}",
                artist=f"Very Long Artist Name To Test Memory Usage Artist {i % 100}",
                album=f"Very Long Album Name To Test Memory Usage Album {i % 50}",
                artwork_path=f"/fake/very/long/path/to/artwork/image_{i % 10}.jpg" if i % 3 == 0 else None,
                duration=180.0 + (i % 300)
            )
            songs.append(song)
        
        playlist = Playlist(songs=songs, current_index=0, loop_enabled=False)
        
        # Get memory usage after creating large playlist
        gc.collect()  # Force garbage collection
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        memory_increase = peak_memory - initial_memory
        memory_per_song = memory_increase / 2000  # MB per song
        
        # Clean up
        del playlist
        del songs
        gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_freed = peak_memory - final_memory
        
        # Memory usage assertions
        self.assertLess(memory_per_song, 0.01, "Memory usage per song should be less than 0.01 MB")
        self.assertLess(memory_increase, 50, "Total memory increase should be less than 50 MB for 2000 songs")
        self.assertGreater(memory_freed, memory_increase * 0.8, "At least 80% of memory should be freed after cleanup")
        
        print(f"✅ Memory increase for 2000 songs: {memory_increase:.2f} MB")
        print(f"✅ Memory per song: {memory_per_song:.4f} MB")
        print(f"✅ Memory freed after cleanup: {memory_freed:.2f} MB")
    
    def test_config_manager_performance(self):
        """Test ConfigManager performance with frequent updates."""
        print("\n🔄 Testing ConfigManager performance...")
        
        config_file = os.path.join(self.temp_dir, "perf_config.json")
        manager = ConfigManager(config_file)
        
        # Test rapid configuration updates
        start_time = time.time()
        for i in range(100):
            config = manager.get_config()
            config.font_size = 20 + (i % 20)
            config.background_color = f"#{i:06x}"
            config.text_color = f"#{(i * 2) % 0xFFFFFF:06x}"
            manager.save_config(config)
        
        update_time = time.time() - start_time
        
        # Test rapid configuration loading
        start_time = time.time()
        for _ in range(100):
            config = manager.get_config()
        
        load_time = time.time() - start_time
        
        # Performance assertions
        self.assertLess(update_time, 1.0, "100 config updates should take less than 1 second")
        self.assertLess(load_time, 0.1, "100 config loads should take less than 0.1 seconds")
        
        print(f"✅ Performed 100 config updates in {update_time:.3f} seconds")
        print(f"✅ Performed 100 config loads in {load_time:.3f} seconds")
    
    def test_web_server_load_simulation(self):
        """Test web server performance under simulated load."""
        print("\n🔄 Testing web server load simulation...")
        
        from web.server import create_app
        import requests
        import threading
        from unittest.mock import patch
        
        # Create test app
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            # Simulate concurrent requests
            results = []
            errors = []
            
            def make_requests():
                """Make multiple requests to test endpoints."""
                try:
                    for _ in range(10):
                        # Test main display page
                        response = client.get('/')
                        if response.status_code != 200:
                            errors.append(f"Display page error: {response.status_code}")
                        
                        # Test config page
                        response = client.get('/config')
                        if response.status_code != 200:
                            errors.append(f"Config page error: {response.status_code}")
                        
                        time.sleep(0.01)  # Small delay
                    
                    results.append("requests_complete")
                except Exception as e:
                    errors.append(f"Request error: {e}")
            
            # Start multiple request threads
            start_time = time.time()
            threads = []
            for _ in range(5):  # 5 concurrent clients
                thread = threading.Thread(target=make_requests)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads
            for thread in threads:
                thread.join()
            
            load_test_time = time.time() - start_time
            
            # Performance assertions
            self.assertLess(load_test_time, 3.0, "Load test should complete within 3 seconds")
            self.assertEqual(len(errors), 0, f"No errors should occur during load test: {errors}")
            self.assertEqual(len(results), 5, "All request threads should complete")
            
            print(f"✅ Completed load test with 5 concurrent clients in {load_test_time:.3f} seconds")
            print(f"✅ Processed {5 * 10 * 2} total requests successfully")


if __name__ == '__main__':
    unittest.main(verbosity=2)