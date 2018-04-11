import perfecto
import os
import robot
import inspect
from perfecto import *
from robot.libraries.BuiltIn import BuiltIn
from .keywordgroup import KeywordGroup

class _DeviceKeywords(KeywordGroup):
    def __init__(self):
		self.bi = BuiltIn()
		
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
    def scroll_to_element(self,elementxpath):
        params = {}
        params['element'] = self.driver.find_element_by_xpath(elementxpath).get_id()
        params['toVisible'] = 'any'
        self.driver.execute_script('mobile:scroll', params)
