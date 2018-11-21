import perfecto
import os
import robot
import inspect
import urllib
import PerfectoLibrary

# import urlparse
from perfecto import *
from robot.libraries.BuiltIn import BuiltIn
from appium import webdriver
from .keywordgroup import KeywordGroup
from ._devices import _DeviceKeywords
# from urlparse import urlparse


class _RestKeywords(KeywordGroup):
    def __init__(self):
        self.bi = BuiltIn()
        self._check_driver=_DeviceKeywords._check_driver
        self.driver=None

    def _perform_rest_request(self,url):
        '''
        :param url:
        :return:
        '''
        return urllib.open(url)
    
    def _exeRestCmd(self,cmd,subcmd,params):
        '''

        :param cmd:
        :param subcmd:
        :param params:
        :return:
        '''
        actions={}
        
        actions['command'] = cmd
        actions['subcommand'] = subcmd
        
#         params={}
        if('deviceId' not in params):
            params['deviceId'] = self.driver.capabilities['devicename']
        svcStr="executions/"+self.driver.capabilities['executionId']
        res=self._exe_restops("command",svcStr,actions,params)
#         ConsoleUtils.logWarningBlocks("Step result:" +res);
#         Assert.assertTrue(res.toLowerCase().contains("success"),res);
        
    def retrieve_Device_Info(self,deviceid):
        '''

        :param deviceid:
        :return:
        '''
        acts={}
        params={}
        svcStr="handsets/"+deviceid
        self._exe_restops("info",svcStr,acts,params)
        
    def start_network_virtulization(self,deviceid,profile):
        '''

        :param deviceid:
        :param profile:
        :return:
        '''
        params={}
        params['deviceId']=deviceid
        params['profile']=profile
        self._exeRestCmd("vnetwork","start",params)
        
    def update_network_virtulization(self,deviceid,profile):
        '''

        :param deviceid:
        :param profile:
        :return:
        '''
        params={}
        params['deviceId']=deviceid
        params['profile']=profile
        self._exeRestCmd("vnetwork","update",params)
        
        
    def stop_network_virtualization(self,deviceid):
        '''

        :param deviceid:
        :return:
        '''
        params={}
        params['deviceId']=deviceid
        self._exeRestCmd("vnetwork","stop",params)
        
    def _exe_restops(self,ops,serviceStr,actions,params):
        '''

        :param ops:
        :param serviceStr:
        :param actions:
        :param params:
        :return:
        '''
        
        if self._check_driver:
            user=self.driver.capabilities['user']
            password=self.driver.capabilities['password']
            cloudServer=self.driver.capabilities['remote.server']
            securityToken=self.driver.capabilities['securityToken']
            # urlparse(url, scheme, allow_fragments)
            if (  None == securityToken or securityToken.trim().isEmpty()):
                authStr="&user=" + user + "&password=" + password
            else:
                authStr="&securityToken=" + securityToken
        
            actionStr=""
            for key, value in actions.iteritems():
                actionStr=actionStr+"&"+key+"="+value
                
            paramStr=""
            for key, value in params.iteritems():
                paramStr=paramStr+"&param." + key +"="+urllib.urlencode(value, "UTF-8")
                
            url = "https://" \
                + cloudServer \
                + "/services/" \
                + serviceStr \
                + "?operation=" + ops \
                + authStr \
                + actionStr \
                + paramStr

            self._perform_rest_request(url)


