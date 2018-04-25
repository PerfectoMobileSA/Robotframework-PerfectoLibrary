import perfecto
import os
import robot
import inspect
from perfecto import *
from robot.libraries.BuiltIn import BuiltIn
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.common.action_chains import ActionChains
from SeleniumLibrary import ElementFinder
from .keywordgroup import KeywordGroup

class _DeviceKeywords(KeywordGroup):
    def __init__(self):
		self.bi = BuiltIn()
		self._element_finder = ElementFinder(self)
    def init_device(self):
		aplib = self.bi.get_library_instance('AppiumLibrary')
		self.driver = aplib._current_application()
		
    def rotate(self,state = 'landscape',method = 'device'):
        params = {}
        params['state'] = state
        params['method'] = method
        self.driver.execute_script('mobile:device:rotate', params)
        
    def start_application_by_name(self,name):
        params = {}
        params['identifier'] = name
        self.driver.execute_script('mobile:application:open', params)
    
    def button_image_click(self,label,threhold=80):
        params = {}
        params['label']= label
        params['threshold']= threhold
        params['imageBounds.needleBound']= 30
        self.driver.execute_script('mobile:button-image:click', params)       
    def maximize_window(self):
        self.driver.maximize_window()
    def scroll_to_element(self,elementxpath,dir):
        params = {}
        params['element'] = self.driver.find_element_by_xpath(elementxpath).id
        params['toVisible'] = 'any'
        params['direction'] = dir
        self.driver.execute_script('mobile:scroll', params)
    def scroll_element_into_view(self,locator):
        element=self.driver.find_element(locator)
        ActionChains(self.driver).move_to_element(element).perform()
    def set_focus_to_element(self, locator):
        """Sets focus to element identified by ``locator``.
        See the `Locating elements` section for details about the locator
        syntax.
        Prior to SeleniumLibrary 3.0 this keyword was named `Focus`.
        """
        element = self._element_finder.find_element(locator)
        self.driver.execute_script("arguments[0].focus();", element)
    def focus(self, locator):
        """Deprecated. Use `Set Focus To Element` instead."""
        self.set_focus_to_element(locator)   
