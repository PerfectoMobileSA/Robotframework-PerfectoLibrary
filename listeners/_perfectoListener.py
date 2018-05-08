import os
import robot
import inspect
from perfecto import *
from SeleniumLibrary import SeleniumLibrary
from AppiumLibrary import AppiumLibrary
from robot.libraries.BuiltIn import BuiltIn
from selenium.webdriver.common.actions.interaction import NONE

class _PerfectoListener(object):
    ROBOT_LISTENER_API_VERSION = 2
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    
    def __init__(self):
        self.ROBOT_LIBRARY_LISTENER = self
        self.bi=BuiltIn()
        self.reporting_client = NONE
        self.active=False
    
    def _start_test(self, name, attrs):
        self.id=attrs['id']
        self.longname=attrs['longname']
        self.tags=attrs['tags']
        if not self.active:
            self._get_execontext()
        if self.active:
            self.execontext = PerfectoExecutionContext(self.driver, [','.join(attrs['tags'])], Job(attrs['longname'], 45), Project('Robotframework Test Project' + attrs['id'], '1.0'))
            self.reporting_client = PerfectoReportiumClient(self.execontext)
            self.reporting_client.test_start(name, TestContext(','.join(attrs['tags'])))
            
    def _start_keyword(self, name, attrs):
        if not self.active:
            self._get_execontext()
        if self.active and self.reporting_client==NONE:    
            self.execontext = PerfectoExecutionContext(self.driver, [','.join(self.tags)], Job(self.longname, 45), Project('Robotframework Test Project' + self.id, '1.0'))
            self.reporting_client = PerfectoReportiumClient(self.execontext)
            self.reporting_client.step_start(attrs['kwname'])
        elif self.active and attrs['kwname'].lower!="commtent":
            self.reporting_client.step_start(attrs['kwname'])
    def _get_execontext(self):
#         self.bi.log_to_console("_get_execontext")
        try:
            aplib = self.bi.get_library_instance('AppiumLibrary')
#             self.bi.log_to_console(aplib)
        except:
            aplib = self.bi.get_library_instance('SeleniumLibrary')
#             self.bi.log_to_console(aplib)
        try:
            if isinstance(aplib,SeleniumLibrary):
                self.driver = aplib.driver
            elif isinstance(aplib,AppiumLibrary):
                self.driver = aplib._current_application()
            self.active=1
        except Exception as e:
#             self.bi.log_to_console(e)
            self.active=False 
            
    def _stop_suite(self):
        if self.active:
            try:
                self.reporting_client.test_stop(TestResultFactory.create_success())
            except Exception as e:
                self.reporting_client.test_stop(TestResultFactory.create_failure(str(e)))
    
    def _stop_test(self, name, attrs):
        if self.active:
            self.reporting_client.step_end()