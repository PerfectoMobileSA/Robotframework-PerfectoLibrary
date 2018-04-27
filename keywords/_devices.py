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
from selenium.webdriver.support.ui import Select

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
    def execute_javascript(self, *code):
        """Executes the given JavaScript code.
        ``code`` may contain multiple lines of code and may be divided into
        multiple cells in the test data. In that case, the parts are
        concatenated together without adding spaces.
        If ``code`` is an absolute path to an existing file, the JavaScript
        to execute will be read from that file. Forward slashes work as
        a path separator on all operating systems.
        The JavaScript executes in the context of the currently selected
        frame or window as the body of an anonymous function. Use ``window``
        to refer to the window of your application and ``document`` to refer
        to the document object of the current frame or window, e.g.
        ``document.getElementById('example')``.
        This keyword returns whatever the executed JavaScript code returns.
        Return values are converted to the appropriate Python types.
        Examples:
        | `Execute JavaScript` | window.myFunc('arg1', 'arg2') |
        | `Execute JavaScript` | ${CURDIR}/js_to_execute.js    |
        | ${sum} =             | `Execute JavaScript` | return 1 + 1; |
        | `Should Be Equal`    | ${sum}               | ${2}          |
        """
        js = self._get_javascript_to_execute(code)
        self.info("Executing JavaScript:\n%s" % js)
        return self.driver.execute_script(js)
    
    def _get_javascript_to_execute(self, lines):
        code = ''.join(lines)
        path = code.replace('/', os.sep)
        if os.path.isabs(path) and os.path.isfile(path):
            code = self._read_javascript_from_file(path)
        return code

    def _read_javascript_from_file(self, path):
        self.info('Reading JavaScript from file <a href="file://%s">%s</a>.'
                  .format(path.replace(os.sep, '/'), path), html=True)
        with open(path) as file:
            return file.read().strip()
    def select_radio_button(self, group_name, value):
        """Sets radio button group ``group_name`` to ``value``.
        The radio button to be selected is located by two arguments:
        - ``group_name`` is the name of the radio button group.
        - ``value`` is the ``id`` or ``value`` attribute of the actual
          radio button.
        Examples:
        | `Select Radio Button` | size    | XL    |
        | `Select Radio Button` | contact | email |
        """
        self.info("Selecting '%s' from radio button '%s'."
                  % (value, group_name))
        element = self._get_radio_button_with_value(group_name, value)
        if not element.is_selected():
            element.click()
    def select_from_list(self, locator, *options):
        """Deprecated. Use `Select From List By Label/Value/Index` instead.
        This keyword selects options based on labels or values, which makes
        it very complicated and slow. It has been deprecated in
        SeleniumLibrary 3.0, and dedicated keywords `Select From List By
        Label`, `Select From List By Value` and `Select From List By Index`
        should be used instead.
        """
        non_existing_items = []
        items_str = options and "option(s) '%s'" % ", ".join(options) or "all options"
        self.info("Selecting %s from list '%s'." % (items_str, locator))
        select = self._get_select_list(locator)
        if not options:
            for i in range(len(select.options)):
                select.select_by_index(i)
            return
        for item in options:
            try:
                select.select_by_value(item)
            except:
                try:
                    select.select_by_visible_text(item)
                except:
                    non_existing_items = non_existing_items + [item]
                    continue
        if any(non_existing_items):
            if select.is_multiple:
                raise ValueError("Options '%s' not in list '%s'." % (", ".join(non_existing_items), locator))
            else:
                if any (non_existing_items[:-1]):
                    items_str = non_existing_items[:-1] and "Option(s) '%s'" % ", ".join(non_existing_items[:-1])
                    self.warn("%s not found within list '%s'." % (items_str, locator))
                if options and options[-1] in non_existing_items:
                    raise ValueError("Option '%s' not in list '%s'." % (options[-1], locator))

    
    def select_from_list_by_index(self, locator, *indexes):
        """Selects options from selection list ``locator`` by ``indexes``.
        Indexes of list options start from 0.
        If more than one option is given for a single-selection list,
        the last value will be selected. With multi-selection lists all
        specified options are selected, but possible old selections are
        not cleared.
        See the `Locating elements` section for details about the locator
        syntax.
        """
        if not indexes:
            raise ValueError("No indexes given.")
 
        select = self._get_select_list(locator)
        for index in indexes:
            select.select_by_index(int(index))

    
    def select_from_list_by_value(self, locator, *values):
        """Selects options from selection list ``locator`` by ``values``.
        If more than one option is given for a single-selection list,
        the last value will be selected. With multi-selection lists all
        specified options are selected, but possible old selections are
        not cleared.
        See the `Locating elements` section for details about the locator
        syntax.
        """
        if not values:
            raise ValueError("No values given.")

        select = self._get_select_list(locator)
        for value in values:
            select.select_by_value(value)

    
    def select_from_list_by_label(self, locator, *labels):
        """Selects options from selection list ``locator`` by ``labels``.
        If more than one option is given for a single-selection list,
        the last value will be selected. With multi-selection lists all
        specified options are selected, but possible old selections are
        not cleared.
        See the `Locating elements` section for details about the locator
        syntax.
        """
        if not labels:
            raise ValueError("No labels given.")

        select = self._get_select_list(locator)
        for label in labels:
            select.select_by_visible_text(label)
    def _get_select_list(self, locator):
        el = self._element_finder.find_element(locator, tag='list')
        return Select(el)

    def _get_options(self, locator):
        return self._get_select_list(locator).options

    def _get_selected_options(self, locator):
        return self._get_select_list(locator).all_selected_options

    def _get_labels(self, options):
        return [opt.text for opt in options]

    def _get_values(self, options):
        return [opt.get_attribute('value') for opt in options]
