import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PerfectoLibrary.keywords._devices import _DeviceKeywords


class TestDeviceKeywords(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.device_keywords = _DeviceKeywords()
        
        # Create mock objects
        self.mock_bi = Mock()
        self.mock_driver = Mock()
        self.mock_appium_lib = Mock()
        
        # Set up driver capabilities
        self.mock_driver.capabilities = {
            'reportPdfUrl': 'http://example.com/report.pdf',
            'devicename': 'test_device',
            'executionId': 'test_execution_123'
        }
        
        # Configure mocks
        self.mock_appium_lib._current_application.return_value = self.mock_driver
        self.mock_bi.get_library_instance.return_value = self.mock_appium_lib
        
        # Patch BuiltIn
        self.device_keywords.bi = self.mock_bi

    def test_check_driver_success(self):
        """Test successful driver check."""
        result = self.device_keywords._check_driver()
        
        self.assertTrue(result)
        self.assertEqual(self.device_keywords.driver, self.mock_driver)
        self.assertEqual(self.device_keywords.reportPdfUrl, 'http://example.com/report.pdf')

    def test_check_driver_failure(self):
        """Test driver check failure."""
        self.mock_bi.get_library_instance.side_effect = Exception("No AppiumLibrary")
        
        result = self.device_keywords._check_driver()
        
        self.assertFalse(result)
        self.mock_bi.log_to_console.assert_called_with(
            "Your script is not using Appium Driver, devices keywords will not be able to performed"
        )

    def test_install_application(self):
        """Test application installation."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.install_application("test_repo", "true")
        
        expected_params = {
            'sensorInstrument': 'sensor',
            'file': 'test_repo'
        }
        self.mock_driver.execute_script.assert_called_with('mobile:application:install', expected_params)

    def test_install_application_no_sensor(self):
        """Test application installation without sensor instrumentation."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.install_application("test_repo", "false")
        
        expected_params = {
            'sensorInstrument': 'nosensor',
            'file': 'test_repo'
        }
        self.mock_driver.execute_script.assert_called_with('mobile:application:install', expected_params)

    @patch.object(_DeviceKeywords, '_check_driver', return_value=False)
    def test_install_application_no_driver(self, mock_check):
        """Test application installation when no driver is available."""
        self.device_keywords.install_application("test_repo", "true")
        
        # Should not call execute_script if no driver
        self.mock_driver.execute_script.assert_not_called()

    def test_uninstall_application(self):
        """Test application uninstallation."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.uninstall_application("com.example.app")
        
        expected_params = {'identifier': 'com.example.app'}
        self.mock_driver.execute_script.assert_called_with('mobile:application:uninstall', expected_params)

    def test_start_application_by_name(self):
        """Test starting application by name."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.start_application_by_name("com.example.app")
        
        expected_params = {'identifier': 'com.example.app'}
        self.mock_driver.execute_script.assert_called_with('mobile:application:open', expected_params)

    def test_close_application_by_name(self):
        """Test closing application by name."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.close_application_by_name("com.example.app")
        
        expected_params = {'identifier': 'com.example.app'}
        self.mock_driver.execute_script.assert_called_with('mobile:application:close', expected_params)

    def test_open_system_browser(self):
        """Test opening system browser."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.open_system_browser()
        
        expected_params = {'automation': 'os'}
        self.mock_driver.execute_script.assert_called_with('mobile:browser:open', expected_params)

    def test_browser_execute_script(self):
        """Test browser script execution."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.browser_execute_script("alert('test')")
        
        expected_params = {
            'script': "alert('test')",
            'timeout': '35'
        }
        self.mock_driver.execute_script.assert_called_with('mobile:browser:execute', expected_params)

    def test_browser_execute_script_with_timeout(self):
        """Test browser script execution with custom timeout."""
        self.device_keywords.driver = self.mock_driver
        
        # Test the second browser_execute_script method with timeout parameter
        self.device_keywords.browser_execute_script("alert('test')", "60")
        
        expected_params = {
            'script': "alert('test')",
            'timeout': '60'
        }
        self.mock_driver.execute_script.assert_called_with('mobile:browser:execute', expected_params)

    def test_browser_execute_repo_script(self):
        """Test browser repository script execution."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.browser_execute_repo_script("repo/script.js")
        
        expected_params = {
            'repositoryFile': 'repo/script.js',
            'timeout': '35'
        }
        self.mock_driver.execute_script.assert_called_with('mobile:browser:execute', expected_params)

    def test_maximize_window(self):
        """Test window maximization."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.maximize_window()
        
        self.mock_driver.maximize_window.assert_called_once()

    def test_scroll_to_element(self):
        """Test scrolling to element."""
        self.device_keywords.driver = self.mock_driver
        mock_element = Mock()
        mock_element.GetId.return_value = "element_id_123"
        
        with patch('selenium.webdriver.common.by.By') as mock_by:
            mock_by.xpath.return_value = "xpath_locator"
            self.mock_driver.findElement.return_value = mock_element
            
            self.device_keywords.scroll_to_element("//div[@id='test']")
            
            expected_params = {
                'element': 'element_id_123',
                'toVisible': 'any'
            }
            self.mock_driver.execute_script.assert_called_with('mobile:scroll', expected_params)

    def test_rotate(self):
        """Test device rotation."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.rotate('portrait', 'screen')
        
        expected_params = {
            'state': 'portrait',
            'method': 'screen'
        }
        self.mock_driver.execute_script.assert_called_with('mobile:device:rotate', expected_params)

    def test_rotate_default_params(self):
        """Test device rotation with default parameters."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.rotate()
        
        expected_params = {
            'state': 'landscape',
            'method': 'device'
        }
        self.mock_driver.execute_script.assert_called_with('mobile:device:rotate', expected_params)

    def test_drag(self):
        """Test drag operation."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.drag("10", "20", "30", "40", "3")
        
        expected_params = {
            'location': '10,20,30,40',
            'duration': '3'
        }
        self.mock_driver.execute_script.assert_called_with('mobile:touch:drag', expected_params)

    def test_drag_default_duration(self):
        """Test drag operation with default duration."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.drag("10%", "20%", "30%", "40%")
        
        expected_params = {
            'location': '10%,20%,30%,40%',
            'duration': '5'
        }
        self.mock_driver.execute_script.assert_called_with('mobile:touch:drag', expected_params)

    def test_gesture_zoom(self):
        """Test zoom gesture."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.gesture("25%", "25%", "75%", "75%", "Zoom", "3")
        
        expected_params = {
            'start': '25%,25%',
            'end': '75%,75%',
            'operation': 'Zoom',
            'duration': '3'
        }
        self.mock_driver.execute_script.assert_called_with('mobile:touch:gesture', expected_params)

    def test_gesture_pinch(self):
        """Test pinch gesture."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.gesture("75%", "75%", "25%", "25%", "Pinch")
        
        expected_params = {
            'start': '75%,75%',
            'end': '25%,25%',
            'operation': 'Pinch',
            'duration': '5'
        }
        self.mock_driver.execute_script.assert_called_with('mobile:touch:gesture', expected_params)

    def test_swipe(self):
        """Test swipe operation."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.swipe("50%", "80%", "50%", "20%", "2")
        
        expected_params = {
            'start': '50%,80%',
            'end': '50%,20%',
            'duration': '2'
        }
        self.mock_driver.execute_script.assert_called_with('mobile:touch:swipe', expected_params)

    def test_perfecto_tap(self):
        """Test Perfecto tap operation."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.perfecto_tap("50%", "50%", "1")
        
        expected_params = {
            'location': '50%,50%',
            'duration': '1'
        }
        self.mock_driver.execute_script.assert_called_with('mobile:touch:tap', expected_params)

    def test_trackball_roll(self):
        """Test trackball roll operation."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.trackball_roll("5,10")
        
        expected_params = {'distance': '5,10'}
        self.mock_driver.execute_script.assert_called_with('mobile:trackball:roll', expected_params)

    def test_button_image_click(self):
        """Test button image click."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.button_image_click("images/button.png", 90)
        
        expected_params = {
            'label': 'images/button.png',
            'threshold': 90,
            'imageBounds.needleBound': 30
        }
        self.mock_driver.execute_script.assert_called_with('mobile:button-image:click', expected_params)

    def test_button_image_click_default_threshold(self):
        """Test button image click with default threshold."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.button_image_click("images/button.png")
        
        expected_params = {
            'label': 'images/button.png',
            'threshold': 80,
            'imageBounds.needleBound': 30
        }
        self.mock_driver.execute_script.assert_called_with('mobile:button-image:click', expected_params)

    def test_button_text_click_case_sensitive(self):
        """Test button text click with case sensitivity."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.button_text_click("Submit", "false")
        
        expected_params = {
            'label': 'Submit',
            'ignorecase': 'case',
            'threshold': 80
        }
        self.mock_driver.execute_script.assert_called_with('mobile:button-text:click', expected_params)

    def test_button_text_click_ignore_case(self):
        """Test button text click ignoring case."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.button_text_click("Submit", "true")
        
        expected_params = {
            'label': 'Submit',
            'ignorecase': 'nocase',
            'threshold': 80
        }
        self.mock_driver.execute_script.assert_called_with('mobile:button-text:click', expected_params)

    def test_find_image_in_screen_success(self):
        """Test finding image in screen successfully."""
        self.device_keywords.driver = self.mock_driver
        self.mock_driver.execute_script.return_value = "true"
        
        result = self.device_keywords.find_image_in_screen("images/target.png", "body")
        
        expected_params = {
            'content': 'images/target.png',
            'context': 'body'
        }
        self.mock_driver.execute_script.assert_called_with('mobile:image:find', expected_params)
        self.assertEqual(result, "true")

    def test_find_image_in_screen_no_driver(self):
        """Test finding image in screen with no driver."""
        self.device_keywords.driver = None
        
        result = self.device_keywords.find_image_in_screen("images/target.png")
        
        self.assertFalse(result)

    def test_find_text_in_screen_success(self):
        """Test finding text in screen successfully."""
        self.device_keywords.driver = self.mock_driver
        self.mock_driver.execute_script.return_value = "true"
        
        result = self.device_keywords.find_text_in_screen("Welcome", "all")
        
        expected_params = {
            'content': 'Welcome',
            'context': 'all'
        }
        self.mock_driver.execute_script.assert_called_with('mobile:text:find', expected_params)
        self.assertEqual(result, "true")

    def test_find_text_in_screen_default_context(self):
        """Test finding text in screen with default context."""
        self.device_keywords.driver = self.mock_driver
        self.mock_driver.execute_script.return_value = "false"
        
        result = self.device_keywords.find_text_in_screen("Welcome")
        
        expected_params = {
            'content': 'Welcome',
            'context': 'body'
        }
        self.mock_driver.execute_script.assert_called_with('mobile:text:find', expected_params)
        self.assertEqual(result, "false")

    def test_device_info(self):
        """Test getting device information."""
        self.device_keywords.driver = self.mock_driver
        self.mock_driver.execute_script.return_value = "iPhone 12"
        
        result = self.device_keywords.device_info("model")
        
        expected_params = {'property': 'model'}
        self.mock_driver.execute_script.assert_called_with('mobile:device:info', expected_params)
        self.assertEqual(result, "iPhone 12")

    def test_device_info_no_driver(self):
        """Test getting device info with no driver."""
        self.device_keywords.driver = None
        
        result = self.device_keywords.device_info("model")
        
        self.assertFalse(result)

    @patch('time.sleep')
    def test_keep_session_alive(self, mock_sleep):
        """Test keeping session alive."""
        self.device_keywords.driver = self.mock_driver
        
        result = self.device_keywords.keep_session_alive(120)
        
        # Should call device_info twice (at 0 and 60 seconds)
        self.assertEqual(self.mock_driver.execute_script.call_count, 3)
        self.assertTrue(result)
        # Should sleep twice for 60 seconds each
        self.assertEqual(mock_sleep.call_count, 3)

    @patch('time.sleep')
    def test_keep_session_alive_no_driver(self, mock_sleep):
        """Test keeping session alive with no driver."""
        self.device_keywords.driver = None
        
        result = self.device_keywords.keep_session_alive(60)
        
        self.assertFalse(result)

    def test_perform_accessibility_audit(self):
        """Test performing accessibility audit."""
        self.device_keywords.driver = self.mock_driver
        
        self.device_keywords.perform_accessibility_audit("login_page")
        
        expected_params = {'tag': 'login_page'}
        self.mock_driver.execute_script.assert_called_with('mobile:checkAccessibility:audit', expected_params)

    def test_perform_ai_checkpoint_true(self):
        """Test AI checkpoint returning true."""
        self.device_keywords.driver = self.mock_driver
        self.mock_driver.execute_script.return_value = "true"
        
        result = self.device_keywords.perform_ai_checkpoint("Is login successful?", True)
        
        expected_params = {
            'validation': 'Is login successful?',
            'reasoning': True
        }
        self.mock_driver.execute_script.assert_called_with('perfecto:ai:validation', expected_params)
        self.assertTrue(result)

    def test_perform_ai_checkpoint_false(self):
        """Test AI checkpoint returning false."""
        self.device_keywords.driver = self.mock_driver
        self.mock_driver.execute_script.return_value = "false"
        
        result = self.device_keywords.perform_ai_checkpoint("Is error displayed?")
        
        expected_params = {
            'validation': 'Is error displayed?',
            'reasoning': False
        }
        self.mock_driver.execute_script.assert_called_with('perfecto:ai:validation', expected_params)
        self.assertFalse(result)

    def test_perform_ai_user_action_success(self):
        """Test AI user action success."""
        self.device_keywords.driver = self.mock_driver
        self.mock_driver.execute_script.return_value = "true"
        
        result = self.device_keywords.perform_ai_user_action(
            "Click on the submit button", True, False
        )
        
        expected_params = {
            'action': 'Click on the submit button',
            'reasoning': True,
            'outputVariable': False
        }
        self.mock_driver.execute_script.assert_called_with('perfecto:ai:useractions', expected_params)
        self.assertTrue(result)

    def test_perform_ai_user_action_failure(self):
        """Test AI user action failure."""
        self.device_keywords.driver = self.mock_driver
        self.mock_driver.execute_script.return_value = "false"
        
        result = self.device_keywords.perform_ai_user_action("Invalid action")
        
        expected_params = {
            'action': 'Invalid action',
            'reasoning': False,
            'outputVariable': False
        }
        self.mock_driver.execute_script.assert_called_with('perfecto:ai:useractions', expected_params)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()