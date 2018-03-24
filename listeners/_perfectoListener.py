import os
import robot
import inspect
from perfecto import *
from robot.libraries.BuiltIn import BuiltIn
from .keywordgroup import KeywordGroup

class _PerfectoListener(KeywordGroup):
    ROBOT_LISTENER_API_VERSION = 2
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self):
        self.ROBOT_LIBRARY_LISTENER = self
        self.bi=BuiltIn()
    
    def _start_suite(self, name, attrs):
        aplib = self.bi.get_library_instance('AppiumLibrary')
        self.driver = aplib._current_application()
        self.execontext = PerfectoExecutionContext(self.driver, [attrs['tags']], Job(attrs['longname'], 45), Project('Robotframework Test Project' + attrs['id'], '1.0'))
        self.reporting_client = PerfectoReportiumClient(self.execontext)
        self.reporting_client.test_start(testName, TestContext(attrs['tags']))
                
    def _start_test(self, name, attrs):
        self.reporting_client.step_start(attrs['longname'])
        
    def _stop_suite(self):
        """.
        """
        try:
            self.reporting_client.test_stop(TestResultFactory.create_success())
        except Exception as e:
            self.reporting_client.test_stop(TestResultFactory.create_failure(str(e)))
    
    def _stop_test(self, name, attrs):
        self.reporting_client.step_end()