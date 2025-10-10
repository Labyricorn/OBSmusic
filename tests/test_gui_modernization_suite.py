"""
Comprehensive test suite for GUI modernization.

This module runs all GUI modernization tests including theme system,
music note indicator, hyperlink interactions, and visual regression tests.
"""

import unittest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import all test modules
from tests.test_theme_system import TestModernTheme, TestThemeManager
from tests.test_music_note_indicator import TestMusicNoteIndicator
from tests.test_hyperlink_interactions import TestHyperlinkInteractions
from tests.test_visual_regression import TestVisualRegression


class GUIModernizationTestSuite:
    """Test suite for GUI modernization components."""
    
    @staticmethod
    def create_suite():
        """Create comprehensive test suite for GUI modernization.
        
        Returns:
            unittest.TestSuite: Complete test suite
        """
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Theme System Tests
        suite.addTest(loader.loadTestsFromTestCase(TestModernTheme))
        suite.addTest(loader.loadTestsFromTestCase(TestThemeManager))
        
        # Music Note Indicator Tests
        suite.addTest(loader.loadTestsFromTestCase(TestMusicNoteIndicator))
        
        # Hyperlink Interaction Tests
        suite.addTest(loader.loadTestsFromTestCase(TestHyperlinkInteractions))
        
        # Visual Regression Tests
        suite.addTest(loader.loadTestsFromTestCase(TestVisualRegression))
        
        return suite
    
    @staticmethod
    def run_all_tests(verbosity=2):
        """Run all GUI modernization tests.
        
        Args:
            verbosity: Test output verbosity level
            
        Returns:
            unittest.TestResult: Test results
        """
        suite = GUIModernizationTestSuite.create_suite()
        runner = unittest.TextTestRunner(verbosity=verbosity)
        return runner.run(suite)
    
    @staticmethod
    def run_theme_tests():
        """Run only theme system tests.
        
        Returns:
            unittest.TestResult: Test results
        """
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        suite.addTest(loader.loadTestsFromTestCase(TestModernTheme))
        suite.addTest(loader.loadTestsFromTestCase(TestThemeManager))
        
        runner = unittest.TextTestRunner(verbosity=2)
        return runner.run(suite)
    
    @staticmethod
    def run_music_note_tests():
        """Run only music note indicator tests.
        
        Returns:
            unittest.TestResult: Test results
        """
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        suite.addTest(loader.loadTestsFromTestCase(TestMusicNoteIndicator))
        
        runner = unittest.TextTestRunner(verbosity=2)
        return runner.run(suite)
    
    @staticmethod
    def run_hyperlink_tests():
        """Run only hyperlink interaction tests.
        
        Returns:
            unittest.TestResult: Test results
        """
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        suite.addTest(loader.loadTestsFromTestCase(TestHyperlinkInteractions))
        
        runner = unittest.TextTestRunner(verbosity=2)
        return runner.run(suite)
    
    @staticmethod
    def run_visual_regression_tests():
        """Run only visual regression tests.
        
        Returns:
            unittest.TestResult: Test results
        """
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        suite.addTest(loader.loadTestsFromTestCase(TestVisualRegression))
        
        runner = unittest.TextTestRunner(verbosity=2)
        return runner.run(suite)


def main():
    """Main entry point for running GUI modernization tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run GUI modernization tests')
    parser.add_argument('--test-type', choices=['all', 'theme', 'music-note', 'hyperlink', 'visual'],
                       default='all', help='Type of tests to run')
    parser.add_argument('--verbosity', type=int, choices=[0, 1, 2], default=2,
                       help='Test output verbosity level')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("GUI MODERNIZATION TEST SUITE")
    print("=" * 70)
    
    if args.test_type == 'all':
        print("Running all GUI modernization tests...")
        result = GUIModernizationTestSuite.run_all_tests(args.verbosity)
    elif args.test_type == 'theme':
        print("Running theme system tests...")
        result = GUIModernizationTestSuite.run_theme_tests()
    elif args.test_type == 'music-note':
        print("Running music note indicator tests...")
        result = GUIModernizationTestSuite.run_music_note_tests()
    elif args.test_type == 'hyperlink':
        print("Running hyperlink interaction tests...")
        result = GUIModernizationTestSuite.run_hyperlink_tests()
    elif args.test_type == 'visual':
        print("Running visual regression tests...")
        result = GUIModernizationTestSuite.run_visual_regression_tests()
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # Return appropriate exit code
    if result.failures or result.errors:
        return 1
    else:
        print("\nAll tests passed successfully!")
        return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)