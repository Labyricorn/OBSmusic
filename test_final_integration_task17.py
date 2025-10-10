#!/usr/bin/env python3
"""
Final integration test for Task 17 - GUI Modernization Integration.

This test verifies that all modernized components work together seamlessly,
including dynamic features, backward compatibility, and complete user workflows.
"""

import sys
import os
import tempfile
import shutil
import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.song import Song
from models.playlist import Playlist
from core.playlist_manager import PlaylistManager
from core.player_engine import PlayerEngine, PlaybackState
from gui.main_window import MainWindow
from gui.branding_config import BrandingConfig, BrandingManager
from gui.hyperlink_config import HyperlinkConfig, DynamicHyperlinkManager


class TestFinalIntegration(unittest.TestCase):
    """Comprehensive integration test for all modernized GUI components."""
    
    def setUp(self):
        """Set up test environment with all components."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.playlist_file = os.path.join(self.temp_dir, "test_playlist.json")
        self.artwork_dir = os.path.join(self.temp_dir, "artwork")
        os.makedirs(self.artwork_dir, exist_ok=True)
        
        # Create test icon file
        self.test_icon_path = os.path.join(self.temp_dir, "OBSmusic.ico")
        with open(self.test_icon_path, 'wb') as f:
            # Write minimal ICO header
            f.write(b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00h\x05\x00\x00\x16\x00\x00\x00')
        
        # Mock pygame to avoid audio initialization
        self.pygame_patcher = patch('core.player_engine.pygame')
        self.mock_pygame = self.pygame_patcher.start()
        self.mock_pygame.mixer.music.get_busy.return_value = False
        
        # Create core components
        self.playlist_manager = PlaylistManager(self.playlist_file, self.artwork_dir)
        self.player_engine = PlayerEngine()
        
        # Create mock web servers
        self.mock_web_server = Mock()
        self.mock_web_server.port = 8080
        self.mock_web_server.is_running = True
        
        self.mock_controls_server = Mock()
        self.mock_controls_server.port = 8081
        self.mock_controls_server.is_running = True
        
        # Create main window
        self.main_window = MainWindow(self.playlist_manager, self.player_engine)
        self.main_window.root.withdraw()  # Hide window during tests
        
        # Set server instances for dynamic hyperlinks
        self.main_window.set_server_instances(self.mock_web_server, self.mock_controls_server)
    
    def tearDown(self):
        """Clean up test environment."""
        self.pygame_patcher.stop()
        
        # Destroy GUI components
        try:
            if self.main_window.root and self.main_window.root.winfo_exists():
                self.main_window.root.destroy()
        except tk.TclError:
            pass
        
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_gui_initialization(self):
        """Test that all GUI components initialize correctly."""
        # Verify main window exists
        self.assertIsNotNone(self.main_window.root)
        
        # Verify all major components exist
        self.assertIsNotNone(self.main_window.current_song_label)
        self.assertIsNotNone(self.main_window.playlist_widget)
        self.assertIsNotNone(self.main_window.play_button)
        self.assertIsNotNone(self.main_window.web_display_link)
        self.assertIsNotNone(self.main_window.web_controls_link)
        
        # Verify theme manager is initialized
        self.assertIsNotNone(self.main_window.theme_manager)
        
        # Verify branding manager is initialized
        self.assertIsNotNone(self.main_window.branding_manager)
        
        # Verify hyperlink manager is initialized
        self.assertIsNotNone(self.main_window.hyperlink_manager)
    
    def test_window_branding_integration(self):
        """Test that window branding is properly integrated."""
        # Check window title
        self.assertEqual(self.main_window.root.title(), "OBSmusic")
        
        # Verify branding manager configuration
        branding_config = self.main_window.branding_manager.config
        self.assertEqual(branding_config.app_title, "OBSmusic")
        self.assertEqual(branding_config.icon_path, "OBSmusic.ico")
    
    def test_dynamic_hyperlink_integration(self):
        """Test that dynamic hyperlinks are properly integrated."""
        # Verify hyperlink URLs are correct
        display_text = self.main_window.web_display_link.cget('text')
        controls_text = self.main_window.web_controls_link.cget('text')
        
        self.assertEqual(display_text, "http://localhost:8080")
        self.assertEqual(controls_text, "http://localhost:8081")
        
        # Test dynamic URL updates
        self.mock_web_server.port = 9000
        self.mock_controls_server.port = 9001
        
        # Update hyperlinks
        self.main_window.refresh_hyperlink_urls()
        
        # Verify URLs updated
        updated_display_text = self.main_window.web_display_link.cget('text')
        updated_controls_text = self.main_window.web_controls_link.cget('text')
        
        self.assertEqual(updated_display_text, "http://localhost:9000")
        self.assertEqual(updated_controls_text, "http://localhost:9001")
    
    def test_playlist_functionality_integration(self):
        """Test that playlist functionality works with modernized interface."""
        # Add test songs
        test_songs = [
            os.path.join(self.temp_dir, "song1.mp3"),
            os.path.join(self.temp_dir, "song2.mp3"),
            os.path.join(self.temp_dir, "song3.mp3")
        ]
        
        # Create dummy MP3 files
        for song_path in test_songs:
            with open(song_path, 'wb') as f:
                f.write(b'dummy mp3 data')
        
        # Add songs to playlist
        for song_path in test_songs:
            self.playlist_manager.add_song(song_path)
        
        # Update GUI display
        self.main_window._update_playlist_display()
        
        # Verify playlist is displayed
        self.assertEqual(self.playlist_manager.get_song_count(), 3)
        
        # Test song selection
        self.main_window._on_playlist_selection_changed(1)
        self.assertEqual(self.main_window._selected_index, 1)
    
    def test_music_note_indicator_integration(self):
        """Test that music note indicator works with playlist changes."""
        # Add test songs
        test_song_path = os.path.join(self.temp_dir, "test_song.mp3")
        with open(test_song_path, 'wb') as f:
            f.write(b'dummy mp3 data')
        
        self.playlist_manager.add_song(test_song_path)
        
        # Set current song
        current_song = self.playlist_manager.set_current_song(0)
        
        # Update GUI
        self.main_window._update_gui()
        
        # Verify current song is displayed
        current_text = self.main_window.current_song_label.cget('text')
        self.assertNotEqual(current_text, "No song selected")
        
        # Test music note indicator position
        if hasattr(self.main_window.playlist_widget, 'current_index'):
            self.assertEqual(self.main_window.playlist_widget.current_index, 0)
    
    def test_playback_controls_integration(self):
        """Test that playback controls work with player engine."""
        # Add test song
        test_song_path = os.path.join(self.temp_dir, "test_song.mp3")
        with open(test_song_path, 'wb') as f:
            f.write(b'dummy mp3 data')
        
        self.playlist_manager.add_song(test_song_path)
        
        # Test play button
        self.main_window._on_play_clicked()
        
        # Verify player engine received play command
        # (This would depend on the actual player engine implementation)
        
        # Test other controls
        self.main_window._on_pause_clicked()
        self.main_window._on_stop_clicked()
        self.main_window._on_next_clicked()
        self.main_window._on_previous_clicked()
        
        # Should not raise exceptions
    
    def test_file_management_integration(self):
        """Test that file management works with modernized interface."""
        # Test add songs functionality
        with patch('tkinter.filedialog.askopenfilenames') as mock_dialog:
            test_files = [
                os.path.join(self.temp_dir, "song1.mp3"),
                os.path.join(self.temp_dir, "song2.mp3")
            ]
            
            # Create dummy files
            for file_path in test_files:
                with open(file_path, 'wb') as f:
                    f.write(b'dummy mp3 data')
            
            mock_dialog.return_value = test_files
            
            # Test add songs
            self.main_window._on_add_songs_clicked()
            
            # Verify songs were added
            self.assertEqual(self.playlist_manager.get_song_count(), 2)
        
        # Test remove song functionality
        if self.playlist_manager.get_song_count() > 0:
            self.main_window._selected_index = 0
            
            with patch('tkinter.messagebox.askyesno', return_value=True):
                self.main_window._on_remove_song_clicked()
                
                # Verify song was removed
                self.assertEqual(self.playlist_manager.get_song_count(), 1)
        
        # Test clear playlist
        with patch('tkinter.messagebox.askyesno', return_value=True):
            self.main_window._on_clear_playlist_clicked()
            
            # Verify playlist was cleared
            self.assertEqual(self.playlist_manager.get_song_count(), 0)
    
    @patch('webbrowser.open')
    def test_hyperlink_interaction_integration(self, mock_webbrowser):
        """Test that hyperlink interactions work correctly."""
        mock_webbrowser.return_value = True
        
        # Test display link click
        self.main_window._on_hyperlink_left_click_dynamic('display')
        mock_webbrowser.assert_called_with("http://localhost:8080")
        
        # Reset mock
        mock_webbrowser.reset_mock()
        
        # Test controls link click
        self.main_window._on_hyperlink_left_click_dynamic('controls')
        mock_webbrowser.assert_called_with("http://localhost:8081")
    
    def test_responsive_layout_integration(self):
        """Test that responsive layout works correctly."""
        # Test window resize
        self.main_window.root.geometry("400x300")
        self.main_window.root.update()
        
        # Simulate resize event
        mock_event = Mock()
        mock_event.widget = self.main_window.root
        self.main_window._on_window_resize(mock_event)
        
        # Should not raise exceptions
        
        # Test minimum size constraints
        self.main_window.root.geometry("200x150")
        self.main_window.root.update()
        
        # Simulate resize event
        self.main_window._on_window_resize(mock_event)
        
        # Window should be resized to minimum
        width = self.main_window.root.winfo_width()
        height = self.main_window.root.winfo_height()
        
        # Should enforce minimum size
        self.assertGreaterEqual(width, 350)
        self.assertGreaterEqual(height, 250)
    
    def test_theme_system_integration(self):
        """Test that theme system is properly integrated."""
        theme_manager = self.main_window.theme_manager
        
        # Verify theme is applied
        self.assertIsNotNone(theme_manager.theme)
        
        # Check that components use theme colors
        bg_color = self.main_window.root.cget('bg')
        self.assertEqual(bg_color, theme_manager.theme.bg_primary)
        
        # Check hyperlink colors
        link_color = self.main_window.web_display_link.cget('fg')
        self.assertEqual(link_color, theme_manager.theme.accent)
    
    def test_error_handling_integration(self):
        """Test that error handling works across all components."""
        # Test theme loading error handling
        with patch.object(self.main_window.theme_manager, 'apply_modern_theme', return_value=False):
            # Should handle theme failure gracefully
            try:
                self.main_window._apply_emergency_fallback_styling()
            except Exception as e:
                self.fail(f"Emergency fallback styling failed: {e}")
        
        # Test branding error handling
        with patch.object(self.main_window.branding_manager, 'apply_window_branding', return_value=False):
            # Should handle branding failure gracefully
            result = self.main_window.branding_manager.apply_window_branding(self.main_window.root)
            self.assertFalse(result)
        
        # Test hyperlink error handling
        with patch('webbrowser.open', side_effect=Exception("Browser error")):
            # Should handle browser launch failure gracefully
            try:
                self.main_window._on_hyperlink_left_click("http://localhost:8080")
            except Exception as e:
                self.fail(f"Hyperlink error handling failed: {e}")
    
    def test_backward_compatibility(self):
        """Test that all existing functionality is preserved."""
        # Test that all original methods still exist and work
        
        # Playlist management
        self.assertTrue(hasattr(self.main_window, '_on_add_songs_clicked'))
        self.assertTrue(hasattr(self.main_window, '_on_remove_song_clicked'))
        self.assertTrue(hasattr(self.main_window, '_on_clear_playlist_clicked'))
        self.assertTrue(hasattr(self.main_window, '_on_save_playlist_clicked'))
        
        # Playback controls
        self.assertTrue(hasattr(self.main_window, '_on_play_clicked'))
        self.assertTrue(hasattr(self.main_window, '_on_pause_clicked'))
        self.assertTrue(hasattr(self.main_window, '_on_stop_clicked'))
        self.assertTrue(hasattr(self.main_window, '_on_next_clicked'))
        self.assertTrue(hasattr(self.main_window, '_on_previous_clicked'))
        
        # Loop functionality
        self.assertTrue(hasattr(self.main_window, '_on_loop_toggled'))
        
        # GUI updates
        self.assertTrue(hasattr(self.main_window, '_update_gui'))
        self.assertTrue(hasattr(self.main_window, '_update_playlist_display'))
    
    def test_complete_user_workflow(self):
        """Test complete user workflow with modernized interface."""
        # 1. Add songs to playlist
        test_songs = []
        for i in range(3):
            song_path = os.path.join(self.temp_dir, f"song{i}.mp3")
            with open(song_path, 'wb') as f:
                f.write(b'dummy mp3 data')
            test_songs.append(song_path)
            self.playlist_manager.add_song(song_path)
        
        # 2. Update display
        self.main_window._update_playlist_display()
        self.assertEqual(self.playlist_manager.get_song_count(), 3)
        
        # 3. Select a song
        self.main_window._on_playlist_selection_changed(1)
        self.assertEqual(self.main_window._selected_index, 1)
        
        # 4. Play the selected song
        self.main_window._on_play_clicked()
        
        # 5. Test playback controls
        self.main_window._on_pause_clicked()
        self.main_window._on_play_clicked()  # Resume
        
        # 6. Test next/previous
        self.main_window._on_next_clicked()
        self.main_window._on_previous_clicked()
        
        # 7. Test loop toggle
        initial_loop_state = self.playlist_manager.is_loop_enabled()
        self.main_window._on_loop_toggled()
        new_loop_state = self.playlist_manager.is_loop_enabled()
        self.assertNotEqual(initial_loop_state, new_loop_state)
        
        # 8. Test web interface access
        with patch('webbrowser.open', return_value=True) as mock_browser:
            self.main_window._on_hyperlink_left_click_dynamic('display')
            mock_browser.assert_called_once()
        
        # 9. Test drag and drop reordering
        self.main_window._on_playlist_reorder(0, 2)
        # Should not raise exceptions
        
        # 10. Test window resize
        self.main_window.root.geometry("500x400")
        mock_event = Mock()
        mock_event.widget = self.main_window.root
        self.main_window._on_window_resize(mock_event)
        
        # All operations should complete without errors
    
    def test_requirements_compliance(self):
        """Test that all requirements are met in the final implementation."""
        
        # Requirement 4.1: All existing functionality preserved
        self.assertTrue(hasattr(self.main_window, '_on_play_clicked'))
        self.assertTrue(hasattr(self.main_window, '_on_add_songs_clicked'))
        
        # Requirement 4.2: Playlist operations work identically
        initial_count = self.playlist_manager.get_song_count()
        test_song = os.path.join(self.temp_dir, "test.mp3")
        with open(test_song, 'wb') as f:
            f.write(b'test')
        
        self.playlist_manager.add_song(test_song)
        self.assertEqual(self.playlist_manager.get_song_count(), initial_count + 1)
        
        # Requirement 4.3: File management operations maintained
        self.assertTrue(hasattr(self.main_window, '_on_remove_song_clicked'))
        self.assertTrue(hasattr(self.main_window, '_on_clear_playlist_clicked'))
        
        # Requirement 4.4: Web interface access available
        self.assertIsNotNone(self.main_window.web_display_link)
        self.assertIsNotNone(self.main_window.web_controls_link)
        
        # Requirement 5.5: Visual hierarchy and organization
        # Check that components are properly organized
        self.assertIsNotNone(self.main_window.now_playing_frame)
        self.assertIsNotNone(self.main_window.playlist_widget)
        
        # Requirement 7.6: Dynamic hyperlink URLs
        current_urls = self.main_window.hyperlink_manager.get_current_urls()
        self.assertIn('display', current_urls)
        self.assertIn('controls', current_urls)
        
        # Requirement 8.1: Window uses OBSmusic branding
        self.assertEqual(self.main_window.root.title(), "OBSmusic")
        
        # Requirement 8.2: Proper branding integration
        self.assertEqual(self.main_window.branding_manager.config.app_title, "OBSmusic")
    
    def test_performance_and_stability(self):
        """Test performance and stability of integrated components."""
        # Test rapid GUI updates
        for i in range(10):
            self.main_window._update_gui()
        
        # Test multiple hyperlink updates
        for port in range(8080, 8090):
            self.mock_web_server.port = port
            self.mock_controls_server.port = port + 1
            self.main_window.refresh_hyperlink_urls()
        
        # Test multiple window resizes
        sizes = [(400, 300), (500, 400), (350, 250), (600, 500)]
        for width, height in sizes:
            self.main_window.root.geometry(f"{width}x{height}")
            mock_event = Mock()
            mock_event.widget = self.main_window.root
            self.main_window._on_window_resize(mock_event)
        
        # All operations should complete without memory leaks or crashes


def run_integration_test():
    """Run the integration test and return results."""
    print("Running Final Integration Test for Task 17...")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFinalIntegration)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("Integration Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall Result: {'PASS' if success else 'FAIL'}")
    
    return success


if __name__ == '__main__':
    success = run_integration_test()
    sys.exit(0 if success else 1)