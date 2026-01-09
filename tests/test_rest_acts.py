import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os
import urllib.request
import urllib.error
from urllib.parse import quote_plus

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PerfectoLibrary.keywords._rest_acts import _RestKeywords


class TestRestKeywords(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.rest_keywords = _RestKeywords()
        
        # Create mock objects
        self.mock_bi = Mock()
        self.mock_driver = Mock()
        self.mock_appium_lib = Mock()
        
        # Set up driver capabilities
        self.mock_driver.capabilities = {
            'devicename': 'test_device_123',
            'executionId': 'exec_456',
            'user': 'driver_user',
            'password': 'driver_pass',
            'host': 'driver.perfectomobile.com',
            'securityToken': 'driver_token_789'
        }
        
        # Configure mocks
        self.mock_appium_lib._current_application.return_value = self.mock_driver
        self.mock_bi.get_library_instance.return_value = self.mock_appium_lib
        
        # Patch BuiltIn
        self.rest_keywords.bi = self.mock_bi

    def test_init(self):
        """Test initialization of RestKeywords."""
        rk = _RestKeywords()
        
        self.assertIsNone(rk.securityToken)
        self.assertIsNone(rk.user)
        self.assertIsNone(rk.password)
        self.assertIsNone(rk.host)

    @patch('urllib.request.urlopen')
    def test_perform_rest_request_success(self, mock_urlopen):
        """Test successful REST request."""
        mock_response = Mock()
        mock_response.read.return_value = b'{"status": "success"}'
        mock_urlopen.return_value = mock_response
        
        result = self.rest_keywords._perform_rest_request('http://example.com/api')
        
        self.assertEqual(result, b'{"status": "success"}')
        mock_urlopen.assert_called_once_with('http://example.com/api')

    @patch('urllib.request.urlopen')
    def test_perform_rest_request_exception(self, mock_urlopen):
        """Test REST request with exception."""
        mock_urlopen.side_effect = urllib.error.URLError('Connection failed')
        
        with self.assertRaises(urllib.error.URLError):
            self.rest_keywords._perform_rest_request('http://example.com/api')

    def test_check_driver_success(self):
        """Test successful driver check."""
        # Set up the _check_driver functionality implicitly tested through _exeRestCmd
        self.rest_keywords.driver = self.mock_driver
        
        # This would be called indirectly through other methods
        # We'll test it through _exeRestCmd since _check_driver is used there

    @patch.object(_RestKeywords, '_exe_restops')
    @patch.object(_RestKeywords, '_check_driver', return_value=True)
    def test_exeRestCmd_with_driver(self, mock_check_driver, mock_exe_restops):
        """Test _exeRestCmd with available driver."""
        self.rest_keywords.driver = self.mock_driver
        mock_exe_restops.return_value = 'success'
        
        params = {'profile': 'test_profile'}
        result = self.rest_keywords._exeRestCmd('vnetwork', 'start', params)
        
        expected_actions = {
            'command': 'vnetwork',
            'subcommand': 'start'
        }
        expected_params = {
            'profile': 'test_profile',
            'deviceId': 'test_device_123'
        }
        
        mock_exe_restops.assert_called_once_with(
            'command',
            'executions/exec_456',
            expected_actions,
            expected_params
        )
        self.assertEqual(result, 'success')

    @patch.object(_RestKeywords, '_exe_restops')
    @patch.object(_RestKeywords, '_check_driver', return_value=True)
    def test_exeRestCmd_with_existing_deviceId(self, mock_check_driver, mock_exe_restops):
        """Test _exeRestCmd when deviceId is already in params."""
        self.rest_keywords.driver = self.mock_driver
        mock_exe_restops.return_value = 'success'
        
        params = {'profile': 'test_profile', 'deviceId': 'custom_device'}
        result = self.rest_keywords._exeRestCmd('vnetwork', 'start', params)
        
        # Should not override existing deviceId
        expected_params = {
            'profile': 'test_profile',
            'deviceId': 'custom_device'  # Should remain unchanged
        }
        
        mock_exe_restops.assert_called_once()
        call_args = mock_exe_restops.call_args[0]
        self.assertEqual(call_args[3]['deviceId'], 'custom_device')

    @patch.object(_RestKeywords, '_check_driver', return_value=False)
    def test_exeRestCmd_no_driver(self, mock_check_driver):
        """Test _exeRestCmd when no driver is available."""
        result = self.rest_keywords._exeRestCmd('vnetwork', 'start', {})
        
        self.assertIsNone(result)

    def test_set_credentials(self):
        """Test setting user credentials."""
        self.rest_keywords.set_credentials('test_user', 'test_password')
        
        self.assertEqual(self.rest_keywords.user, 'test_user')
        self.assertEqual(self.rest_keywords.password, 'test_password')

    def test_set_securityToken(self):
        """Test setting security token."""
        self.rest_keywords.set_securityToken('test_token_123')
        
        self.assertEqual(self.rest_keywords.securityToken, 'test_token_123')

    def test_set_host(self):
        """Test setting host."""
        self.rest_keywords.set_host('test.perfectomobile.com')
        
        self.assertEqual(self.rest_keywords.host, 'test.perfectomobile.com')

    @patch.object(_RestKeywords, '_exe_restops')
    def test_retrieve_Device_Info(self, mock_exe_restops):
        """Test retrieving device information."""
        mock_exe_restops.return_value = '{"model": "iPhone 12"}'
        
        self.rest_keywords.retrieve_Device_Info('device123')
        
        mock_exe_restops.assert_called_once_with(
            'info',
            'handsets/device123',
            {},
            {}
        )
        self.mock_bi.log_to_console.assert_called_with('{"model": "iPhone 12"}')

    @patch.object(_RestKeywords, '_exeRestCmd')
    def test_start_network_virtualization(self, mock_exe_rest):
        """Test starting network virtualization."""
        mock_exe_rest.return_value = 'started'
        
        self.rest_keywords.start_network_virtualization('device123', 'profile_4g')
        
        expected_params = {
            'deviceId': 'device123',
            'profile': 'profile_4g'
        }
        mock_exe_rest.assert_called_once_with('vnetwork', 'start', expected_params)
        self.mock_bi.log_to_console.assert_called_with('started')

    @patch.object(_RestKeywords, '_exeRestCmd')
    def test_update_network_virtualization(self, mock_exe_rest):
        """Test updating network virtualization."""
        mock_exe_rest.return_value = 'updated'
        
        self.rest_keywords.update_network_virtualization('device123', 'profile_3g')
        
        expected_params = {
            'deviceId': 'device123',
            'profile': 'profile_3g'
        }
        mock_exe_rest.assert_called_once_with('vnetwork', 'update', expected_params)
        self.mock_bi.log_to_console.assert_called_with('updated')

    @patch.object(_RestKeywords, '_exeRestCmd')
    def test_stop_network_virtualization(self, mock_exe_rest):
        """Test stopping network virtualization."""
        mock_exe_rest.return_value = 'stopped'
        
        self.rest_keywords.stop_network_virtualization('device123')
        
        expected_params = {
            'deviceId': 'device123'
        }
        mock_exe_rest.assert_called_once_with('vnetwork', 'stop', expected_params)
        self.mock_bi.log_to_console.assert_called_with('stopped')

    @patch.object(_RestKeywords, '_perform_rest_request')
    @patch.object(_RestKeywords, '_check_driver', return_value=True)
    def test_exe_restops_with_driver_credentials(self, mock_check_driver, mock_perform_request):
        """Test _exe_restops using driver credentials."""
        self.rest_keywords.driver = self.mock_driver
        mock_perform_request.return_value = b'success'
        
        actions = {'command': 'test_command'}
        params = {'param1': 'value1', 'param2': 'value with spaces'}
        
        result = self.rest_keywords._exe_restops('test', 'test_service', actions, params)
        
        # Verify URL construction with driver credentials
        expected_url = (
            'https://driver.perfectomobile.com/services/test_service?operation=test'
            '&securityToken=driver_token_789'
            '&command=test_command'
            '&param.param1=value1'
            '&param.param2=value%20with%20spaces'
        )
        mock_perform_request.assert_called_once_with(expected_url)
        self.assertEqual(result, b'success')

    @patch.object(_RestKeywords, '_perform_rest_request')
    @patch.object(_RestKeywords, '_check_driver', return_value=True)
    def test_exe_restops_with_user_password(self, mock_check_driver, mock_perform_request):
        """Test _exe_restops using user/password when no security token."""
        # Set up driver without security token
        self.rest_keywords.driver = self.mock_driver
        self.mock_driver.capabilities['securityToken'] = None
        mock_perform_request.return_value = b'success'
        
        actions = {'command': 'test_command'}
        params = {'param1': 'value1'}
        
        result = self.rest_keywords._exe_restops('test', 'test_service', actions, params)
        
        # Should use user/password authentication
        expected_url = (
            'https://driver.perfectomobile.com/services/test_service?operation=test'
            '&user=driver_user&password=driver_pass'
            '&command=test_command'
            '&param.param1=value1'
        )
        mock_perform_request.assert_called_once_with(expected_url)

    @patch.object(_RestKeywords, '_perform_rest_request')
    @patch.object(_RestKeywords, '_check_driver', return_value=True)
    def test_exe_restops_with_empty_security_token(self, mock_check_driver, mock_perform_request):
        """Test _exe_restops when security token is empty string."""
        # Set up driver with empty security token
        self.rest_keywords.driver = self.mock_driver
        self.mock_driver.capabilities['securityToken'] = ''
        mock_perform_request.return_value = b'success'
        
        actions = {}
        params = {}
        
        result = self.rest_keywords._exe_restops('test', 'test_service', actions, params)
        
        # Should fallback to user/password authentication
        expected_url = (
            'https://driver.perfectomobile.com/services/test_service?operation=test'
            '&user=driver_user&password=driver_pass'
        )
        mock_perform_request.assert_called_once_with(expected_url)

    @patch.object(_RestKeywords, '_perform_rest_request')
    @patch.object(_RestKeywords, '_check_driver', return_value=True)
    def test_exe_restops_override_with_instance_variables(self, mock_check_driver, mock_perform_request):
        """Test _exe_restops with instance variables overriding driver capabilities."""
        self.rest_keywords.driver = self.mock_driver
        self.rest_keywords.user = 'override_user'
        self.rest_keywords.password = 'override_pass'
        self.rest_keywords.host = 'override.perfectomobile.com'
        self.rest_keywords.securityToken = 'override_token'
        mock_perform_request.return_value = b'success'
        
        result = self.rest_keywords._exe_restops('test', 'test_service', {}, {})
        
        # Should use instance variables instead of driver capabilities
        expected_url = (
            'https://override.perfectomobile.com/services/test_service?operation=test'
            '&securityToken=override_token'
        )
        mock_perform_request.assert_called_once_with(expected_url)

    @patch.object(_RestKeywords, '_perform_rest_request')
    @patch.object(_RestKeywords, '_check_driver', return_value=False)
    def test_exe_restops_no_driver_with_instance_vars(self, mock_check_driver, mock_perform_request):
        """Test _exe_restops without driver but with instance variables."""
        self.rest_keywords.user = 'instance_user'
        self.rest_keywords.password = 'instance_pass'
        self.rest_keywords.host = 'instance.perfectomobile.com'
        self.rest_keywords.securityToken = 'instance_token'
        mock_perform_request.return_value = b'success'
        
        result = self.rest_keywords._exe_restops('test', 'test_service', {}, {})
        
        expected_url = (
            'https://instance.perfectomobile.com/services/test_service?operation=test'
            '&securityToken=instance_token'
        )
        mock_perform_request.assert_called_once_with(expected_url)

    @patch.object(_RestKeywords, '_perform_rest_request')
    def test_exe_restops_complex_params(self, mock_perform_request):
        """Test _exe_restops with complex parameters requiring URL encoding."""
        self.rest_keywords.host = 'test.perfectomobile.com'
        self.rest_keywords.securityToken = 'test_token'
        mock_perform_request.return_value = b'success'
        
        actions = {
            'command': 'test_command',
            'subcommand': 'test_sub'
        }
        params = {
            'special_chars': 'hello world & test=value',
            'unicode': 'café',
            'numbers': '123'
        }
        
        result = self.rest_keywords._exe_restops('operation', 'service', actions, params)
        
        # Verify URL contains properly encoded parameters
        call_args = mock_perform_request.call_args[0][0]
        self.assertIn('param.special_chars=hello%20world%20%26%20test%3Dvalue', call_args)
        self.assertIn('param.unicode=caf%C3%A9', call_args)
        self.assertIn('param.numbers=123', call_args)
        self.assertIn('command=test_command', call_args)
        self.assertIn('subcommand=test_sub', call_args)

    @patch.object(_RestKeywords, '_perform_rest_request')
    def test_exe_restops_url_construction(self, mock_perform_request):
        """Test complete URL construction in _exe_restops."""
        self.rest_keywords.host = 'test.perfectomobile.com'
        self.rest_keywords.securityToken = 'test_token'
        mock_perform_request.return_value = b'response'
        
        actions = {'action1': 'value1', 'action2': 'value2'}
        params = {'param1': 'value1', 'param2': 'value2'}
        
        self.rest_keywords._exe_restops('myop', 'myservice', actions, params)
        
        call_args = mock_perform_request.call_args[0][0]
        
        # Verify all parts of URL
        self.assertTrue(call_args.startswith('https://test.perfectomobile.com/services/myservice'))
        self.assertIn('operation=myop', call_args)
        self.assertIn('securityToken=test_token', call_args)
        self.assertIn('action1=value1', call_args)
        self.assertIn('action2=value2', call_args)
        self.assertIn('param.param1=value1', call_args)
        self.assertIn('param.param2=value2', call_args)

        # Verify URL logging
        self.mock_bi.log_to_console.assert_called_with('url=' + call_args)


if __name__ == '__main__':
    unittest.main()