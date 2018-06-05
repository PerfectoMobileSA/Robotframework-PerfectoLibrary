import os
import robot
import inspect
import pdb
import sys
from perfecto import *
from SeleniumLibrary import SeleniumLibrary
from Selenium2Library import Selenium2Library
from AppiumLibrary import AppiumLibrary
from Selenium2LibraryExtension import Selenium2LibraryExtension
from robot.libraries.BuiltIn import BuiltIn

class _PerfectoListener(object):
    ROBOT_LISTENER_API_VERSION = 2
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    driver=''

    def __init__(self):
        # pdb.Pdb(stdout=sys.__stdout__).set_trace()
        self.ROBOT_LIBRARY_LISTENER = self
        self.bi=BuiltIn()
        self.reporting_client = None
        self.active=False
        self.stop_reporting = False
        self.tags=''
        self.longname='Robotframework Script'
        self.id='1'
        self.status='pass'
        self.message=''
        self.running=False

    def _start_test(self, name, attrs):
#         pdb.Pdb(stdout=sys.__stdout__).set_trace()
        self.id=attrs['id']
        self.longname=attrs['longname']
        self.tags=attrs['tags']
        if not self.active:
            self._get_execontext()
        if self.active and self.reporting_client!=None and self.running == False:
            self.execontext = PerfectoExecutionContext(self.driver, self.tags, Job(self.longname, '1'),
                                                       Project('Robotframework Test Project ' + self.id, '1.0'))
            self.reporting_client = PerfectoReportiumClient(self.execontext)
            self.reporting_client.test_start(self.longname, TestContext(*self.tags))
            self.running = True

    def _start_keyword(self, name, attrs):
        try:
            if not self.active:
                self._get_execontext()
            if self.active and self.reporting_client==None and self.stop_reporting!=True \
                    and "keyword" in attrs['type'].lower()\
                    and self.running == False:
                self.execontext = PerfectoExecutionContext(self.driver, self.tags, Job(self.longname, '1'), Project('Robotframework Test Project ' + self.id, '1.0'))
                self.reporting_client = PerfectoReportiumClient(self.execontext)
                self.reporting_client.test_start(self.longname, TestContext(*self.tags))
                self.running = True

            if self.active and "comment" not in attrs['kwname'].lower() and self.reporting_client!=None \
                    and "keyword" in attrs['type'].lower():
                self.reporting_client.step_start(attrs['kwname']+ ' '+' '.join(attrs['args']))
                self.status = 'pass'
                self.message = ''
            elif self.active and "comment" not in attrs['kwname'].lower() and self.reporting_client!=None and self.stop_reporting!=True\
                    and "tear" in attrs['type'].lower():
                if self.status == 'pass':
                    self.reporting_client.test_stop(TestResultFactory.create_success())
                else:
                    self.reporting_client.test_stop(TestResultFactory.create_failure(self.message))
                self.stop_reporting = True

        except Exception as e:
            try:
                self._get_execontext()
                self.execontext = PerfectoExecutionContext(self.driver, [','.join(self.tags)], Job(self.longname, '1'),
                                                           Project('Robotframework Test Project ' + self.id, '1.0'))
                self.reporting_client = PerfectoReportiumClient(self.execontext)
            except:
                pass

    def _end_keyword(self, name, attrs):
        try:
            if self.active and "comment" not in attrs['kwname'].lower() and self.reporting_client!=None and self.stop_reporting!=True\
                    and "keyword" in attrs['type'].lower():
                self.reporting_client.step_end(attrs['kwname'] + ' ' + ' '.join(attrs['args']))
                # if 'ignore error' in attrs['kwname'].lower():
                #     self.ignoreError=True

        except Exception as e:
            self.bi.log_to_console(e)

    def _log_message(self,message):
        if message.get('level')=='FAIL':
            self.status = 'fail'
            self.message=message.get('message')
        # elif message.get('level')=='FAIL' and self.ignoreError==True:
        #     self.ignoreError = False


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

    def _end_test(self, name, attrs):
        try:
            if attrs['status']=="PASS":
                self.reporting_client.test_stop(TestResultFactory.create_success())
            else:
                self.reporting_client.test_stop(TestResultFactory.create_failure(attrs['message']))
        except Exception as e:
            self.bi.log_to_console(e)
        self.stop_reporting = False
        self.reporting_client = None
        self.active = False
        self.running = False