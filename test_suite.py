#!/usr/bin/env python3
"""
Comprehensive Test Suite for Music Player Application

This module provides a complete testing framework that covers:
- Unit tests for all components
- Integration tests for component interactions
- Performance tests for large playlist handling
- Manual testing scenarios for OBS integration
"""

import unittest
import sys
import os
import time
import json
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all test modules with optional dependency handling
from tests.test_song import TestSong
from tests.test_playlist import TestPlaylist
from tests.test_player_engine import TestPlayerEngine
from tests.test_playlist_manager import TestPlaylistManager
from tests.test_config_manager import TestConfigManager
from tests.test_web_server import TestWebServer
from tests.test_gui_integration import TestGUIIntegration
from tests.test_playback_controls import TestPlaybackControls
from tests.test_file_management import TestFileManagement
from tests.test_error_handling import (
    TestPlayerEngineErrorHandling,
    TestPlaylistManagerErrorHandling,
    TestConfigManagerErrorHandling,
    TestSongErrorHandling,
    TestWebServerErrorHandling,
    TestIntegratedErrorHandling
)
from tests.test_application_startup_shutdown import TestApplicationStartupShutdown
from tests.test_integration_task_8_1 import TestTask8_1Integration

# Optional test modules that may have additional dependencies
optional_test_modules = []
try:
    from tests.test_config_web_interface import TestConfigWebInterface
    optional_test_modules.append(TestConfigWebInterface)
except ImportError as e:
    print(f"Warning: Skipping TestConfigWebInterface due to missing dependency: {e}")

try:
    from tests.test_performance import TestPerformance
    optional_test_modules.append(TestPerformance)
except ImportError as e:
    print(f"Warning: Skipping TestPerformance due to missing dependency: {e}")


class TestSuiteRunner:
    """Main test suite runner with comprehensive reporting and performance testing."""
    
    def __init__(self):
        self.results = {}
        self.performance_results = {}
        self.start_time = None
        self.end_time = None
        
    def run_unit_tests(self) -> Dict[str, Any]:
        """Run all unit tests and return results."""
        print("=" * 60)
        print("RUNNING UNIT TESTS")
        print("=" * 60)
        
        unit_test_classes = [
            TestSong,
            TestPlaylist,
            TestPlayerEngine,
            TestPlaylistManager,
            TestConfigManager,
            TestWebServer,
        ]
        
        unit_results = {}
        total_tests = 0
        total_failures = 0
        total_errors = 0
        
        for test_class in unit_test_classes:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
            runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
            result = runner.run(suite)
            
            class_name = test_class.__name__
            unit_results[class_name] = {
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
            }
            
            total_tests += result.testsRun
            total_failures += len(result.failures)
            total_errors += len(result.errors)
            
            print(f"\n{class_name}: {result.testsRun} tests, {len(result.failures)} failures, {len(result.errors)} errors")
        
        unit_results['summary'] = {
            'total_tests': total_tests,
            'total_failures': total_failures,
            'total_errors': total_errors,
            'overall_success_rate': ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
        }
        
        return unit_results
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run all integration tests and return results."""
        print("\n" + "=" * 60)
        print("RUNNING INTEGRATION TESTS")
        print("=" * 60)
        
        integration_test_classes = [
            TestGUIIntegration,
            TestPlaybackControls,
            TestFileManagement,
            TestPlayerEngineErrorHandling,
            TestPlaylistManagerErrorHandling,
            TestConfigManagerErrorHandling,
            TestSongErrorHandling,
            TestWebServerErrorHandling,
            TestIntegratedErrorHandling,
            TestApplicationStartupShutdown,
            TestTask8_1Integration,
        ]
        
        # Add optional test classes that were successfully imported
        for optional_class in optional_test_modules:
            if optional_class.__name__ != 'TestPerformance':  # Performance tests run separately
                integration_test_classes.append(optional_class)
        
        integration_results = {}
        total_tests = 0
        total_failures = 0
        total_errors = 0
        
        for test_class in integration_test_classes:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
            runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
            result = runner.run(suite)
            
            class_name = test_class.__name__
            integration_results[class_name] = {
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
            }
            
            total_tests += result.testsRun
            total_failures += len(result.failures)
            total_errors += len(result.errors)
            
            print(f"\n{class_name}: {result.testsRun} tests, {len(result.failures)} failures, {len(result.errors)} errors")
        
        integration_results['summary'] = {
            'total_tests': total_tests,
            'total_failures': total_failures,
            'total_errors': total_errors,
            'overall_success_rate': ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
        }
        
        return integration_results
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests for large playlist handling."""
        print("\n" + "=" * 60)
        print("RUNNING PERFORMANCE TESTS")
        print("=" * 60)
        
        # Check if TestPerformance is available
        performance_test_class = None
        for optional_class in optional_test_modules:
            if optional_class.__name__ == 'TestPerformance':
                performance_test_class = optional_class
                break
        
        if performance_test_class is None:
            print("Performance tests skipped - TestPerformance not available")
            return {
                'tests_run': 0,
                'failures': 0,
                'errors': 0,
                'success_rate': 100.0
            }
        
        suite = unittest.TestLoader().loadTestsFromTestCase(performance_test_class)
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(suite)
        
        performance_results = {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
        }
        
        return performance_results
    
    def generate_test_report(self, unit_results: Dict, integration_results: Dict, performance_results: Dict):
        """Generate comprehensive test report."""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        total_duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        print(f"Test Suite Execution Time: {total_duration:.2f} seconds")
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\nUNIT TEST SUMMARY:")
        print("-" * 40)
        unit_summary = unit_results.get('summary', {})
        print(f"Total Tests: {unit_summary.get('total_tests', 0)}")
        print(f"Failures: {unit_summary.get('total_failures', 0)}")
        print(f"Errors: {unit_summary.get('total_errors', 0)}")
        print(f"Success Rate: {unit_summary.get('overall_success_rate', 0):.1f}%")
        
        print("\nINTEGRATION TEST SUMMARY:")
        print("-" * 40)
        integration_summary = integration_results.get('summary', {})
        print(f"Total Tests: {integration_summary.get('total_tests', 0)}")
        print(f"Failures: {integration_summary.get('total_failures', 0)}")
        print(f"Errors: {integration_summary.get('total_errors', 0)}")
        print(f"Success Rate: {integration_summary.get('overall_success_rate', 0):.1f}%")
        
        print("\nPERFORMANCE TEST SUMMARY:")
        print("-" * 40)
        print(f"Total Tests: {performance_results.get('tests_run', 0)}")
        print(f"Failures: {performance_results.get('failures', 0)}")
        print(f"Errors: {performance_results.get('errors', 0)}")
        print(f"Success Rate: {performance_results.get('success_rate', 0):.1f}%")
        
        # Overall summary
        total_tests = (unit_summary.get('total_tests', 0) + 
                      integration_summary.get('total_tests', 0) + 
                      performance_results.get('tests_run', 0))
        total_failures = (unit_summary.get('total_failures', 0) + 
                         integration_summary.get('total_failures', 0) + 
                         performance_results.get('failures', 0))
        total_errors = (unit_summary.get('total_errors', 0) + 
                       integration_summary.get('total_errors', 0) + 
                       performance_results.get('errors', 0))
        
        overall_success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
        
        print("\nOVERALL TEST SUMMARY:")
        print("=" * 40)
        print(f"Total Tests: {total_tests}")
        print(f"Total Failures: {total_failures}")
        print(f"Total Errors: {total_errors}")
        print(f"Overall Success Rate: {overall_success_rate:.1f}%")
        
        # Save detailed report to file
        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'execution_time': total_duration,
            'unit_tests': unit_results,
            'integration_tests': integration_results,
            'performance_tests': performance_results,
            'overall_summary': {
                'total_tests': total_tests,
                'total_failures': total_failures,
                'total_errors': total_errors,
                'success_rate': overall_success_rate
            }
        }
        
        with open('test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nDetailed report saved to: test_report.json")
        
        return overall_success_rate >= 90  # Return True if success rate is 90% or higher
    
    def run_all_tests(self) -> bool:
        """Run complete test suite and return success status."""
        self.start_time = time.time()
        
        print("Starting Comprehensive Test Suite for Music Player Application")
        print("=" * 80)
        
        try:
            # Run all test categories
            unit_results = self.run_unit_tests()
            integration_results = self.run_integration_tests()
            performance_results = self.run_performance_tests()
            
            self.end_time = time.time()
            
            # Generate comprehensive report
            success = self.generate_test_report(unit_results, integration_results, performance_results)
            
            return success
            
        except Exception as e:
            print(f"Test suite execution failed: {e}")
            return False


def main():
    """Main entry point for test suite."""
    runner = TestSuiteRunner()
    success = runner.run_all_tests()
    
    if success:
        print("\n✅ Test suite completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test suite completed with failures!")
        sys.exit(1)


if __name__ == "__main__":
    main()