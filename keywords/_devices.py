import perfecto
import os
import robot
import inspect
from perfecto import *
from robot.libraries.BuiltIn import BuiltIn
from appium import webdriver
from .keywordgroup import KeywordGroup
from ..listeners import * 


class _DeviceKeywords(KeywordGroup):
    def __init__(self):
        self.bi = BuiltIn()
        
    def _check_driver(self):
        try:
            if isinstance(PerfectoLibrary.driver, webdriver):
                self.driver=PerfectoLibrary.driver
                return True
            else:
                return False
        except:
            log_to_console("Your script is not using Appium Driver, devices keywords will not be able to performed")
    def rotate(self,state = 'landscape',method = 'device'):
        if self._check_driver:
            params = {}
            params['state'] = state
            params['method'] = method
            self.driver.execute_script('mobile:device:rotate', params)
        
    def start_application_by_name(self,name):
        if self._check_driver:
            params = {}
            params['identifier'] = name
            self.driver.execute_script('mobile:application:open', params)
    
    def button_image_click(self,label,threhold=80):
        if self._check_driver:
            params = {}
            params['label']= label
            params['threshold']= threhold
            params['imageBounds.needleBound']= 30
            self.driver.execute_script('mobile:button-image:click', params)       
    def maximize_window(self):
        if self._check_driver:
            self.driver.maximize_window()
    def scroll_to_element(self,elementxpath):
        if self._check_driver:
            params = {}
            params['element'] = (self.driver.findElement(By.xpath(elementxpath))).GetId()
            params['toVisible'] = 'any'
            self.driver.execute_script('mobile:scroll', params)
