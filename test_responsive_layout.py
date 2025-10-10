#!/usr/bin/env python3
"""
Test script for responsive layout behavior in the modernized GUI.

This script tests the window resize functionality, minimum size constraints,
and responsive component scaling as specified in task 9.
"""

import sys
import os
import tkinter as tk
from pathlib import Path
import time
import logging

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from models.song import Song
from models.playlist import Playlist
from core.playlist_manager import PlaylistManager
from core.player_engine import PlayerEngine
from gui.main_window import MainWindow

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def create_test_playlist():
    """Create a test playlist using existing songs."""
    playlist_manager = PlaylistManager()
    
    # Load existing playlist (which should have songs already)
    # The PlaylistManager will automatically load from data/playlist.json
    
    return playlist_manager


def test_responsive_layout():
    """Test responsive layout behavior."""
    print("Testing Responsive Layout Behavior")
    print("=" * 50)
    
    # Create test components
    playlist_manager = create_test_playlist()
    player_engine = PlayerEngine(playlist_manager)
    
    # Create main window
    main_window = MainWindow(playlist_manager, player_engine)
    root = main_window.root
    
    # Test initial size
    print(f"Initial window size: {root.winfo_width()}x{root.winfo_height()}")
    
    def test_resize_scenarios():
        """Test different resize scenarios."""
        test_cases = [
            # (width, height, description)
            (400, 300, "Default size"),
            (350, 250, "Minimum size"),
            (300, 200, "Below minimum (should be corrected)"),
            (600, 400, "Larger size"),
            (800, 600, "Much larger size"),
            (350, 300, "Minimum width, normal height"),
            (500, 250, "Normal width, minimum height")
        ]
        
        for width, height, description in test_cases:
            print(f"\nTesting: {description} ({width}x{height})")
            
            # Set window size
            root.geometry(f"{width}x{height}")
            root.update()
            
            # Allow time for resize handling
            time.sleep(0.1)
            
            # Check actual size after resize handling
            actual_width = root.winfo_width()
            actual_height = root.winfo_height()
            print(f"  Actual size after resize: {actual_width}x{actual_height}")
            
            # Check if minimum constraints were enforced
            min_width = main_window.theme_manager.theme.window_min_width
            min_height = main_window.theme_manager.theme.window_min_height
            
            if actual_width >= min_width and actual_height >= min_height:
                print(f"  ✓ Minimum size constraints respected")
            else:
                print(f"  ✗ Minimum size constraints violated!")
                print(f"    Expected minimum: {min_width}x{min_height}")
            
            # Test component visibility and layout
            try:
                # Check if all components are still visible and properly laid out
                components_visible = all([
                    main_window.now_playing_frame.winfo_viewable(),
                    main_window.playlist_widget.winfo_viewable(),
                    main_window.play_button.winfo_viewable(),
                    main_window.web_display_link.winfo_viewable()
                ])
                
                if components_visible:
                    print(f"  ✓ All components remain visible")
                else:
                    print(f"  ✗ Some components not visible")
                    
            except Exception as e:
                print(f"  ⚠ Error checking component visibility: {e}")
    
    def test_text_truncation():
        """Test text truncation at different window sizes."""
        print(f"\nTesting text truncation behavior:")
        
        # Set a song with a long title (use existing song)
        if playlist_manager.get_song_count() > 0:
            playlist_manager.set_current_song(0)  # Use first available song
            main_window._update_current_song_display()
        
        # Test at different widths
        widths = [350, 400, 500, 600]
        for width in widths:
            root.geometry(f"{width}x300")
            root.update()
            time.sleep(0.1)
            
            current_text = main_window.current_song_label.cget("text")
            print(f"  Width {width}px: '{current_text}'")
    
    def test_playlist_responsiveness():
        """Test playlist area responsiveness."""
        print(f"\nTesting playlist area responsiveness:")
        
        heights = [250, 300, 400, 500]
        for height in heights:
            root.geometry(f"400x{height}")
            root.update()
            time.sleep(0.1)
            
            # Calculate expected playlist height
            fixed_height = (
                main_window.theme_manager.theme.now_playing_height +
                main_window.theme_manager.theme.controls_height +
                main_window.theme_manager.theme.file_panel_height +
                30 +  # Web links
                (main_window.theme_manager.theme.spacing_small * 10)
            )
            expected_playlist_height = max(100, height - fixed_height)
            
            print(f"  Window height {height}px: Expected playlist area ~{expected_playlist_height}px")
    
    # Schedule tests to run after GUI is fully initialized
    root.after(100, test_resize_scenarios)
    root.after(2000, test_text_truncation)
    root.after(4000, test_playlist_responsiveness)
    
    # Add a close button for manual testing
    def close_test():
        print("\nTest completed. Closing window...")
        root.quit()
    
    root.after(6000, close_test)  # Auto-close after 6 seconds
    
    print("\nStarting GUI for responsive layout testing...")
    print("The window will automatically resize to test different scenarios.")
    print("Watch the console output for test results.")
    
    # Start the GUI
    root.mainloop()


def test_minimum_size_enforcement():
    """Test that minimum size constraints are properly enforced."""
    print("\nTesting Minimum Size Enforcement")
    print("=" * 40)
    
    # Create minimal test setup
    playlist_manager = PlaylistManager()
    player_engine = PlayerEngine(playlist_manager)
    main_window = MainWindow(playlist_manager, player_engine)
    root = main_window.root
    
    min_width = main_window.theme_manager.theme.window_min_width
    min_height = main_window.theme_manager.theme.window_min_height
    
    print(f"Minimum size constraints: {min_width}x{min_height}")
    
    # Test cases that should trigger minimum size enforcement
    test_cases = [
        (200, 150, "Very small"),
        (300, 200, "Below minimum"),
        (349, 249, "Just below minimum"),
        (350, 250, "Exactly minimum"),
        (351, 251, "Just above minimum")
    ]
    
    for width, height, description in test_cases:
        print(f"\nTesting {description}: {width}x{height}")
        
        # Try to set the size
        root.geometry(f"{width}x{height}")
        root.update()
        time.sleep(0.1)
        
        # Check actual size
        actual_width = root.winfo_width()
        actual_height = root.winfo_height()
        
        print(f"  Requested: {width}x{height}")
        print(f"  Actual: {actual_width}x{actual_height}")
        
        # Verify minimum constraints
        if actual_width >= min_width and actual_height >= min_height:
            print(f"  ✓ Minimum constraints enforced correctly")
        else:
            print(f"  ✗ Minimum constraints not enforced!")
    
    root.after(100, root.quit)
    root.mainloop()


if __name__ == "__main__":
    print("Responsive Layout Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Basic responsive layout behavior
        test_responsive_layout()
        
        # Test 2: Minimum size enforcement
        test_minimum_size_enforcement()
        
        print("\n" + "=" * 60)
        print("All responsive layout tests completed!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()