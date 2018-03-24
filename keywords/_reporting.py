import perfecto
import os
import robot
import inspect
from perfecto import *
from robot.libraries.BuiltIn import BuiltIn
from .keywordgroup import KeywordGroup

class _ReportingKeywords(KeywordGroup):
    def __init__(self):
		self.bi = BuiltIn()
    def init_report(self):
		aplib = self.bi.get_library_instance('AppiumLibrary')
		self.driver = aplib._current_application()
		self.execontext = PerfectoExecutionContext(self.driver, ['RobotTestTag'], Job('Robot Test Job', 45), Project('Robotframework Test Project', '1.0'))
		self.reporting_client = PerfectoReportiumClient(self.execontext)
		
    def test_start(self, testName,testTag):
        """
        """
        self.reporting_client.test_start(testName, TestContext(testTag))
    def test_stop(self):
        """.
        """
        try:
            self.reporting_client.test_stop(TestResultFactory.create_success())
        except Exception as e:
            self.reporting_client.test_stop(TestResultFactory.create_failure(str(e)))
    def test_step(self, testStepName):
		self.reporting_client.step_end()
		self.reporting_client.step_start(testStepName)