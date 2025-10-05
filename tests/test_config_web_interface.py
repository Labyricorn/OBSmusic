"""
Integration tests for the configuration web interface.
Tests configuration form functionality, real-time preview, and persistence.
"""

import unittest
import json
import tempfile
import os
import shutil
import time
import requests
from unittest.mock import patch, MagicMock
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException

# Import the web server and config manager modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from web.server import WebServer
from core.config_manager import ConfigManager, WebDisplayConfig


class TestConfigurationWebInterface(unittest.TestCase):
    """Integration tests for configuration web interface functionality."""
    
    def setUp(self):
        """Set up test fixtures with running server."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create data directory and templates
        os.makedirs('data', exist_ok=True)
        os.makedirs('web/templates', exist_ok=True)
        
        # Copy the actual config template for testing
        config_template_path = os.path.join(self.original_cwd, 'web', 'templates', 'config.html')
        if os.path.exists(config_template_path):
            shutil.copy2(config_template_path, 'web/templates/config.html')
        else:
            # Create a minimal config template for testing
            self._create_minimal_config_template()
        
        # Create display template
        self._create_display_template()
        
        # Initialize config manager with test directory
        self.config_manager = ConfigManager(config_file="data/config.json")
        
        # Start web server for testing
        self.web_server = WebServer(host='127.0.0.1', port=8080)
        self.server_started = self.web_server.start()
        
        # Wait for server to start
        if self.server_started:
            time.sleep(1)  # Give server time to start
            self.base_url = f"http://127.0.0.1:{self.web_server.port}"
        
        # Set up Chrome driver for Selenium tests (headless mode)
        self.driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
        except WebDriverException:
            # Skip Selenium tests if Chrome driver not available
            self.driver = None
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.driver:
            self.driver.quit()
        
        if hasattr(self, 'web_server') and self.web_server.is_running:
            self.web_server.stop()
        
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def _create_minimal_config_template(self):
        """Create a minimal config template for testing."""
        template_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Config Test</title></head>
        <body>
            <form id="config-form">
                <input type="text" id="font-family" name="font_family" value="Arial">
                <input type="number" id="font-size" name="font_size" value="24">
                <input type="color" id="background-color" name="background_color" value="#000000">
                <input type="color" id="text-color" name="text_color" value="#ffffff">
                <input type="checkbox" id="show-artwork" name="show_artwork" checked>
                <select id="layout" name="layout">
                    <option value="horizontal">Horizontal</option>
                    <option value="vertical">Vertical</option>
                </select>
                <button type="submit">Save</button>
            </form>
            <div id="preview-display"></div>
        </body>
        </html>
        """
        with open('web/templates/config.html', 'w') as f:
            f.write(template_content)
    
    def _create_display_template(self):
        """Create a minimal display template for testing."""
        template_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Display Test</title></head>
        <body>
            <div id="song-title">{{ song_data.title }}</div>
            <div id="song-artist">{{ song_data.artist }}</div>
        </body>
        </html>
        """
        with open('web/templates/display.html', 'w') as f:
            f.write(template_content)
    
    def test_config_api_get_default(self):
        """Test GET /api/config returns default configuration."""
        if not self.server_started:
            self.skipTest("Web server failed to start")
        
        response = requests.get(f"{self.base_url}/api/config")
        self.assertEqual(response.status_code, 200)
        
        config = response.json()
        self.assertEqual(config['font_family'], 'Arial')
        self.assertEqual(config['font_size'], 24)
        self.assertEqual(config['background_color'], '#000000')
        self.assertEqual(config['text_color'], '#ffffff')
        self.assertTrue(config['show_artwork'])
        self.assertEqual(config['layout'], 'horizontal')
    
    def test_config_api_post_valid_config(self):
        """Test POST /api/config with valid configuration data."""
        if not self.server_started:
            self.skipTest("Web server failed to start")
        
        new_config = {
            'font_family': 'Helvetica',
            'font_size': 32,
            'font_weight': 'bold',
            'background_color': '#ff0000',
            'text_color': '#00ff00',
            'accent_color': '#0000ff',
            'show_artwork': False,
            'artwork_size': 150,
            'layout': 'vertical'
        }
        
        response = requests.post(
            f"{self.base_url}/api/config",
            json=new_config,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result['success'])
        
        # Verify configuration was saved
        get_response = requests.get(f"{self.base_url}/api/config")
        saved_config = get_response.json()
        
        self.assertEqual(saved_config['font_family'], 'Helvetica')
        self.assertEqual(saved_config['font_size'], 32)
        self.assertEqual(saved_config['background_color'], '#ff0000')
        self.assertFalse(saved_config['show_artwork'])
        self.assertEqual(saved_config['layout'], 'vertical')
    
    def test_config_api_post_invalid_json(self):
        """Test POST /api/config with invalid JSON data."""
        if not self.server_started:
            self.skipTest("Web server failed to start")
        
        response = requests.post(
            f"{self.base_url}/api/config",
            data="invalid json",
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 400)
        result = response.json()
        self.assertIn('error', result)
    
    def test_config_api_post_empty_data(self):
        """Test POST /api/config with no data."""
        if not self.server_started:
            self.skipTest("Web server failed to start")
        
        response = requests.post(
            f"{self.base_url}/api/config",
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 400)
        result = response.json()
        self.assertIn('error', result)
    
    def test_config_persistence(self):
        """Test that configuration changes persist across server restarts."""
        if not self.server_started:
            self.skipTest("Web server failed to start")
        
        # Save a configuration
        test_config = {
            'font_family': 'Georgia',
            'font_size': 28,
            'background_color': '#333333',
            'layout': 'overlay'
        }
        
        response = requests.post(
            f"{self.base_url}/api/config",
            json=test_config,
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        
        # Stop and restart server
        self.web_server.stop()
        time.sleep(0.5)
        
        new_server = WebServer(host='127.0.0.1', port=8081)
        server_started = new_server.start()
        self.assertTrue(server_started)
        
        try:
            time.sleep(1)
            new_base_url = f"http://127.0.0.1:{new_server.port}"
            
            # Verify configuration persisted
            response = requests.get(f"{new_base_url}/api/config")
            self.assertEqual(response.status_code, 200)
            
            config = response.json()
            self.assertEqual(config['font_family'], 'Georgia')
            self.assertEqual(config['font_size'], 28)
            self.assertEqual(config['background_color'], '#333333')
            self.assertEqual(config['layout'], 'overlay')
        finally:
            new_server.stop()
    
    def test_config_page_loads(self):
        """Test that the configuration page loads successfully."""
        if not self.server_started:
            self.skipTest("Web server failed to start")
        
        response = requests.get(f"{self.base_url}/config")
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.headers.get('content-type', ''))
    
    @unittest.skipIf(not os.environ.get('RUN_SELENIUM_TESTS'), "Selenium tests disabled")
    def test_config_form_elements_present(self):
        """Test that all configuration form elements are present."""
        if not self.server_started or not self.driver:
            self.skipTest("Web server or Chrome driver not available")
        
        self.driver.get(f"{self.base_url}/config")
        
        # Check for form elements
        self.assertTrue(self.driver.find_element(By.ID, "config-form"))
        self.assertTrue(self.driver.find_element(By.ID, "font-family"))
        self.assertTrue(self.driver.find_element(By.ID, "font-size"))
        self.assertTrue(self.driver.find_element(By.ID, "background-color"))
        self.assertTrue(self.driver.find_element(By.ID, "text-color"))
        self.assertTrue(self.driver.find_element(By.ID, "show-artwork"))
        self.assertTrue(self.driver.find_element(By.ID, "layout"))
    
    @unittest.skipIf(not os.environ.get('RUN_SELENIUM_TESTS'), "Selenium tests disabled")
    def test_config_form_submission(self):
        """Test configuration form submission through browser."""
        if not self.server_started or not self.driver:
            self.skipTest("Web server or Chrome driver not available")
        
        self.driver.get(f"{self.base_url}/config")
        
        # Wait for form to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "config-form"))
        )
        
        # Change some form values
        font_family = Select(self.driver.find_element(By.ID, "font-family"))
        font_family.select_by_value("Helvetica")
        
        font_size = self.driver.find_element(By.ID, "font-size")
        font_size.clear()
        font_size.send_keys("30")
        
        layout = Select(self.driver.find_element(By.ID, "layout"))
        layout.select_by_value("vertical")
        
        # Submit form
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Wait a moment for submission to complete
        time.sleep(2)
        
        # Verify configuration was saved by checking API
        response = requests.get(f"{self.base_url}/api/config")
        config = response.json()
        
        self.assertEqual(config['font_family'], 'Helvetica')
        self.assertEqual(config['font_size'], 30)
        self.assertEqual(config['layout'], 'vertical')
    
    @unittest.skipIf(not os.environ.get('RUN_SELENIUM_TESTS'), "Selenium tests disabled")
    def test_real_time_preview_updates(self):
        """Test that preview updates in real-time when form values change."""
        if not self.server_started or not self.driver:
            self.skipTest("Web server or Chrome driver not available")
        
        self.driver.get(f"{self.base_url}/config")
        
        # Wait for page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "preview-display"))
        )
        
        preview_display = self.driver.find_element(By.ID, "preview-display")
        
        # Get initial background color
        initial_bg = preview_display.value_of_css_property("background-color")
        
        # Change background color
        color_input = self.driver.find_element(By.ID, "background-color")
        self.driver.execute_script("arguments[0].value = '#ff0000';", color_input)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", color_input)
        
        # Wait for preview to update
        time.sleep(1)
        
        # Check that background color changed
        updated_bg = preview_display.value_of_css_property("background-color")
        self.assertNotEqual(initial_bg, updated_bg)
    
    def test_config_validation_invalid_color(self):
        """Test configuration validation with invalid color values."""
        config_manager = ConfigManager(config_file="data/test_config.json")
        
        # Test invalid color format
        invalid_config = {
            'background_color': 'invalid_color',
            'text_color': '#gggggg',
            'font_size': 24
        }
        
        # Should use default values for invalid colors
        config = WebDisplayConfig.from_dict(invalid_config)
        self.assertEqual(config.background_color, '#000000')  # Default
        self.assertEqual(config.text_color, '#ffffff')  # Default
        self.assertEqual(config.font_size, 24)  # Valid value should be kept
    
    def test_config_validation_invalid_font_size(self):
        """Test configuration validation with invalid font size."""
        # Test negative font size
        invalid_config = {
            'font_size': -10,
            'artwork_size': 0,
            'font_family': 'Arial'
        }
        
        config = WebDisplayConfig.from_dict(invalid_config)
        self.assertEqual(config.font_size, 24)  # Default
        self.assertEqual(config.artwork_size, 200)  # Default
        self.assertEqual(config.font_family, 'Arial')  # Valid value kept
    
    def test_config_validation_invalid_layout(self):
        """Test configuration validation with invalid layout value."""
        invalid_config = {
            'layout': 'invalid_layout',
            'font_weight': 'invalid_weight'
        }
        
        config = WebDisplayConfig.from_dict(invalid_config)
        self.assertEqual(config.layout, 'horizontal')  # Default
        self.assertEqual(config.font_weight, 'normal')  # Default
    
    def test_config_file_corruption_recovery(self):
        """Test recovery from corrupted configuration file."""
        if not self.server_started:
            self.skipTest("Web server failed to start")
        
        # Create corrupted config file
        with open('data/config.json', 'w') as f:
            f.write('{"invalid": json content}')
        
        # Request should still work with defaults
        response = requests.get(f"{self.base_url}/api/config")
        self.assertEqual(response.status_code, 200)
        
        config = response.json()
        self.assertEqual(config['font_family'], 'Arial')  # Default values
        self.assertEqual(config['font_size'], 24)
    
    def test_config_directory_creation(self):
        """Test that data directory is created if it doesn't exist."""
        # Remove data directory
        if os.path.exists('data'):
            shutil.rmtree('data')
        
        # Create config manager - should create directory
        config_manager = ConfigManager(config_file="data/new_config.json")
        config = WebDisplayConfig(font_family="Test")
        
        success = config_manager.save_config(config)
        self.assertTrue(success)
        self.assertTrue(os.path.exists('data'))
        self.assertTrue(os.path.exists('data/new_config.json'))


if __name__ == '__main__':
    # Set environment variable to run Selenium tests if Chrome driver is available
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.quit()
        os.environ['RUN_SELENIUM_TESTS'] = '1'
    except WebDriverException:
        print("Chrome driver not available, skipping Selenium tests")
    
    unittest.main()