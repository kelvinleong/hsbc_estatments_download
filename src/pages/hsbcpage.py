from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from .basepage import BasePage
import logging
from time import sleep

log = logging.getLogger('AutoDownloads.pages.hsbc')

class HomePage(BasePage):

    def __init__(self, context):
        BasePage.__init__(
            self,
            context.driver,
            base_url='https://www.ebanking.hsbc.com.hk/1/2/logon?LANGTAG=en&COUNTRYTAG=US')

    locator_dictionary = {
        "usrname": (By.NAME, 'userid'),
        "submit": (By.CLASS_NAME, 'submit_input')
    }

    def login(self,username):
        self.usrname.send_keys(username)
        self.submit.click()
        WebDriverWait(self.driver, 15).until(EC.title_contains("Log on"))
        log.debug("moved to login page")

class LoginPage(BasePage):

    def __init__(self, context):
        BasePage.__init__(
            self,
            context.driver,
            base_url='')

    locator_dictionary = {
        "memorable": (By.NAME, 'memorableAnswer'),
        "second_password": (By.XPATH, "//input[@type='password']"),
        "logon": (By.XPATH, "//input[@class='submit_input']")
    }

    def login(self,pwd1, pwd2):
        pwd2 = pwd2[:6] + pwd2[-2:]
        self.memorable.send_keys(pwd1)
        elts = self.find_elements(*self.locator_dictionary["second_password"])
        for elt in elts:
            if elt.get_attribute('disabled') is None and elt.get_attribute('class') == "smallestInput active":
                elt.send_keys(pwd2[int(elt.get_attribute('id')[-1]) - 1])
        self.logon.click()
        WebDriverWait(self.driver, 15).until(EC.title_contains("My banking"))
        sleep(4)
        log.debug("moved to main page")


class MyBankingPage(BasePage):

    def __init__(self, context):
        BasePage.__init__(
            self,
            context.driver,
            base_url='')

    locator_dictionary = {
        "old_menu": (By.LINK_TEXT, "Use the old internet banking"),
        "confirm_leave": (
            By.CSS_SELECTOR,
            ".confirmLeave button[data-dojo-attach-point='leaveDialogBtn'][tabindex='0'][type='button']"
        ),
        "main_menu": (By.ID, "dijit__WidgetBase_0"),
        "menu_statement": (By.LINK_TEXT, "View/Manage documents")
    }

    def goto_old_page(self):
        self.old_menu.click()
        self.confirm_leave.click()
        WebDriverWait(self.driver, 15).until(EC.title_contains("My HSBC"))
        sleep(4)

    def goto_statements(self):
        self.main_menu.click()
        self.menu_statement.click()
        WebDriverWait(self.driver, 15).until(EC.title_contains("Statements"))
        sleep(4)
        log.debug("moved to statement page")

    class StatementPage(BasePage):

        ACC_TYPE = {
            "HSBC Premier": "accounts",
            "HSBC Premier Credit Card": "cards"
        }

        def __init__(self, context):
            BasePage.__init__(
                self,
                context.driver,
                base_url='')
            self.accounts = None
            self.cards = None

        locator_dictionary = {
            "account_selector": (By.ID, "arrowid_group_gpib_newstmt_bijit_AccountSelect_0"),
            "acc_list_container": (By.ID, "group_gpib_newstmt_bijit_AccountSelect_0_menu"),
            "accounts_list": (By.CSS_SELECTOR, "tr.dijitMenuItem"),
            "acc_item_type": (By.CSS_SELECTOR, "span[class='title cobrowse_hide']"),
            "acc_item_number": (By.CSS_SELECTOR, "span[class='accountDetails cobrowse_hide']"),

            "st_row": (By.CSS_SELECTOR, "div[class='row statementListItem']"),
            "st_row_date": (By.CSS_SELECTOR, "div[class='statementListItemText statementListItemTextUS']"),
            "st_row_button": (By.CSS_SELECTOR, "a[data-dojo-attach-point='statementDownloadFileAP']"),

            "view_more": (By.ID, "showMoreButton"),
        }

        def _get_account_menu(self):
            self.accounts = {}
            self.cards = {}
            account_list = {'accounts': self.accounts, 'cards': self.cards}
            self.account_selector.click()
            c = self.acc_list_container
            log.debug("found account menu container")
            items = c.find_elements(*self.locator_dictionary['accounts_list'])
            log.debug("found account list item")
            for e in items:
                acc_type = e.find_element(*self.locator_dictionary['acc_item_type']).get_attribute("innerHTML")
                log.debug("found item account type '%s'", acc_type)
                acc_number = e.find_element(*self.locator_dictionary['acc_item_number']).get_attribute("innerHTML")
                log.debug("found item account number '%s'", acc_number)
                account_list[self.ACC_TYPE[acc_type]][acc_number] = e
            self.account_selector.click()
            log.debug("found all available accounts")

        def get_accounts_list(self):
            if self.accounts is None:
                self._get_account_menu()
            return self.accounts.keys()

        def get_cards_list(self):
            if self.cards is None:
                self._get_account_menu()
            return self.cards.keys()

        def select_account(self, account):
            if self.accounts is None:
                self._get_account_menu()
            self.account_selector.click()
            #self.accounts[account].click()
            action = ActionChains(self.driver)
            action.move_to_element(self.accounts[account]).click().perform()
            sleep(5)

        def select_card(self, card):
            if self.accounts is None:
                self._get_account_menu()
            self.account_selector.click()
            #self.cards[card].click()
            action = ActionChains(self.driver)
            action.move_to_element(self.cards[card]).click().perform()
            sleep(2)

        def get_rows_buttons(self):
            result = {}
            if self.view_more.is_displayed:
                self.view_more.click()
                sleep(5)
            rows = self.find_elements(*self.locator_dictionary['st_row'])
            for r in rows:
                row_date = r.find_element(*self.locator_dictionary['st_row_date']).get_attribute("innerHTML")
                row_button = r.find_element(*self.locator_dictionary['st_row_button'])
                result[row_date] = row_button
            return result
