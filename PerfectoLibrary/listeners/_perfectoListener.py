import os
import robot
import inspect
import pdb
import sys
import PerfectoLibrary
from perfecto import *
# from SeleniumLibrary import SeleniumLibrary
# from Selenium2Library import Selenium2Library
# from AppiumLibrary import AppiumLibrary
# from Selenium2LibraryExtension import Selenium2LibraryExtension
from robot.libraries.BuiltIn import BuiltIn

class _PerfectoListener(object):
    ROBOT_LISTENER_API_VERSION = 2
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    driver=''
    projectname = 'Robotframework Test Project'
    projectversion = '1.0'
    jobname = 'Robotframework Test Job'
    jobnumber = '1'


    def __init__(self):
        # pdb.Pdb(stdout=sys.__stdout__).set_trace()
        self.ROBOT_LIBRARY_LISTENER = self
        self.bi=BuiltIn()
        self.reporting_client = None
        self.active=False
        self.stop_reporting = False
        self.tags=''
        self.longname='Robotframework Script'
        self.id='s1-t1'
        self.running=False

    def init_listener(self,projectname=None,projectversion=None,jobname=None,jobnumber=None):
        """
        This key word helps to initialize the listener with proper project info
        :param projectname: current project name
        :param projectversion: current project version
        :param jobname: the CI job name
        :param jobnumber: the CI job number
        :return:
        """
        if projectname !=None:
            self.projectname = projectname
        if projectversion !=None:
            self.projectversion = projectversion
        if jobname !=None:
            self.jobname = jobname
        if jobnumber !=None:
            self.jobnumber = jobnumber


    def _start_suite(self, name, attrs):
#         pdb.Pdb(stdout=sys.__stdout__).set_trace()
        if not self.active:
            self._get_execontext()

    def _start_test(self, name, attrs):
        # pdb.Pdb(stdout=sys.__stdout__).set_trace()
        self.id=attrs['id']
        self.longname=self.bi.get_variable_value('${TEST NAME}')
        self.tags=attrs['tags']
        if not self.active:
            self._get_execontext()
        if self.active and self.reporting_client!=None and self.running == False:
            self.reporting_client.test_start(self.longname, TestContext(*self.tags))
            self.running = True

    def _start_keyword(self, name, attrs):
        try:
            if not self.active:
                self._get_execontext()
            if self.active and self.reporting_client!=None and self.stop_reporting!=True \
                    and self.running == False:
                self.reporting_client.test_start(self.bi.get_variable_value('${TEST NAME}'), TestContext(*self.tags))
                self.running = True

            if self.active and self.reporting_client!=None \
                    and "comment" not in attrs['kwname'].lower() \
                    and "excel" not in attrs['kwname'].lower() \
                    and "sheet" not in attrs['kwname'].lower() \
                    and "cell" not in attrs['kwname'].lower() \
                    and "column" not in attrs['kwname'].lower() \
                    and "keyword" in attrs['type'].lower() \
                    and "builtin" not in attrs['libname'].lower() \
                    and "excellibrary" not in attrs['libname'].lower() \
                    and "selenium" not in attrs['libname'].lower() \
                    and "appium" not in attrs['libname'].lower():
                self.reporting_client.step_start(attrs['kwname']+ ' '+' '.join(attrs['args']))
                # pass
            if self.active and "comment" not in attrs['kwname'].lower() and self.reporting_client!=None and self.stop_reporting!=True\
                    and "tear" in attrs['type'].lower():
                if self.bi.get_variable_value('${TEST STATUS}')=='FAIL':
                    self.reporting_client.test_stop(
                        TestResultFactory.create_failure(self.bi.get_variable_value('${TEST MESSAGE}')))
                else:
                    self.reporting_client.test_stop(TestResultFactory.create_success())
                self.stop_reporting = True

        except Exception as e:
            pass
            # try:
            #     self._get_execontext()
            #     self.execontext = PerfectoExecutionContext(self.driver, self.tags, Job('Robotframework Test Job', '1'),
            #                                                Project('Robotframework Test Project ' + self.id, '1.0'))
            #     self.reporting_client = PerfectoReportiumClient(self.execontext)
            # except:
            #     pass


    def _get_execontext(self):
        # self.bi.log_to_console("_get_execontext")
        try:
            aplib = self.bi.get_library_instance('AppiumLibrary')
            self.driver = aplib._current_application()
            # self.bi.log_to_console(aplib)
            self.active = True
        except:
            try:
                aplib = self.bi.get_library_instance('SeleniumLibrary')
                self.driver = aplib.driver
                # self.bi.log_to_console(aplib)
                self.active = True
            except:
                try:
                    aplib = self.bi.get_library_instance('Selenium2Library')
                    self.driver = self.driver = aplib._current_browser()
                    self.active = True
                except:
                    try:
                        aplib = self.bi.get_library_instance('Selenium2LibraryExtension')
                        self.driver = self.driver = aplib._current_browser()
                        self.active = True
                    except:
                        self.active = False

        if self.active:
            self.execontext = PerfectoExecutionContext(self.driver, self.tags, Job(self.jobname, self.jobnumber),
                                                       Project(self.projectname, self.projectversion))
            self.reporting_client = PerfectoReportiumClient(self.execontext)

    def _end_test(self, name, attrs):
        if self.stop_reporting != True:
            try:
                if attrs['status']=="PASS":
                    self.reporting_client.test_stop(TestResultFactory.create_success())
                else:
                    self.reporting_client.test_stop(TestResultFactory.create_failure(attrs['message']))
            except Exception as e:
                # self.bi.log_to_console(e)
                pass
        self.stop_reporting = False
        self.reporting_client = None
        self.active = False
        self.running = False