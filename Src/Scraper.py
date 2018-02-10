from selenium import webdriver
from selenium.webdriver.support.ui import Select
from pathlib import Path
from time import sleep
import requests
import sys
import threading


class Scraper:
    SEC_PWD_ARR = ['your_second_pass_word_bit_array']
    DEFAULT_CURRENT = 'd'
    FILE_DIR = '/your_file_folder'
    CREDIT_CARD = 'c'
    SAVING_ACCOUNT = 'd'

    type = ''
    month_year_str = ''
    done = False
    current_window = ""
    download_type_dir = ''
    security_mode = False

    @staticmethod
    def thread(e, t):
        while not e.isSet():
            sys.stdout.write(">")
            sys.stdout.flush()
            e.wait(t)

    def create_thread(self, thread_name, e):
        return threading.Thread(name = thread_name,
                                target = self.thread,
                                args = (e, 1))

    def find_and_download_pdf(self, driver, download_type):
        # find month statement download link
        all_mon_odd_rows = driver.find_elements_by_xpath("//tr[@class=' rowodd']")
        all_mon_eve_rows = driver.find_elements_by_xpath("//tr[@class='zebra']")

        if download_type == self.SAVING_ACCOUNT:
            self.download_type_dir = "SavingAcc"
        elif download_type == self.CREDIT_CARD:
            self.download_type_dir = 'CrCard'

        for mon_odd_row in all_mon_odd_rows:
            if self.done:
                break
            self.click_download(mon_odd_row, driver)
            driver.switch_to.window(self.current_window)

        if self.type != self.DEFAULT_CURRENT:
            for mon_eve_row in all_mon_eve_rows:
                if self.done:
                    break
                self.click_download(mon_eve_row, driver)
                driver.switch_to.window(self.current_window)

    def click_download(self, mon_odd_row, driver):
        href_a = mon_odd_row.find_element_by_tag_name('a')
        filename = href_a.text.replace(' ', '-')

        # m for month, a for all
        if (self.type == 'm' or self.type == self.DEFAULT_CURRENT) and self.month_year_str in filename:
            self.done = True
            href_a.click()
        elif self.type == 'a':
            href_a.click()
        else:
            return False

        # switch to new open window
        # sleep(2)
        new_win = driver.window_handles[-1]
        driver.switch_to.window(new_win)

        # print(driver.page_source)
        # pdf_file = driver.find_element_by_tag_name("iframe")
        pdf_file = driver.find_element_by_xpath("//form[@name='downloadForm']")
        path = pdf_file.get_attribute('action')

        headers = {
            "User-Agent":
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"
        }
        s = requests.session()
        s.headers.update(headers)
        cookies = driver.get_cookies()
        for cookie in cookies:
            s.cookies.set(cookie['name'], cookie['value'])

        local_filename = "{!s}/{!s}/{!s}.pdf".format(self.FILE_DIR, self.download_type_dir, filename)
        file = Path(local_filename)
        if not file.is_file():
            r = s.get(path)
            open(local_filename, 'wb').write(r.content)
        else:
            print('\n' + filename + " File already existed")

        driver.close()

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

    def download(self, statement_issued_time, _month_year, day, card_type, security_mode):
        # day checking
        if day < 15 and statement_issued_time == self.DEFAULT_CURRENT:
            print("Current monthly credit & debit card e-statements are not issued.")
            return

        # initialize global type & month_year
        self.done = False
        self.type = statement_issued_time
        self.month_year_str = _month_year
        self.security_mode = security_mode
        print('Month-Year: ' + self.month_year_str + '\n')

        e = threading.Event()
        t1 = self.create_thread('scheduler1', e)
        t1.start()

        # Create a new instance of the Chrome driver
        driver = webdriver.Chrome("/your_driver_folder")

        # go to HSBC e-banking login page
        driver.get("https://www.ebanking.hsbc.com.hk/1/2/logon?LANGTAG=en&COUNTRYTAG=US")

        # find username input
        usr_name_input = driver.find_element_by_name("u_UserID")
        usr_name_input.send_keys("your_user_name")

        # submit the form
        submit = driver.find_element_by_xpath("//a[@href='javascript:PC_7_0G3UNU10SD0MHTI7TQA0000000000000_validate()']")
        submit.click()

        # now we are on the password input page
        first_password = driver.find_element_by_name("memorableAnswer")
        first_password.send_keys("your_pass_word")

        # find all secondary password input
        all_second_password = driver.find_elements_by_xpath("//input[@type='password']")

        # fill the second password
        for secondPwd in all_second_password:
            disable = secondPwd.get_attribute('disabled')
            memory_ans = secondPwd.get_attribute('aria-required')
            if disable is None and memory_ans is None:
                index_str = secondPwd.get_attribute('id')
                index = int(index_str[len(index_str) - 1])
                if index < 7:
                    secondPwd.send_keys(self.SEC_PWD_ARR[index])
                elif index == 7:
                    secondPwd.send_keys(self.SEC_PWD_ARR[len(self.SEC_PWD_ARR) - 2])
                elif index == 8:
                    secondPwd.send_keys(self.SEC_PWD_ARR[len(self.SEC_PWD_ARR) - 1])

        # press logon
        logon = driver.find_element_by_xpath("//input[@class='submit_input']")
        logon.click()

        e.set()
        print('\n' + "Logged in to System !" + '\n')

        # find eStatement and eAdvice tab on the left panel
        sleep(5)
        driver.maximize_window()
        statements_tab = driver.find_element_by_xpath("//a[contains(@data-url, 'personal.ebanking.hsbc.com.hk/1/2/obadaptor?cmd_in=&uid=banking.dashboard.estatement') and @data-camlevel='30']")
        statements_tab.click()

        # download debit card account eStatment first
        if 'd' in card_type:
            # check if debit card estatement is ready by day
            if day < 23 and statement_issued_time == 'd':
                print("Current monthly saving account estatement is not issued.")
                return

            e.clear()
            t2 = self.create_thread('scheduler2', e)
            t2.start()

            if security_mode:
                self.show_adddress_on_statement(e, driver)
                sleep(2)

            # select saving account
            select = Select(driver.find_element_by_xpath("//select[@id='number2']"))
            select.select_by_value('your_account_number')

            # click go and find eStament download list
            go_link = driver.find_element_by_xpath("//img[@src='/1/PA_defaultName/images/go.gif']")
            go_link.click()

            # find current window handle
            sleep(2)
            self.current_window = driver.window_handles[0]

            self.find_and_download_pdf(driver, self.SAVING_ACCOUNT)

            e.set()
            print('\n' + 'Saving Account e-Statement download finished!' + '\n')

        # download credit card account eStatment first
        if 'c' in card_type:
            self.done = False

            e.clear()
            t3 = self.create_thread('scheduler3', e)
            t3.start()

            # find credit card estatment download tab
            credit_card_tab = driver.find_element_by_xpath("//a[@id='Card']")

            # route to eStatement list tab page
            credit_card_tab.click()

            if self.security_mode:
                self.show_adddress_on_statement(e, driver)
                sleep(5)

            # find current window handle
            self.current_window = driver.window_handles[0]

            self.find_and_download_pdf(driver, self.CREDIT_CARD)
            e.set()
            print('\n' + "Credit card e-Statement download finished !")

        driver.close()