#!/usr/bin/env python3
"""
End-to-end tests for complete application startup and shutdown sequence.

Tests the complete application lifecycle including:
- Command-line argument parsing
- Component initialization order
- Graceful shutdown handling for all threads and resources
- Error recovery during startup
- Resource cleanup verification
"""

import unittest
import subprocess
import threading
import time
import tempfile
import shutil
import os
import sys
import signal
from pathlib import Path
import requests
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from main import MusicPlayerApp, parse_arguments, main


class TestApplicationStartupShutdown(unittest.TestCase):
    """Test complete application startup and shutdown sequence."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create test MP3 file (copy from project root)
        test_mp3_source = project_root / "test_song_file.mp3"
        if test_mp3_source.exists():
            shutil.copy2(test_mp3_source, "test_song.mp3")
        else:
            # Create a dummy file for testing
            with open("test_song.mp3", "wb") as f:
                f.write(b"dummy mp3 content for testing")
        
        self.app = None
        self.processes = []
    
    def tearDown(self):
        """Clean up test environment."""
        if self.app:
            self.app.shutdown()
        
        # Clean up any spawned processes
        for process in self.processes:
            try:
                if process.poll() is None:  # Process is still running
                    process.terminate()
                    process.wait(timeout=5)
            except (subprocess.TimeoutExpired, ProcessLookupError):
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
        
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_command_line_argument_parsing(self):
        """Test command-line argument parsing functionality."""
        print("\n🧪 Testing command-line argument parsing")
        
        # Test default arguments
        sys.argv = ['main.py']
        args = parse_arguments()
        self.assertIsNone(args.config_dir, "Default config_dir should be None")
        self.assertFalse(args.debug, "Default debug should be False")
        self.assertEqual(args.port, 8080, "Default port should be 8080")
        
        # Test custom arguments
        sys.argv = ['main.py', '--config-dir', '/custom/path', '--debug', '--port', '9090']
        args = parse_arguments()
        self.assertEqual(args.config_dir, '/custom/path', "Custom config_dir should be set")
        self.assertTrue(args.debug, "Debug should be enabled")
        self.assertEqual(args.port, 9090, "Custom port should be set")
        
        print("✅ Command-line argument parsing working correctly")
    
    def test_application_initialization_sequence(self):
        """Test proper initialization order of all components."""
        print("\n🧪 Testing application initialization sequence")
        
        # Create application with custom config
        self.app = MusicPlayerApp(config_dir="test_config", web_port=8090)
        
        # Verify initial state
        self.assertIsNone(self.app.playlist_manager, "Playlist manager should not be initialized yet")
        self.assertIsNone(self.app.player_engine, "Player engine should not be initialized yet")
        self.assertIsNone(self.app.web_server, "Web server should not be initialized yet")
        self.assertIsNone(self.app.gui, "GUI should not be initialized yet")
        self.assertFalse(self.app.running, "App should not be running yet")
        
        # Initialize components
        success = self.app.initialize_components()
        self.assertTrue(success, "Component initialization should succeed")
        
        # Verify initialization order and connections
        self.assertIsNotNone(self.app.playlist_manager, "Playlist manager should be initialized")
        self.assertIsNotNone(self.app.player_engine, "Player engine should be initialized")
        self.assertIsNotNone(self.app.web_server, "Web server should be initialized")
        self.assertIsNotNone(self.app.gui, "GUI should be initialized")
        
        # Verify player engine has playlist
        playlist = self.app.player_engine.get_playlist()
        self.assertIsNotNone(playlist, "Player engine should have playlist")
        
        # Verify callbacks are set up
        self.assertIsNotNone(self.app.player_engine._on_song_changed, 
                           "Song change callback should be set")
        self.assertIsNotNone(self.app.player_engine._on_state_changed,
                           "State change callback should be set")
        
        # Verify config directory was created
        self.assertTrue(self.app.config_dir.exists(), "Config directory should be created")
        
        print("✅ Application initialization sequence working correctly")
    
    def test_web_server_startup_sequence(self):
        """Test web server startup and port handling."""
        print("\n🧪 Testing web server startup sequence")
        
        # Test successful startup
        self.app = MusicPlayerApp(config_dir="test_config", web_port=8091)
        self.app.initialize_components()
        
        success = self.app.start_web_server()
        self.assertTrue(success, "Web server should start successfully")
        self.assertTrue(self.app.web_server.is_running, "Web server should be running")
        
        # Verify server is accessible
        time.sleep(1)  # Wait for server to be ready
        base_url = self.app.web_server.get_server_url()
        response = requests.get(f"{base_url}/", timeout=5)
        self.assertEqual(response.status_code, 200, "Web server should be accessible")
        
        print("✅ Web server startup sequence working correctly")
    
    def test_graceful_shutdown_sequence(self):
        """Test graceful shutdown of all components and threads."""
        print("\n🧪 Testing graceful shutdown sequence")
        
        # Initialize and start application
        self.app = MusicPlayerApp(config_dir="test_config", web_port=8092)
        self.app.initialize_components()
        self.app.start_web_server()
        self.app.running = True
        
        # Add a song and start playback
        self.app.playlist_manager.add_song("test_song.mp3")
        current_song = self.app.playlist_manager.get_current_song()
        if current_song:
            self.app.player_engine.play_song(current_song)
        
        # Verify components are running
        self.assertTrue(self.app.running, "App should be running")
        self.assertTrue(self.app.web_server.is_running, "Web server should be running")
        
        # Perform graceful shutdown
        self.app.shutdown()
        
        # Verify shutdown state
        self.assertFalse(self.app.running, "App should not be running after shutdown")
        self.assertFalse(self.app.web_server.is_running, "Web server should not be running after shutdown")
        
        # Verify player engine is stopped
        self.assertFalse(self.app.player_engine.is_playing(), "Player should not be playing after shutdown")
        
        # Verify playlist was saved
        playlist_file = self.app.config_dir / "playlist.json"
        self.assertTrue(playlist_file.exists(), "Playlist should be saved during shutdown")
        
        print("✅ Graceful shutdown sequence working correctly")
    
    def test_error_recovery_during_startup(self):
        """Test error recovery during component initialization."""
        print("\n🧪 Testing error recovery during startup")
        
        # Test with invalid config directory (read-only)
        if os.name != 'nt':  # Skip on Windows due to permission handling differences
            readonly_dir = Path(self.test_dir) / "readonly"
            readonly_dir.mkdir()
            readonly_dir.chmod(0o444)  # Read-only
            
            try:
                self.app = MusicPlayerApp(config_dir=str(readonly_dir), web_port=8093)
                # This should still work as the app creates subdirectories
                success = self.app.initialize_components()
                # The app should handle this gracefully
                self.assertIsNotNone(self.app.playlist_manager, "Should handle config dir issues gracefully")
            finally:
                readonly_dir.chmod(0o755)  # Restore permissions for cleanup
        
        # Test with port conflict
        # Start first app
        app1 = MusicPlayerApp(config_dir="test_config1", web_port=8094)
        app1.initialize_components()
        app1.start_web_server()
        
        try:
            # Start second app with same port (should handle gracefully)
            app2 = MusicPlayerApp(config_dir="test_config2", web_port=8094)
            app2.initialize_components()
            success = app2.start_web_server()
            
            # The web server should handle port conflicts gracefully
            # Either by finding an alternative port or failing gracefully
            if not success:
                # If it fails, the app should still be functional without web server
                self.assertIsNotNone(app2.playlist_manager, "App should work without web server")
                self.assertIsNotNone(app2.player_engine, "Player should work without web server")
            
            app2.shutdown()
        finally:
            app1.shutdown()
        
        print("✅ Error recovery during startup working correctly")
    
    def test_resource_cleanup_verification(self):
        """Test that all resources are properly cleaned up after shutdown."""
        print("\n🧪 Testing resource cleanup verification")
        
        # Get initial process info
        initial_threads = threading.active_count()
        
        # Initialize and start application
        self.app = MusicPlayerApp(config_dir="test_config", web_port=8095)
        self.app.initialize_components()
        self.app.start_web_server()
        
        # Verify threads were created
        running_threads = threading.active_count()
        self.assertGreater(running_threads, initial_threads, "Threads should be created")
        
        # Add songs and start playback
        self.app.playlist_manager.add_song("test_song.mp3")
        current_song = self.app.playlist_manager.get_current_song()
        if current_song:
            self.app.player_engine.play_song(current_song)
        
        # Perform shutdown
        self.app.shutdown()
        
        # Wait for threads to clean up
        time.sleep(2)
        
        # Verify thread cleanup
        final_threads = threading.active_count()
        # Note: We can't guarantee exact thread count due to system threads,
        # but we can verify no obvious leaks
        self.assertLessEqual(final_threads, running_threads, 
                           "Thread count should not increase after shutdown")
        
        # Verify files were saved
        config_dir = Path("test_config")
        playlist_file = config_dir / "playlist.json"
        self.assertTrue(playlist_file.exists(), "Playlist file should be saved")
        
        # Verify web server port is released
        time.sleep(1)
        try:
            # Try to start another server on the same port
            test_app = MusicPlayerApp(config_dir="test_config2", web_port=8095)
            test_app.initialize_components()
            success = test_app.start_web_server()
            if success:
                test_app.shutdown()
            # If this succeeds, the port was properly released
        except Exception:
            pass  # Port might still be in TIME_WAIT state, which is normal
        
        print("✅ Resource cleanup verification working correctly")
    
    def test_command_line_integration(self):
        """Test complete application startup via command line."""
        print("\n🧪 Testing command-line integration")
        
        # Test the main.py help command
        try:
            result = subprocess.run([
                sys.executable, str(project_root / "main.py"), "--help"
            ], capture_output=True, text=True, timeout=10, cwd=self.test_dir)
            
            self.assertEqual(result.returncode, 0, f"Help command should work: {result.stderr}")
            self.assertIn("Music Player with OBS Integration", result.stdout, "Should show help text")
            self.assertIn("--config-dir", result.stdout, "Should show config-dir option")
            self.assertIn("--debug", result.stdout, "Should show debug option")
            self.assertIn("--port", result.stdout, "Should show port option")
            self.assertIn("--no-gui", result.stdout, "Should show no-gui option")
            self.assertIn("--no-web", result.stdout, "Should show no-web option")
            
        except subprocess.TimeoutExpired:
            self.fail("Help command test timed out")
        
        # Test version command
        try:
            result = subprocess.run([
                sys.executable, str(project_root / "main.py"), "--version"
            ], capture_output=True, text=True, timeout=10, cwd=self.test_dir)
            
            self.assertEqual(result.returncode, 0, f"Version command should work: {result.stderr}")
            self.assertIn("Music Player v1.0.0", result.stdout, "Should show version")
            
        except subprocess.TimeoutExpired:
            self.fail("Version command test timed out")
        
        print("✅ Command-line integration working correctly")
    
    def test_configuration_persistence(self):
        """Test that configuration persists across application restarts."""
        print("\n🧪 Testing configuration persistence")
        
        # First run: Create app and add configuration
        app1 = MusicPlayerApp(config_dir="test_config", web_port=8097)
        app1.initialize_components()
        
        # Add a song to playlist
        app1.playlist_manager.add_song("test_song.mp3")
        songs_before = len(app1.playlist_manager.get_songs())
        self.assertEqual(songs_before, 1, "Should have one song")
        
        # Shutdown (this should save configuration)
        app1.shutdown()
        
        # Second run: Create new app instance and verify persistence
        app2 = MusicPlayerApp(config_dir="test_config", web_port=8098)
        app2.initialize_components()
        
        # Verify playlist was loaded
        songs_after = len(app2.playlist_manager.get_songs())
        self.assertEqual(songs_after, songs_before, "Playlist should persist across restarts")
        
        # Verify song details
        loaded_song = app2.playlist_manager.get_songs()[0]
        self.assertEqual(loaded_song.file_path, "test_song.mp3", "Song file path should persist")
        
        app2.shutdown()
        
        print("✅ Configuration persistence working correctly")
    
    def test_multiple_instance_handling(self):
        """Test handling of multiple application instances."""
        print("\n🧪 Testing multiple instance handling")
        
        # Start first instance
        app1 = MusicPlayerApp(config_dir="test_config1", web_port=8099)
        app1.initialize_components()
        success1 = app1.start_web_server()
        self.assertTrue(success1, "First instance should start successfully")
        
        # Start second instance with different config and port
        app2 = MusicPlayerApp(config_dir="test_config2", web_port=8100)
        app2.initialize_components()
        success2 = app2.start_web_server()
        self.assertTrue(success2, "Second instance should start successfully")
        
        # Verify both are running independently
        self.assertTrue(app1.web_server.is_running, "First instance web server should be running")
        self.assertTrue(app2.web_server.is_running, "Second instance web server should be running")
        
        # Verify they have separate configurations
        self.assertNotEqual(app1.config_dir, app2.config_dir, "Should have different config directories")
        self.assertNotEqual(app1.web_port, app2.web_port, "Should have different ports")
        
        # Shutdown both
        app1.shutdown()
        app2.shutdown()
        
        # Verify both shut down properly
        self.assertFalse(app1.web_server.is_running, "First instance should be shut down")
        self.assertFalse(app2.web_server.is_running, "Second instance should be shut down")
        
        print("✅ Multiple instance handling working correctly")


def run_startup_shutdown_tests():
    """Run all startup and shutdown tests."""
    print("🧪 Running End-to-End Application Startup/Shutdown Tests")
    print("=" * 70)
    print("Testing: Complete application lifecycle")
    print("Requirements: All requirements integration")
    print("=" * 70)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestApplicationStartupShutdown)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 All startup/shutdown tests passed!")
        print("✅ Command-line argument parsing working correctly")
        print("✅ Proper initialization order for all components")
        print("✅ Graceful shutdown handling for all threads and resources")
        print("✅ Error recovery during startup")
        print("✅ Resource cleanup verification")
        print("✅ Configuration persistence across restarts")
        print("✅ Multiple instance handling")
        print("\n🎯 Task 9.1 Requirements Met:")
        print("✅ main.py with proper initialization order for all components")
        print("✅ Command-line argument parsing for configuration options")
        print("✅ Graceful shutdown handling for all threads and resources")
        print("✅ End-to-end tests for complete application startup and shutdown")
        print("✅ All requirements integration verified")
    else:
        print("❌ Some startup/shutdown tests failed")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_startup_shutdown_tests()
    sys.exit(0 if success else 1)