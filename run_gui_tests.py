#!/usr/bin/env python3
"""
Simple test runner for GUI modernization tests.

This script provides an easy way to run the comprehensive GUI modernization
test suite without needing to remember the full command line arguments.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tests.test_gui_modernization_suite import GUIModernizationTestSuite


def main():
    """Main entry point for running GUI modernization tests."""
    print("=" * 70)
    print("GUI MODERNIZATION TEST RUNNER")
    print("=" * 70)
    print()
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
    else:
        test_type = 'all'
    
    print(f"Running {test_type} tests...")
    print()
    
    if test_type == 'theme':
        result = GUIModernizationTestSuite.run_theme_tests()
    elif test_type == 'music-note':
        result = GUIModernizationTestSuite.run_music_note_tests()
    elif test_type == 'hyperlink':
        result = GUIModernizationTestSuite.run_hyperlink_tests()
    elif test_type == 'visual':
        result = GUIModernizationTestSuite.run_visual_regression_tests()
    else:
        result = GUIModernizationTestSuite.run_all_tests()
    
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    
    if result.wasSuccessful():
        print("✅ All tests passed successfully!")
        return 0
    else:
        print("❌ Some tests failed.")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)