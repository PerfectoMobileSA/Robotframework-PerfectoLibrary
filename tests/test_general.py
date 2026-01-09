import unittest
from unittest.mock import Mock, patch, MagicMock, call, mock_open
import sys
import os
import subprocess
import urllib.request
import time

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PerfectoLibrary.keywords._general import _GeneralKeywords


class TestGeneralKeywords(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.general_keywords = _GeneralKeywords()
        
        # Create mock objects
        self.mock_bi = Mock()
        self.mock_driver = Mock()
        self.mock_appium_lib = Mock()
        self.mock_selenium_lib = Mock()
        self.mock_selenium2_lib = Mock()
        self.mock_selenium2_ext_lib = Mock()
        
        # Set up driver capabilities
        self.mock_driver.capabilities = {
            'reportPdfUrl': 'http://example.com/report.pdf?executionId=123',
            'user': 'testuser',
            'password': 'testpass',
            'host': 'test.perfectomobile.com',
            'securityToken': 'test_token',
            'executionId': 'test_execution_123'
        }
        
        # Configure library mocks
        self.mock_appium_lib._current_application.return_value = self.mock_driver
        self.mock_selenium_lib.driver = self.mock_driver
        self.mock_selenium2_lib._current_browser.return_value = self.mock_driver
        self.mock_selenium2_ext_lib._current_browser.return_value = self.mock_driver
        
        # Patch BuiltIn
        self.general_keywords.bi = self.mock_bi

    def test_init(self):
        """Test initialization of GeneralKeywords."""
        gk = _GeneralKeywords()
        
        self.assertIsNone(gk.driver)
        self.assertEqual(gk.reportPdfUrl, '')

    def test_init_driver(self):
        """Test init_driver method."""
        with patch.object(self.general_keywords, '_check_driver') as mock_check:
            self.general_keywords.init_driver()
            mock_check.assert_called_once()

    def test_check_driver_appium_success(self):
        """Test successful driver check with AppiumLibrary."""
        self.mock_bi.get_library_instance.return_value = self.mock_appium_lib
        
        self.general_keywords._check_driver()
        
        self.assertEqual(self.general_keywords.driver, self.mock_driver)
        self.assertTrue(self.general_keywords.active)
        self.assertEqual(self.general_keywords.reportPdfUrl, 'http://example.com/report.pdf?executionId=123')

    def test_check_driver_selenium_success(self):
        """Test successful driver check with SeleniumLibrary."""
        def mock_get_lib(name):
            if name == 'AppiumLibrary':
                raise Exception("No AppiumLibrary")
            elif name == 'SeleniumLibrary':
                return self.mock_selenium_lib
        
        self.mock_bi.get_library_instance.side_effect = mock_get_lib
        
        self.general_keywords._check_driver()
        
        self.assertEqual(self.general_keywords.driver, self.mock_driver)
        self.assertTrue(self.general_keywords.active)

    def test_check_driver_selenium2_success(self):
        """Test successful driver check with Selenium2Library."""
        def mock_get_lib(name):
            if name in ['AppiumLibrary', 'SeleniumLibrary']:
                raise Exception("Library not found")
            elif name == 'Selenium2Library':
                return self.mock_selenium2_lib
        
        self.mock_bi.get_library_instance.side_effect = mock_get_lib
        
        self.general_keywords._check_driver()
        
        self.assertEqual(self.general_keywords.driver, self.mock_driver)
        self.assertTrue(self.general_keywords.active)

    def test_check_driver_selenium2_ext_success(self):
        """Test successful driver check with Selenium2LibraryExtension."""
        def mock_get_lib(name):
            if name in ['AppiumLibrary', 'SeleniumLibrary', 'Selenium2Library']:
                raise Exception("Library not found")
            elif name == 'Selenium2LibraryExtension':
                return self.mock_selenium2_ext_lib
        
        self.mock_bi.get_library_instance.side_effect = mock_get_lib
        
        self.general_keywords._check_driver()
        
        self.assertEqual(self.general_keywords.driver, self.mock_driver)
        self.assertTrue(self.general_keywords.active)

    def test_check_driver_all_fail(self):
        """Test driver check when all libraries fail."""
        self.mock_bi.get_library_instance.side_effect = Exception("No libraries found")
        
        self.general_keywords._check_driver()
        
        self.assertFalse(self.general_keywords.active)

    def test_check_driver_none_driver(self):
        """Test driver check with None driver."""
        self.mock_appium_lib._current_application.return_value = None
        self.mock_bi.get_library_instance.return_value = self.mock_appium_lib
        
        self.general_keywords._check_driver()
        
        self.assertIsNone(self.general_keywords.driver)

    @patch.dict(os.environ, {}, clear=True)
    def test_enable_proxy(self):
        """Test enabling proxy settings."""
        proxy_url = "http://proxy.example.com:8080"
        
        self.general_keywords.enable_proxy(proxy_url)
        
        self.assertEqual(os.environ['http_proxy'], proxy_url)
        self.assertEqual(os.environ['HTTP_PROXY'], proxy_url)
        self.assertEqual(os.environ['https_proxy'], proxy_url)
        self.assertEqual(os.environ['HTTPS_PROXY'], proxy_url)

    @patch.dict(os.environ, {
        'http_proxy': 'old_proxy',
        'HTTP_PROXY': 'old_proxy',
        'https_proxy': 'old_proxy',
        'HTTPS_PROXY': 'old_proxy'
    })
    def test_disable_proxy(self):
        """Test disabling proxy settings."""
        self.general_keywords.disable_proxy()
        
        # Check that proxy environment variables are not set
        self.assertNotIn('http_proxy', os.environ)
        self.assertNotIn('HTTP_PROXY', os.environ)
        self.assertNotIn('https_proxy', os.environ)
        self.assertNotIn('HTTPS_PROXY', os.environ)

    @patch.dict(os.environ, {}, clear=True)
    def test_disable_proxy_no_existing_vars(self):
        """Test disabling proxy when no environment variables exist."""
        # This should not raise an exception
        self.general_keywords.disable_proxy()
        
        # Environment should still be empty
        self.assertEqual(os.environ.get('http_proxy', ''), '')

    def test_driver_execute_script_success(self):
        """Test successful script execution."""
        self.general_keywords.driver = self.mock_driver
        self.general_keywords.active = True
        self.mock_driver.execute_script.return_value = "success_result"
        
        result = self.general_keywords.driver_execute_script(
            'mobile:button:click', 
            {'label': 'Submit'}
        )
        
        self.mock_driver.execute_script.assert_called_with(
            'mobile:button:click', 
            {'label': 'Submit'}
        )
        self.assertEqual(result, "success_result")

    def test_driver_execute_script_no_driver(self):
        """Test script execution when no driver is available."""
        with patch.object(self.general_keywords, '_check_driver', return_value=False):
            result = self.general_keywords.driver_execute_script(
                'mobile:button:click', 
                {'label': 'Submit'}
            )
            
            self.assertFalse(result)

    @patch('time.sleep')
    def test_keep_browser_session_alive_selenium(self, mock_sleep):
        """Test keeping browser session alive with SeleniumLibrary."""
        def mock_get_lib(name):
            if name == 'SeleniumLibrary':
                return self.mock_selenium_lib
            raise Exception("Library not found")
        
        self.mock_bi.get_library_instance.side_effect = mock_get_lib
        
        result = self.general_keywords.keep_browser_session_alive(120)
        
        self.assertTrue(result)
        # Should call execute_script 3 times (0, 60, 120 seconds)
        self.assertEqual(self.mock_driver.execute_script.call_count, 3)
        # Should sleep 2 times for 60 seconds each
        self.assertEqual(mock_sleep.call_count, 2)

    @patch('time.sleep')
    def test_keep_browser_session_alive_selenium2(self, mock_sleep):
        """Test keeping browser session alive with Selenium2Library."""
        def mock_get_lib(name):
            if name == 'SeleniumLibrary':
                raise Exception("SeleniumLibrary not found")
            elif name == 'Selenium2Library':
                return self.mock_selenium2_lib
            raise Exception("Library not found")
        
        self.mock_bi.get_library_instance.side_effect = mock_get_lib
        
        result = self.general_keywords.keep_browser_session_alive(60)
        
        self.assertTrue(result)
        self.assertEqual(self.mock_driver.execute_script.call_count, 2)

    @patch('time.sleep')
    def test_keep_browser_session_alive_selenium2_ext(self, mock_sleep):
        """Test keeping browser session alive with Selenium2LibraryExtension."""
        def mock_get_lib(name):
            if name in ['SeleniumLibrary', 'Selenium2Library']:
                raise Exception("Library not found")
            elif name == 'Selenium2LibraryExtension':
                return self.mock_selenium2_ext_lib
            raise Exception("Library not found")
        
        self.mock_bi.get_library_instance.side_effect = mock_get_lib
        
        result = self.general_keywords.keep_browser_session_alive(0)
        
        self.assertTrue(result)
        self.assertEqual(self.mock_driver.execute_script.call_count, 1)

    def test_keep_browser_session_alive_no_driver(self):
        """Test keeping browser session alive when no driver is available."""
        self.mock_bi.get_library_instance.side_effect = Exception("No libraries")
        
        result = self.general_keywords.keep_browser_session_alive(60)
        
        self.assertFalse(result)

    @patch('subprocess.Popen')
    def test_perfectoconnect_start_with_proxy(self, mock_popen):
        """Test starting PerfectoConnect with proxy settings."""
        mock_process = Mock()
        mock_process.communicate.return_value = (b'tunnel_id_123', b'')
        mock_popen.return_value = mock_process
        
        result = self.general_keywords.perfectoconnect_start(
            '/path/to/perfectoconnect.exe',
            'test.perfectomobile.com',
            'security_token',
            'proxy_user',
            'proxy_pass',
            '192.168.1.1',
            '8080'
        )
        
        expected_cmd = [
            '/path/to/perfectoconnect.exe',
            'start',
            '--cloudurl=test.perfectomobile.com',
            '--securitytoken=security_token',
            '--outgoingproxyuser=proxy_user',
            '--outgoingproxypass=proxy_pass',
            '--outgoingproxyip=192.168.1.1',
            '--outgoingproxyport=8080'
        ]
        mock_popen.assert_called_with(expected_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(result, 'tunnel_id_123')

    @patch('subprocess.Popen')
    def test_perfectoconnect_start_with_proxy_no_auth(self, mock_popen):
        """Test starting PerfectoConnect with proxy but no authentication."""
        mock_process = Mock()
        mock_process.communicate.return_value = (b'tunnel_id_456', b'')
        mock_popen.return_value = mock_process
        
        result = self.general_keywords.perfectoconnect_start(
            '/path/to/perfectoconnect.exe',
            'test.perfectomobile.com',
            'security_token',
            None,
            None,
            '192.168.1.1',
            '8080'
        )
        
        expected_cmd = [
            '/path/to/perfectoconnect.exe',
            'start',
            '--cloudurl=test.perfectomobile.com',
            '--securitytoken=security_token',
            '--outgoingproxyip=192.168.1.1',
            '--outgoingproxyport=8080'
        ]
        mock_popen.assert_called_with(expected_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(result, 'tunnel_id_456')

    @patch('subprocess.Popen')
    def test_perfectoconnect_start_no_proxy(self, mock_popen):
        """Test starting PerfectoConnect without proxy."""
        mock_process = Mock()
        mock_process.communicate.return_value = (b'tunnel_id_789', b'')
        mock_popen.return_value = mock_process
        
        result = self.general_keywords.perfectoconnect_start(
            '/path/to/perfectoconnect.exe',
            'test.perfectomobile.com',
            'security_token'
        )
        
        expected_cmd = [
            '/path/to/perfectoconnect.exe',
            'start',
            '--cloudurl=test.perfectomobile.com',
            '--securitytoken=security_token'
        ]
        mock_popen.assert_called_with(expected_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(result, 'tunnel_id_789')

    @patch('subprocess.Popen')
    def test_perfectoconnect_stop(self, mock_popen):
        """Test stopping PerfectoConnect."""
        mock_process = Mock()
        mock_process.communicate.return_value = (b'stopped', b'')
        mock_popen.return_value = mock_process
        
        self.general_keywords.perfectoconnect_stop('/path/to/perfectoconnect.exe')
        
        expected_cmd = ['/path/to/perfectoconnect.exe', 'stop']
        mock_popen.assert_called_with(expected_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_maximize_window_success(self):
        """Test successful window maximization."""
        self.general_keywords.driver = self.mock_driver
        
        with patch.object(self.general_keywords, '_check_driver', return_value=True):
            self.general_keywords.maximize_window()
            
            self.mock_driver.maximize_window.assert_called_once()

    def test_maximize_window_no_driver(self):
        """Test window maximization when no driver is available."""
        with patch.object(self.general_keywords, '_check_driver', return_value=False):
            self.general_keywords.maximize_window()
            
            self.mock_driver.maximize_window.assert_not_called()

    @patch('urllib.request.urlopen')
    @patch('time.sleep')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_summary_pdf_report_default(self, mock_file, mock_sleep, mock_urlopen):
        """Test downloading PDF report with default parameters."""
        self.general_keywords.reportPdfUrl = 'http://example.com/report.pdf?executionId=123'
        
        mock_response = Mock()
        mock_response.read.return_value = b'PDF content'
        mock_urlopen.return_value = mock_response
        
        result = self.general_keywords.download_summary_pdf_report(
            '/reports/', 
            'security_token'
        )
        
        self.assertTrue(result)
        mock_sleep.assert_called_with(10)
        mock_file.assert_called_once()

    @patch('urllib.request.urlopen')
    @patch('time.sleep')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_summary_pdf_report_with_params(self, mock_file, mock_sleep, mock_urlopen):
        """Test downloading PDF report with custom parameters."""
        self.general_keywords.reportPdfUrl = 'http://example.com/report.pdf?executionId=123'
        
        mock_response = Mock()
        mock_response.read.return_value = b'PDF content'
        mock_urlopen.return_value = mock_response
        
        result = self.general_keywords.download_summary_pdf_report(
            '/reports/', 
            'security_token',
            'exec_123',
            'TestJob',
            '1',
            'smoke'
        )
        
        self.assertTrue(result)
        mock_sleep.assert_called_with(10)

    @patch('urllib.request.urlopen')
    @patch('time.sleep')
    def test_download_summary_pdf_report_exception(self, mock_sleep, mock_urlopen):
        """Test downloading PDF report with exception."""
        self.general_keywords.reportPdfUrl = 'http://example.com/report.pdf?executionId=123'
        mock_urlopen.side_effect = Exception("Network error")
        
        with patch.object(self.general_keywords.bi, 'log_to_console') as mock_log:
            result = self.general_keywords.download_summary_pdf_report(
                '/reports/', 
                'security_token'
            )
            
            self.assertFalse(result)
            mock_log.assert_called()

    def test_download_summary_pdf_report_empty_url(self):
        """Test downloading PDF report with empty URL."""
        self.general_keywords.reportPdfUrl = ''
        
        with patch.object(self.general_keywords.bi, 'log_to_console') as mock_log:
            result = self.general_keywords.download_summary_pdf_report(
                '/reports/', 
                'security_token'
            )
            
            self.assertFalse(result)
            mock_log.assert_called_with("empty with ")

    @patch('axe_core_python.selenium.Axe')
    def test_accessibility_audit_current_page(self, mock_axe_class):
        """Test accessibility audit on current page."""
        # Set up mocks
        mock_axe = Mock()
        mock_axe_class.return_value = mock_axe
        mock_axe.run.return_value = {
            'violations': [
                {'description': 'Missing alt text'},
                {'description': 'Low color contrast'}
            ]
        }
        
        # Mock SeleniumLibrary
        mock_selenium_lib = Mock()
        mock_selenium_lib.driver = self.mock_driver
        self.general_keywords.bi.get_library_instance.return_value = mock_selenium_lib
        self.general_keywords.reporting_client = Mock()
        
        self.general_keywords.accessibility_audit_current_page()
        
        # Verify interactions
        self.mock_driver.maximize_window.assert_called_once()
        mock_axe.run.assert_called_once_with(self.mock_driver)
        
        # Verify violations are reported
        expected_calls = [
            call('Accessbility volation: '+str({'description': 'Missing alt text'}), False),
            call('Accessbility volation: '+str({'description': 'Low color contrast'}), False)
        ]
        self.general_keywords.reporting_client.reportium_assert.assert_has_calls(expected_calls)


if __name__ == '__main__':
    unittest.main()