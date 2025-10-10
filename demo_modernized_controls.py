#!/usr/bin/env python3
"""
Demo script for modernized playback control buttons.

This script demonstrates the enhanced control button styling with:
- 30px control panel height
- 24x24px buttons with modern flat design
- 4px button spacing
- Enhanced visual feedback and hover effects
- Modern button state management
"""

import sys
import tkinter as tk
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from models.playlist import Playlist
from core.playlist_manager import PlaylistManager
from core.player_engine import PlayerEngine, PlaybackState
from gui.main_window import MainWindow


def demo_modernized_controls():
    """Demonstrate the modernized control buttons."""
    print("Modernized Control Buttons Demo")
    print("=" * 40)
    print("Features demonstrated:")
    print("✓ 30px control panel height")
    print("✓ 24x24px buttons with modern flat design")
    print("✓ 4px button spacing")
    print("✓ Enhanced visual feedback")
    print("✓ Modern button state management")
    print("✓ Hover effects")
    print()
    
    # Create components
    playlist = Playlist()
    playlist_manager = PlaylistManager(playlist)
    player_engine = PlayerEngine(playlist_manager)
    
    # Create main window
    main_window = MainWindow(playlist_manager, player_engine)
    root = main_window.root
    
    # Add instructions
    instructions = tk.Label(
        root,
        text="Modernized Control Buttons Demo\n\n" +
             "• Control panel is 30px high with compact design\n" +
             "• Buttons are 24x24px with 4px spacing\n" +
             "• Hover over buttons to see modern hover effects\n" +
             "• Active button state is highlighted with accent color\n" +
             "• All buttons use flat modern design\n\n" +
             "Try clicking the buttons to see state changes!",
        bg="#2b2b2b",
        fg="#ffffff",
        font=("Segoe UI", 10),
        justify="left",
        padx=20,
        pady=10
    )
    instructions.grid(row=4, column=0, sticky="ew", padx=8, pady=8)
    
    # Simulate different states for demonstration
    def cycle_states():
        """Cycle through different playback states to show button styling."""
        states = [PlaybackState.STOPPED, PlaybackState.PLAYING, PlaybackState.PAUSED]
        current_state = [0]  # Use list to allow modification in nested function
        
        def next_state():
            state = states[current_state[0]]
            main_window._update_playback_controls(state)
            
            state_names = ["STOPPED", "PLAYING", "PAUSED"]
            print(f"Demonstrating {state_names[current_state[0]]} state")
            
            current_state[0] = (current_state[0] + 1) % len(states)
            root.after(3000, next_state)  # Change state every 3 seconds
        
        next_state()
    
    # Start state cycling after a short delay
    root.after(1000, cycle_states)
    
    print("Window opened. Watch the button states cycle automatically.")
    print("Close the window when done.")
    
    root.mainloop()


if __name__ == "__main__":
    demo_modernized_controls()