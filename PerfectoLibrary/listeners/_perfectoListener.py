import os
import robot
import json
import inspect
import pdb
import sys
import PerfectoLibrary
from perfecto import *
import traceback
# from SeleniumLibrary import SeleniumLibrary
# from Selenium2Library import Selenium2Library
# from AppiumLibrary import AppiumLibrary
# from Selenium2LibraryExtension import Selenium2LibraryExtension
from robot.libraries.BuiltIn import BuiltIn


class _PerfectoListener(object):
    ROBOT_LISTENER_API_VERSION = 2
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    driver = ''
    projectname = 'Robotframework Test Project'
    projectversion = '1.0'
    jobname = 'Robotframework Test Job'
    jobnumber = 1

    def __init__(self):
        # pdb.Pdb(stdout=sys.__stdout__).set_trace()
        self.ROBOT_LIBRARY_LISTENER = self
        self.bi = BuiltIn()
        self.reporting_client = None
        self.active = False
        self.stop_reporting = False
        self.tags = ''
        self.longname = 'Robotframework Script'
        self.id = 's1-t1'
        self.running = False
        self.suitesetup = False
        self.setupclient = None
        self.lib_path = os.path.join(os.path.dirname(__file__), 'data')
        self.failure_config_orig = 'failure_reasons.json'
        self.excluded_reporting_keywords_orig = 'excluded_reporting_keywords.json'
        self.excluded_reporting_keyword_dict = {}
        self.failure_config_json_list = []
        self.failure_config = ''
        self.excluded_reporting_keywords = ''

    def init_listener(self, projectname=None, projectversion=None, jobname=None, jobnumber=None,failure_config='',excluded_reporting_keywords=''):
        """
        This key word helps to initialize the listener with proper project info
        :param projectname: current project name
        :param projectversion: current project version
        :param jobname: the CI job name
        :param jobnumber: the CI job number
        :param failure_config: the CI job number
        :param excluded_reporting_keywords: the CI job number
        :return:
        """
        if projectname is not None:
            self.projectname = projectname
        if projectversion is not None:
            self.projectversion = projectversion
        if jobname != None:
            self.jobname = jobname
        if jobnumber is not None:
            self.jobnumber = int(float(jobnumber))
        if failure_config != '':
            self.failure_config = failure_config
        if excluded_reporting_keywords != '':
            self.excluded_reporting_keywords = excluded_reporting_keywords

    def _start_suite(self, name, attrs):
        #         pdb.Pdb(stdout=sys.__stdout__).set_trace()

        #if not self.active:
        self._get_execontext(False)

    def _start_test(self, name, attrs):
        # pdb.Pdb(stdout=sys.__stdout__).set_trace()
        self.id = attrs['id']
        self.longname = self.bi.get_variable_value('${TEST NAME}')
        self.tags = attrs['tags']
        #         if not self.active:
        self._get_execontext(False)
        if self.active and self.reporting_client is not None and self.running is False:
            self._suitesetup_result()
            self.reporting_client.test_start(self.longname, TestContext([], self.tags))
            self.running = True

    def _suitesetup_result(self):
        if self.suitesetup:
            if self.bi.get_variable_value('${TEST STATUS}') == 'FAIL':
                self.setupclient.test_stop(
                    TestResultFactory.create_failure(self.bi.get_variable_value('${TEST MESSAGE}')))
            else:
                self.setupclient.test_stop(TestResultFactory.create_success())
            self.suitesetup = False

    def _start_keyword(self, name, attrs):
        try:
            # if not self.active:
            self._get_execontext(False)

            if self.active and self.reporting_client is not None and self.stop_reporting is not True \
                    and self.running == False and "tear" not in attrs['type'].lower():
                if self.bi.get_variable_value('${TEST NAME}') != None:
                    self._suitesetup_result()
                    self.reporting_client.test_start(self.bi.get_variable_value('${TEST NAME}'),
                                                     TestContext([], self.tags))

                else:
                    self.reporting_client.test_start('Suite Setup', TestContext([], self.tags))
                    self.setupclient = self.reporting_client
                    self.suitesetup = True
                self.running = True

            # pass
            if self.active and self.reporting_client is not None and self.stop_reporting is not True \
                    and "tear" in attrs['type'].lower():
                self._get_execontext(True)
                if self.bi.get_variable_value('${TEST STATUS}') == 'FAIL':
                    failure_reason_customer_error = self._match_failure_reasons(self.bi.get_variable_value('${TEST MESSAGE}'))
                    self.reporting_client.test_stop(
                        TestResultFactory.create_failure(self.bi.get_variable_value('${TEST MESSAGE}'), None, failure_reason_customer_error))
                else:
                    self.reporting_client.test_stop(TestResultFactory.create_success())
                self.stop_reporting = True
                self.running = False
            if not self.excluded_reporting_keyword_dict:
                self._parse_execluded_reporting_keywords_json_file()

            if self.active and self.reporting_client is not None and self.stop_reporting is not True \
                    and attrs['kwname'].lower() not in self.excluded_reporting_keyword_dict['kwname'] \
                    and attrs['libname'].lower() not in self.excluded_reporting_keyword_dict['libname'] \
                    and attrs['type'].lower() in self.excluded_reporting_keyword_dict['type']:
                self.reporting_client.step_start(attrs['kwname'] + ' ' + ' '.join(attrs['args']))


        except Exception as e:
            self.bi.log_to_console(traceback.format_exc())
            pass

    #     def _end_keyword(self, name, attrs):
    #         if "setup" in attrs['type'].lower() \
    #             and ("selenium" in attrs['libname'].lower() \
    #             or "appium"  in attrs['libname'].lower()):
    #                 self._get_execontext()

    def _get_execontext(self,enable_multi):
        # self.bi.log_to_console("_get_execontext")
        if self.active:
            refresh_context = False
            try:
                aplib = self.bi.get_library_instance('AppiumLibrary')
                current_driver = aplib._current_application()
                if isinstance(self.driver, list):
                    if current_driver not in self.driver:
                        self.driver.append(current_driver)
                        refresh_context = True
                elif self.driver != current_driver:
                    self.driver = [self.driver, current_driver]
                    refresh_context = True
                if refresh_context:
                    self.execontext = PerfectoExecutionContext(self.driver, self.tags,
                                                               Job(self.jobname, self.jobnumber),
                                                               Project(self.projectname, self.projectversion))
                    # self.reporting_client = PerfectoReportiumClient(self.execontext)
            except:
                pass

        else:
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

        if enable_multi:
            try:
                if isinstance(self.execontext.webdriver, list) and len(self.execontext.webdriver)>1:
                    self.reporting_client = PerfectoReportiumClient(self.execontext)
            except:
                pass


    def _end_test(self, name, attrs):
        failure_reason_customer_error = ""
        self._get_execontext(True)
        if not self.stop_reporting:
            try:
                if attrs['status'] == "PASS":
                    self.reporting_client.test_stop(TestResultFactory.create_success())
                else:
                    failure_reason_customer_error = self._match_failure_reasons(attrs['message'])
                    self.reporting_client.test_stop(TestResultFactory.create_failure(attrs['message'], None,
                                                                                     failure_reason_customer_error))
            except Exception as e:
                if self.reporting_client:
                    failure_reason_customer_error = self._match_failure_reasons(e)
                    self.reporting_client.test_stop(TestResultFactory.create_failure(attrs['message'], e,
                                                                                 failure_reason_customer_error))
                # pass
        self.stop_reporting = False
        self.reporting_client = None
        self.active = False
        self.running = False

    def _parse_failure_json_file(self):
        try:
            with open(self.lib_path + '/' + self.failure_config_orig, 'r') as failure_config_json_file:
                failure_config_json_list_orig = json.load(failure_config_json_file)
                self.failure_config_json_list = failure_config_json_list_orig

            if self.failure_config != '' and self.failure_config is not None:

                with open(self.failure_config, 'r') as failure_config_json_file:
                    failure_config_json_list_add = json.load(failure_config_json_file)
                self.failure_config_json_list = self.failure_config_json_list + failure_config_json_list_add

        except Exception as e:
            # print(e)
            # console.log("Ignoring Failure Reasons because JSON file was not found in path: " + self.failure_config)

            return

    def _match_failure_reasons(self, actual_message):
        if len(self.failure_config_json_list) == 0:
            self._parse_failure_json_file()

        try:
            act = actual_message.lower().replace('"', '').replace('\'', '').replace('.', '').strip()
            for item in self.failure_config_json_list:
                for it in item["StackTraceErrors"]:
                    it_mod = it.lower().replace('"', '').replace('\'', '').replace('.', '').strip()
                    if it_mod == act:
                        return item["CustomError"]

        except Exception as e:
            # print(e)
            return ""



    def _parse_execluded_reporting_keywords_json_file(self):

        try:
            with open(self.lib_path + '/' + self.excluded_reporting_keywords_orig,
                      "r") as excluded_reporting_keywords_json_file:
                excluded_reporting_keywords_dict_orig = json.load(excluded_reporting_keywords_json_file)
            if self.excluded_reporting_keywords != '' and self.excluded_reporting_keywords is not None:
                with open(self.excluded_reporting_keywords, "r") as excluded_reporting_keywords_json_file:
                    excluded_reporting_keywords_dict_add = json.load(excluded_reporting_keywords_json_file)

                for key in excluded_reporting_keywords_dict_orig.keys():
                    if key in excluded_reporting_keywords_dict_add.keys():
                        excluded_reporting_keywords_dict_orig[key] += excluded_reporting_keywords_dict_add[key]
            for key in excluded_reporting_keywords_dict_orig.keys():
                excluded_reporting_keywords_dict_orig[key] = [a.lower() for a in
                                                              excluded_reporting_keywords_dict_orig[key]]

            self.excluded_reporting_keyword_dict = excluded_reporting_keywords_dict_orig
            return

        except Exception as e:
            # print(e)
            # console.log("Ignoring excluded_reporting_keywords_json_file because JSON file was not found in path: " + excluded_reporting_keywords_loc)
            return





