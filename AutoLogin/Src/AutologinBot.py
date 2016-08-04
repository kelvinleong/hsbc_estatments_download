from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
import requests
import shutil

# Fill your second password
# sec_pwd =

# Create a new instance of the Firefox driver
driver = webdriver.Chrome("your_path/chromedriver")

# go to the google home page
driver.get("https://www2.ebanking.hsbc.com.hk/1/2/logon?LANGTAG=en&COUNTRYTAG=US")

# find username input
usr_name_input = driver.find_element_by_name("u_UserID")
usr_name_input.send_keys("your_usr_name")

# submit the form (although google automatically searches now without submitting)
submit = driver.find_element_by_xpath("//a[@href='javascript:PC_7_0G3UNU10SD0MHTI7TQA0000000000000_validate()']")
submit.click()

# now we are on the password input page
firstPassword = driver.find_element_by_name("memorableAnswer")
firstPassword.send_keys("your_pass_word")

# fill secondary password
all_secondPassword = []
all_secondPassword = driver.find_elements_by_xpath("//td[@width='28']")

valid_sec_pwd = []
i = 0
for secondPwd in all_secondPassword:
    sec_pwd_input = secondPwd.find_elements_by_xpath(".//label[@for='code']")
    if(len(sec_pwd_input) > 0):
        index_str = sec_pwd_input[0].text
        #print("index_str: " + index_str)
        if(len(index_str) < 10):
            if 'last' in index_str or 'Last' in index_str:
                if (index_str == 'Last'):
                    index = len(sec_pwd) - 1
                else:
                    index = len(sec_pwd) - int(index_str[0])
            else:
                index = int(index_str[0])
            valid_sec_pwd.append(sec_pwd[index])
            #print(valid_sec_pwd[i])
            i += 1

# fill the second password
j = 0
while (j < 3) :
    sec_pwd_name = 'RCC_PWD' + str(j + 1)
    field = driver.find_element_by_name(sec_pwd_name)
    field.send_keys(valid_sec_pwd[j])
    j += 1

# press logon
logon = driver.find_element_by_xpath("//input[@src='/P2GTheme/themes/html/BDE_HBAP_LOGON/images/buttons/btn_logon_png.gif']")
logon.click()

driver.get("https://www2.ebanking.hsbc.com.hk/1/3/cards?__cmd-All_MenuRefresh=")
link = driver.find_element_by_xpath("//a[@href='https://www2.ebanking.hsbc.com.hk/1/3/my-hsbc/estatement?cmd-ECorrespDummyPortlet_in=&designateType=Card']")
link.click()
