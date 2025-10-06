#!/usr/bin/env python3
"""
Test script to verify artwork functionality is working correctly.
"""

import requests
import json
import os
import sys
from pathlib import Path

def test_artwork_functionality():
    """Test all aspects of the artwork functionality."""
    base_url = "http://127.0.0.1:8080"
    
    print("Testing Music Player Artwork Functionality")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("1. Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/api/song", timeout=5)
        if response.status_code == 200:
            print("   ✓ Server is running and responding")
        else:
            print(f"   ✗ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Cannot connect to server: {e}")
        return False
    
    # Test 2: Check current song data
    print("2. Testing current song data...")
    try:
        song_data = response.json()
        print(f"   Title: {song_data.get('title', 'N/A')}")
        print(f"   Artist: {song_data.get('artist', 'N/A')}")
        print(f"   Artwork URL: {song_data.get('artwork_url', 'N/A')}")
        print(f"   Playing: {song_data.get('is_playing', 'N/A')}")
        
        if song_data.get('artwork_url'):
            print("   ✓ Song has artwork URL")
        else:
            print("   ✗ Song missing artwork URL")
            return False
    except json.JSONDecodeError:
        print("   ✗ Invalid JSON response")
        return False
    
    # Test 3: Check if artwork file is accessible
    print("3. Testing artwork file accessibility...")
    artwork_url = song_data.get('artwork_url')
    if artwork_url:
        try:
            artwork_response = requests.get(f"{base_url}{artwork_url}", timeout=5)
            if artwork_response.status_code == 200:
                print(f"   ✓ Artwork file accessible (Content-Type: {artwork_response.headers.get('Content-Type', 'Unknown')})")
                print(f"   ✓ File size: {len(artwork_response.content)} bytes")
            else:
                print(f"   ✗ Artwork file not accessible (Status: {artwork_response.status_code})")
                return False
        except requests.exceptions.RequestException as e:
            print(f"   ✗ Error accessing artwork: {e}")
            return False
    
    # Test 4: Check placeholder image
    print("4. Testing placeholder image...")
    try:
        placeholder_response = requests.get(f"{base_url}/static/artwork/placeholder.jpg", timeout=5)
        if placeholder_response.status_code == 200:
            print("   ✓ Placeholder image accessible")
            print(f"   ✓ Placeholder size: {len(placeholder_response.content)} bytes")
        else:
            print(f"   ✗ Placeholder image not accessible (Status: {placeholder_response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Error accessing placeholder: {e}")
        return False
    
    # Test 5: Check main display page
    print("5. Testing main display page...")
    try:
        display_response = requests.get(f"{base_url}/", timeout=5)
        if display_response.status_code == 200:
            html_content = display_response.text
            if 'song-artwork' in html_content and artwork_url in html_content:
                print("   ✓ Display page contains artwork element")
                print("   ✓ Display page has correct artwork URL")
            else:
                print("   ✗ Display page missing artwork elements")
                return False
        else:
            print(f"   ✗ Display page not accessible (Status: {display_response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Error accessing display page: {e}")
        return False
    
    # Test 6: Check local artwork files
    print("6. Testing local artwork files...")
    artwork_dir = Path("data/artwork")
    if artwork_dir.exists():
        artwork_files = list(artwork_dir.glob("*.jpg"))
        print(f"   ✓ Found {len(artwork_files)} artwork files locally")
        
        # Check if placeholder exists
        placeholder_path = artwork_dir / "placeholder.jpg"
        if placeholder_path.exists():
            print("   ✓ Placeholder image exists locally")
        else:
            print("   ✗ Placeholder image missing locally")
            return False
    else:
        print("   ✗ Artwork directory not found")
        return False
    
    print("\n" + "=" * 50)
    print("✓ All artwork functionality tests passed!")
    print("✓ Album artwork is properly loading and displaying")
    print("✓ Placeholder system is working correctly")
    return True

if __name__ == "__main__":
    success = test_artwork_functionality()
    sys.exit(0 if success else 1)