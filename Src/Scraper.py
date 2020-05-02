from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

from pathlib import Path
from time import sleep
import sys
import base64
from pathlib import Path
from pages.hsbcpage import *
from FileWatcher import FileWatcher
import logging
import platform
from datetime import datetime

log = logging.getLogger('AutoDownloads.Scraper')

class Scraper:
    DEFAULT_CURRENT = 'd'
    CREDIT_CARD = 'c'
    SAVING_ACCOUNT = 'd'

    type = ''
    month_year_str = ''
    done = False
    current_window = ""
    download_type_dir = ''
    security_mode = False


    class Context:
        """
        Context to be transfered from page to page in Page Object Model pattern
        """
        def __init__(self, cfg):
            self.driver = None
            self.cfg = cfg

            sysos = platform.system()
            self.file_dir = Path(cfg['Paths.' + sysos]['FILE_DIR'])
            self.chrome_driver_path = Path(cfg['Paths.' + sysos]['driver_path'])
            self.chrome_path = Path(cfg['Paths.' + sysos]['chrome_path'])

            #TODO find more secure way to manage secrets out of a file
            self.username = base64.b64decode(cfg['Account']['username'].encode()).decode()
            self.memorable = base64.b64decode(cfg['Account']['memorable'].encode()).decode()
            self.secret2 = base64.b64decode(cfg['Account']['secret2'].encode()).decode()

            self.accounts = [acc.strip() for acc in cfg['Account']['accounts'].split(",")]

            self.cc_issue = int(cfg['IssueDate']['credit_card'])
            self.st_issue = int(cfg['IssueDate']['statement'])

    def __init__(self, cfg):
        self.context = Scraper.Context(cfg)
        self.file_watcher = FileWatcher()

    def find_and_download_pdf(self, driver, download_type, account=""):
        self.done = False

        # find month statement download link
        page = MyBankingPage.StatementPage(self.context)
        rows = page.get_rows_buttons()
        downloaded_files = []
        if (self.type == 'm' or self.type == self.DEFAULT_CURRENT):
            date_file = [key for key in rows.keys() if self.month_year_str in key.replace(' ', '-')][0]
            fdpath = self.click_download(
                download_type,
                date_file,
                rows[date_file],
                driver,
                account
            )
            if fdpath is None:
                log.error("failed to download file")
            else:
                downloaded_files.append(fdpath)
        elif self.type == 'a':
            errors = 0
            for k, v in rows.items():
                log.info("download %s statement", k)
                fdpath = self.click_download(download_type, k, v, driver, account)
                if fdpath is None:
                    log.warning("failed to download %s while trying to download all statements, keep trying", k)
                    errors += 1
                else:
                    downloaded_files.append(fdpath)
            if errors > 0:
                log.warning("faced %n errors over %n files", errors, len(rows))
        return downloaded_files

    def click_download(self, download_type, file_date, link, driver, acc):
        current_win = driver.current_window_handle
        nbwin = len(driver.window_handles)
        linkhref = link.get_attribute('href')
        log.debug("initial url : [%s]", linkhref)

        """
        First click button and ignore automatic download that cannot be trapped
        then get updated file link after js processing to load in in new window
        """

        # blank download loop
        link.click()

        log.debug("wait for new window to be created")
        retry = 0
        times = 1
        while len(driver.window_handles) == nbwin and retry < 5:
            sleep(1)
            if times % 10 == 0:
                log.warning("no window for 5 sec: retry")
                link.click()
                retry += 1
            times += 1
        if len(driver.window_handles) == nbwin:
            log.error("issue to open download link for '%s': '%s'", file_date, link.get_attribute("href"))
        # switch to new open window
        log.debug("existing windows handlers after click: [%s]", "-".join([str(h) for h in driver.window_handles]))
        new_win = driver.window_handles[-1]
        if new_win == current_win:
            log.warn("switching to same window")
        else:
            log.debug("switching to nw window '%s'", new_win)
        driver.switch_to.window(new_win)
        sleep(2)
        driver.close()
        sleep(1)
        driver.switch_to.window(current_win)

        # get updated file link and proceed download in new window
        linkhref = link.get_attribute('href')
        log.debug("after url : [%s]", linkhref)

        driver.execute_script("window.open()")

        log.debug("wait for new window to be created")
        retry = 0
        times = 1
        while len(driver.window_handles) == nbwin and retry < 5:
            sleep(1)
            if times % 10 == 0:
                log.warning("no window for 5 sec: retry")
                driver.execute_script("window.open()")
                retry += 1
            times += 1
        if len(driver.window_handles) == nbwin:
            log.error("issue to open download link for '%s': '%s'", file_date, link.get_attribute("href"))
        # switch to new open window
        log.debug("existing windows handlers after click: [%s]", "-".join([str(h) for h in driver.window_handles]))
        new_win = driver.window_handles[-1]
        if new_win == current_win:
            log.warn("switching to same window")
        else:
            log.debug("switching to nw window '%s'", new_win)
        driver.switch_to.window(new_win)
        sleep(2)
        self.file_watcher.start()
        driver.get(linkhref)

        pref = "SAVING_ACC"
        if download_type == self.SAVING_ACCOUNT:
            pref = "SAVING_ACC"
        elif download_type == self.CREDIT_CARD:
            pref = 'CREDIT_CARD'

        strdate = datetime.strptime(file_date, "%d %b %Y").strftime("%Y%m%d")
        fname = "{!s}-{!s}-{!s}.pdf".format(pref, acc, strdate)
        targetfile = self.context.file_dir / fname
        success = self.file_watcher.wait_move_file(targetfile, 60)
        if success:
            log.debug("statement downloaded : %s", str(targetfile))
        # close current download window
        driver.close()
        sleep(1)
        driver.switch_to.window(current_win)
        sleep(1)
        log.debug("download window closed and switched back to statements page")
        return targetfile if success else None

    """
    def show_adddress_on_statement(self, e, driver):
        e.set()
        check_box = driver.find_element_by_xpath("//input[@type='checkbox']")
        check_box.click()

        go_button = driver.find_element_by_xpath("//a[@id='viewns_7_0G3UNU10SD0MHTI7STB0000000_:searchForm:gobutton']")
        go_button.click()

        passcode = input("Press passcode to continue: ")

        passcode_input = driver.find_element_by_xpath("//input[@type='password']")
        passcode_input.send_keys(passcode)

        confirm_button = driver.find_element_by_xpath("//a[@onclick='return checkIfSubmitted(PC_7_81861HO0HG0180AJ125VE110O1000000_submitForm)']")
        confirm_button.click()
    """

    def download(self, statement_issued_time, _month_year, day, card_type, security_mode):
        # day checking
        if day < self.context.cc_issue and statement_issued_time == self.DEFAULT_CURRENT:
            log.info("Current monthly credit & debit card e-statements are not issued.")
            return

        # initialize global type & month_year
        self.type = statement_issued_time
        self.month_year_str = _month_year
        self.security_mode = security_mode
        log.debug('Month-Year: ' + self.month_year_str + '\n')

        # Create a new instance of the Chrome driver
        chrome_options = Options()
        if str(self.context.chrome_path) != '.':
            chrome_options.binary_location = str(self.context.chrome_path)
        for key, val in self.context.cfg.items('ChromeConfig'):
            chrome_options.add_argument('--' + key)
            if key == 'headless':
                isheadless = True

        chrome_options.add_experimental_option('prefs', {
                "download": {
                    "default_directory": str(self.file_watcher.get_dir()),
                    "prompt_for_download": False,
                    "directory_upgrade": True,
                },
                "download_restrictions": 0
            }
        )

        driver = webdriver.Chrome(
            str(self.context.chrome_driver_path),
            options=chrome_options
        )

        driver.implicitly_wait(5)
        driver.maximize_window()
        self.context.driver = driver
        log.info("driver is live, let's start")

        # go to HSBC e-banking login page
        page = HomePage(self.context)
        page.visit()
        page.login(self.context.username)

        # now we are on the password input page
        page = LoginPage(self.context)
        page.login(self.context.memorable, self.context.secret2)
        log.debug("Logged in to System !")

        # goto Statement page
        page = MyBankingPage(self.context)
        page.goto_statements()
        page = page.StatementPage(self.context)

        # download debit card account eStatment first
        if 'd' in card_type:
            log.info("manage account statements")
            # check if debit card estatement is ready by day
            if day < self.context.st_issue and statement_issued_time == 'd':
                log.warning("Current monthly saving account estatement is not issued.")
            else:
                # select saving accounts
                for acc in page.get_accounts_list():
                    log.info("manage account {}...".format(acc))
                    page.select_account(acc)
                    # if security_mode:
                    #    self.show_adddress_on_statement(e, driver)
                    #    sleep(2)

                    sleep(1)
                    self.find_and_download_pdf(driver, self.SAVING_ACCOUNT, acc)


        # download credit card account eStatment first
        if 'c' in card_type:
            log.info("manage cards statements")
            # select saving accounts
            for card in page.get_cards_list():
                log.info("manage card {}...".format(card))
                page.select_card(card)
                # if security_mode:
                #    self.show_adddress_on_statement(e, driver)
                #    sleep(2)

                sleep(1)
                self.find_and_download_pdf(driver, self.CREDIT_CARD)

        log.info("processing done")
        # close main window
        driver.close()