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