import perfecto
import os
import robot
import inspect
import PerfectoLibrary
import appium
import urllib2
import traceback
import time
import sys
from perfecto import *
from robot.libraries.BuiltIn import BuiltIn
# from appium import webdriver
from .keywordgroup import KeywordGroup
from ..listeners import *


class _GeneralKeywords(KeywordGroup):
    def __init__(self):
        self.bi = BuiltIn()
        self.reportPdfUrl = ''

    def init_driver(self):
        self._check_driver()

    def _check_driver(self):

        try:
            aplib = self.bi.get_library_instance('AppiumLibrary')
            self.driver = aplib._current_application()
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
        if self.driver != None:
            self.reportPdfUrl=self.driver.capabilities['reportPdfUrl']

    def enable_proxy(self, str):
        proxy = str
        os.environ['http_proxy'] = proxy
        os.environ['HTTP_PROXY'] = proxy
        os.environ['https_proxy'] = proxy
        os.environ['HTTPS_PROXY'] = proxy

    def disable_proxy(self):
        proxy = ""
        os.environ['http_proxy'] = proxy
        os.environ['HTTP_PROXY'] = proxy
        os.environ['https_proxy'] = proxy
        os.environ['HTTPS_PROXY'] = proxy
        try:
            del os.environ['http_proxy']
            del os.environ['https_proxy']
            del os.environ['HTTP_PROXY']
            del os.environ['HTTPS_PROXY']
        except:
            pass


    def maximize_window(self):
        if self._check_driver():
            self.driver.maximize_window()

    def download_summary_pdf_report(self, reportpath, sectoken, executionID=None, jobName=None, jobNumber=None,
                                    tags=None):
        '''

        :param reportpath: the local path where you want to store the pdf reports
                sectoken: perfecto securitytoken to access the report
                executionID: the executionID of the reports
                jobName: the jobName of the reports
                jobID: the jobID of the reports
                tags: the tags of the reports
        :return: return false if anything go wrong
        '''
        exeRptUrl = self.reportPdfUrl
        rptQuery = ''
        if self.reportPdfUrl != '':

            if executionID == None and jobName == None and jobNumber == None and tags == None:
                exeRptUrl = self.reportPdfUrl
            else:
                if executionID != None:
                    if rptQuery == '':
                        rptQuery = 'externalId[0]=' + executionID
                    else:
                        rptQuery = rptQuery + '&' + 'externalId[0]=' + executionID
                if jobName != None:
                    if rptQuery == '':
                        rptQuery = 'jobName[0]=' + jobName
                    else:
                        rptQuery = rptQuery + '&' + 'jobName[0]=' + jobName
                if tags != None:
                    if rptQuery == '':
                        rptQuery = 'tags[0]=' + tags
                    else:
                        rptQuery = rptQuery + '&' + 'tags[0]=' + tags
                if jobNumber != None:
                    if rptQuery == '':
                        rptQuery = 'jobNumber[0]=' + jobNumber
                    else:
                        rptQuery = rptQuery + '&' + 'jobNumber[0]=' + jobNumber
                exeRptUrl = self.reportPdfUrl.split('pdf?')[0] + 'pdf?' + rptQuery
                # self.bi.log_to_console(exeRptUrl)

            time.sleep(10)  # have to sleep for 10 seconds
            try:
                headers = {'PERFECTO-AUTHORIZATION': sectoken, }
                req = urllib2.Request(exeRptUrl, None, headers)
                rp = urllib2.urlopen(req)
                with open(reportpath + self.reportPdfUrl.rsplit('=', 1)[-1] + '.pdf', 'wb') as output:
                    output.write(rp.read())
                    output.close()
                return True
            except:
                self.bi.log_to_console(traceback.print_exc())
                return False
        self.bi.log_to_console("empty with " + self.reportPdfUrl)
        return False