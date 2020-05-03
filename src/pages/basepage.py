'''
Page Object Model implementation based on http://www.seleniumframework.com
'''
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
import traceback
import time
import logging

log = logging.getLogger('AutoDownloads.pages')

class BasePage(object):

    def __init__(self, driver, base_url):
        self.base_url = base_url
        self.driver = driver
        self.timeout = 30

    def find_element(self, *loc):
        return self.driver.find_element(*loc)

    def find_elements(self, *loc):
        return self.driver.find_elements(*loc)

    def visit(self):
        self.driver.get(self.base_url)

    def hover(self,element):
            ActionChains(self.browser).move_to_element(element).perform()
            # I don't like this but hover is sensitive and needs some sleep time
            time.sleep(5)

    def __getattr__(self, what):
        try:
            if what in self.locator_dictionary.keys():
                try:
                    element = WebDriverWait(self.driver,self.timeout).until(
                        EC.presence_of_element_located(self.locator_dictionary[what])
                    )
                except(TimeoutException,StaleElementReferenceException):
                    log.warning("presence of locator did not show before timeout")

                try:
                    element = WebDriverWait(self.driver,self.timeout).until(
                        EC.visibility_of_element_located(self.locator_dictionary[what])
                    )
                except(TimeoutException,StaleElementReferenceException):
                    log.warning("visibility of locator did not show before timeout")
                # I could have returned element, however because of lazy loading, I am seeking the element before return
                return self.find_element(*self.locator_dictionary[what])
        except AttributeError:
            log.error("locator [%s] not defined", what)
            super(BasePage, self).__getattribute__("method_missing")(what)

    def method_missing(self, what):
        log.error("No %s here!", what)
