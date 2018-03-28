import os
import robot
import inspect
from perfecto import *
from robot.libraries.BuiltIn import BuiltIn

class _PerfectoListener(object):
    ROBOT_LISTENER_API_VERSION = 2
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
	
    def __init__(self):
		self.ROBOT_LIBRARY_LISTENER = self
		self.bi=BuiltIn()
		self.active=1
    
    def _start_test(self, name, attrs):
		aplib = self.bi.get_library_instance('AppiumLibrary')
		try:
			self.driver = aplib._current_application()
			self.active=1
		except Exception as e:
			self.active=False
		if self.active:	
			self.execontext = PerfectoExecutionContext(self.driver, [','.join(attrs['tags'])], Job(attrs['longname'], 45), Project('Robotframework Test Project' + attrs['id'], '1.0'))
			self.reporting_client = PerfectoReportiumClient(self.execontext)
			self.reporting_client.test_start(name, TestContext(','.join(attrs['tags'])))
			self.reporting_client.step_start(attrs['longname'])
        
    def _stop_suite(self):
		if self.active:
			try:
				self.reporting_client.test_stop(TestResultFactory.create_success())
			except Exception as e:
				self.reporting_client.test_stop(TestResultFactory.create_failure(str(e)))
    
    def _stop_test(self, name, attrs):
		if self.active:
			self.reporting_client.step_end()