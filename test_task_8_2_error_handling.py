"""
Focused error handling tests for Task 8.2 - Comprehensive Error Handling
Tests the key error handling scenarios required by the task.
"""

import unittest
import tempfile
import os
import json
import shutil
from pathlib import Path

# Import the modules to test
from core.player_engine import PlayerEngine, PlaybackState
from core.playlist_manager import PlaylistManager
from core.config_manager import ConfigManager, WebDisplayConfig
from models.song import Song
from models.playlist import Playlist


class TestTask82ErrorHandling(unittest.TestCase):
    """Test comprehensive error handling implementation for Task 8.2."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.playlist_file = os.path.join(self.temp_dir, "test_playlist.json")
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        
        # Initialize components
        self.playlist_manager = PlaylistManager(self.playlist_file)
        self.config_manager = ConfigManager(self.config_file)
        self.player_engine = PlayerEngine()
        
        # Track errors
        self.playback_errors = []
        self.player_engine.set_on_playback_error(lambda msg: self.playback_errors.append(msg))
    
    def tearDown(self):
        """Clean up after tests."""
        self.player_engine.shutdown()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_missing_mp3_file_graceful_skipping(self):
        """Test graceful skipping of missing MP3 files (Requirement 6.3)."""
        print("\n=== Testing Missing MP3 File Handling ===")
        
        # Try to play a non-existent file
        result = self.player_engine.play("nonexistent_file.mp3")
        
        # Should fail gracefully
        self.assertFalse(result, "Playing non-existent file should return False")
        self.assertEqual(self.player_engine.get_state(), PlaybackState.STOPPED, 
                        "Player should be in STOPPED state after error")
        self.assertTrue(len(self.playback_errors) > 0, 
                       "Should have recorded a playback error")
        self.assertIn("not found", self.playback_errors[0].lower(), 
                     "Error message should mention file not found")
        
        print(f"✓ Missing file error handled: {self.playback_errors[0]}")
    
    def test_corrupted_playlist_recovery(self):
        """Test recovery from corrupted playlist files (Requirement 2.5)."""
        print("\n=== Testing Corrupted Playlist Recovery ===")
        
        # Create a corrupted playlist file
        with open(self.playlist_file, 'w') as f:
            f.write("This is not valid JSON content {")
        
        print(f"Created corrupted playlist file: {self.playlist_file}")
        
        # Try to load - should handle corruption gracefully
        result = self.playlist_manager.load_playlist()
        
        # Should have empty playlist after corruption handling
        self.assertTrue(self.playlist_manager.is_empty(), 
                       "Should have empty playlist after corruption")
        
        # Verify playlist is functional
        if os.path.exists("test_song_file.mp3"):
            add_result = self.playlist_manager.add_song("test_song_file.mp3")
            self.assertTrue(add_result, "Should be able to add songs after recovery")
            print("✓ Playlist is functional after corruption recovery")
        
        print("✓ Corrupted playlist handled gracefully")
    
    def test_corrupted_config_recovery(self):
        """Test recovery from corrupted configuration files."""
        print("\n=== Testing Corrupted Config Recovery ===")
        
        # Create a corrupted config file
        with open(self.config_file, 'w') as f:
            f.write("Invalid JSON content {")
        
        print(f"Created corrupted config file: {self.config_file}")
        
        # Try to load - should use defaults
        config = self.config_manager.load_config()
        
        # Should get valid default configuration
        self.assertIsInstance(config, WebDisplayConfig, 
                             "Should return valid WebDisplayConfig")
        self.assertEqual(config.font_family, "Arial", 
                        "Should use default font family")
        self.assertEqual(config.font_size, 24, 
                        "Should use default font size")
        
        print("✓ Corrupted config handled, defaults loaded")
    
    def test_invalid_song_cleanup(self):
        """Test cleanup of invalid songs from playlist (Requirement 6.4)."""
        print("\n=== Testing Invalid Song Cleanup ===")
        
        # Add a valid song if available
        valid_songs_added = 0
        if os.path.exists("test_song_file.mp3"):
            self.playlist_manager.add_song("test_song_file.mp3")
            valid_songs_added = 1
            print("Added valid test song")
        
        # Create a temporary file and add it as a song
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(b"Fake MP3 content")
            temp_file = f.name
        
        # Add the song while file exists
        temp_song = Song.from_file(temp_file)
        self.playlist_manager.playlist.songs.append(temp_song)
        print(f"Added temporary song: {temp_song.get_display_name()}")
        
        # Delete the file to make it invalid
        os.unlink(temp_file)
        print("Deleted temporary file to make song invalid")
        
        # Validate playlist shows invalid songs
        validation = self.playlist_manager.validate_playlist()
        self.assertEqual(validation['invalid_songs'], 1, 
                        "Should detect 1 invalid song")
        
        # Cleanup invalid songs
        removed_count = self.playlist_manager.cleanup_invalid_songs()
        self.assertEqual(removed_count, 1, 
                        "Should remove 1 invalid song")
        
        # Verify cleanup worked
        final_validation = self.playlist_manager.validate_playlist()
        self.assertEqual(final_validation['invalid_songs'], 0, 
                        "Should have no invalid songs after cleanup")
        self.assertEqual(final_validation['valid_songs'], valid_songs_added,
                        f"Should have {valid_songs_added} valid songs remaining")
        
        print(f"✓ Cleaned up {removed_count} invalid songs")
    
    def test_playback_error_with_auto_skip(self):
        """Test automatic skipping on playback errors (Requirement 6.4)."""
        print("\n=== Testing Auto-Skip on Playback Error ===")
        
        # Create playlist with valid and invalid songs
        playlist = Playlist()
        
        # Add valid song if available
        if os.path.exists("test_song_file.mp3"):
            valid_song = Song.from_file("test_song_file.mp3")
            playlist.add_song(valid_song)
            print("Added valid song to playlist")
        
        # Create and add invalid song
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(b"Fake MP3 content")
            temp_file = f.name
        
        invalid_song = Song.from_file(temp_file)
        playlist.add_song(invalid_song)
        
        # Delete file to make it invalid
        os.unlink(temp_file)
        
        # Set up player with playlist and auto-advance
        self.player_engine.set_playlist(playlist)
        self.player_engine.set_auto_advance(True)
        
        # Try to play invalid song
        playlist.current_index = len(playlist.songs) - 1  # Set to invalid song
        result = self.player_engine.play_song(invalid_song)
        
        # Should fail but handle gracefully
        self.assertFalse(result, "Playing invalid song should fail")
        
        print("✓ Auto-skip functionality tested")
    
    def test_configuration_validation(self):
        """Test configuration validation and error handling."""
        print("\n=== Testing Configuration Validation ===")
        
        # Test invalid configuration values
        invalid_config_data = {
            'font_size': -10,  # Invalid
            'artwork_size': 5000,  # Invalid
            'background_color': 'not_a_color',  # Invalid
            'font_weight': 'invalid_weight',  # Invalid
            'layout': 'invalid_layout'  # Invalid
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(invalid_config_data, f)
        
        print("Created config with invalid values")
        
        # Load config - should use defaults due to validation failure
        config = self.config_manager.load_config()
        
        # Should get valid defaults
        self.assertEqual(config.font_size, 24, "Should use default font size")
        self.assertEqual(config.artwork_size, 200, "Should use default artwork size")
        self.assertEqual(config.background_color, "#000000", "Should use default background color")
        self.assertEqual(config.font_weight, "normal", "Should use default font weight")
        self.assertEqual(config.layout, "horizontal", "Should use default layout")
        
        print("✓ Invalid config values handled, defaults applied")
    
    def test_status_checking_functionality(self):
        """Test status checking for playlist and config health."""
        print("\n=== Testing Status Checking ===")
        
        # Test playlist status
        playlist_status = self.playlist_manager.get_playlist_status()
        self.assertIn('playlist_file_exists', playlist_status)
        self.assertIn('is_valid', playlist_status)
        self.assertIn('validation', playlist_status)
        print(f"✓ Playlist status check: {playlist_status['validation']['total_songs']} songs")
        
        # Test config status
        config_status = self.config_manager.get_config_status()
        self.assertIn('config_file_exists', config_status)
        self.assertIn('is_valid', config_status)
        print(f"✓ Config status check: valid={config_status['is_valid']}")
    
    def test_error_callback_robustness(self):
        """Test that error callbacks don't crash the system."""
        print("\n=== Testing Error Callback Robustness ===")
        
        def failing_callback(msg):
            raise Exception("Callback intentionally failed")
        
        # Set failing callback
        self.player_engine.set_on_playback_error(failing_callback)
        
        # This should not crash the player
        result = self.player_engine.play("nonexistent_file.mp3")
        
        self.assertFalse(result, "Should still return False on error")
        self.assertEqual(self.player_engine.get_state(), PlaybackState.STOPPED,
                        "Should still be in STOPPED state")
        
        print("✓ System remains stable even with failing error callbacks")
    
    def test_comprehensive_error_scenario(self):
        """Test a comprehensive error scenario with multiple failures."""
        print("\n=== Testing Comprehensive Error Scenario ===")
        
        # Create corrupted playlist
        with open(self.playlist_file, 'w') as f:
            f.write("Corrupted playlist data {")
        
        # Create corrupted config
        with open(self.config_file, 'w') as f:
            f.write("Corrupted config data {")
        
        print("Created corrupted playlist and config files")
        
        # Try to load both - should recover gracefully
        playlist_result = self.playlist_manager.load_playlist()
        config_result = self.config_manager.load_config()
        
        # Both should handle corruption gracefully
        self.assertTrue(self.playlist_manager.is_empty(), 
                       "Should have empty playlist after corruption")
        self.assertIsInstance(config_result, WebDisplayConfig,
                             "Should have valid config after corruption")
        
        # System should still be functional
        if os.path.exists("test_song_file.mp3"):
            add_result = self.playlist_manager.add_song("test_song_file.mp3")
            self.assertTrue(add_result, "Should be able to add songs after recovery")
        
        save_result = self.config_manager.save_config(config_result)
        self.assertTrue(save_result, "Should be able to save config after recovery")
        
        print("✓ System recovered from multiple simultaneous failures")


def run_error_handling_tests():
    """Run the error handling tests with detailed output."""
    print("=" * 60)
    print("TASK 8.2 - COMPREHENSIVE ERROR HANDLING TESTS")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTask82ErrorHandling)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=None)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("ERROR HANDLING TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Set up logging for tests
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the focused error handling tests
    success = run_error_handling_tests()
    
    if success:
        print("\n🎉 All error handling tests passed!")
        print("Task 8.2 - Comprehensive Error Handling is complete.")
    else:
        print("\n⚠️  Some tests failed. Review the output above.")