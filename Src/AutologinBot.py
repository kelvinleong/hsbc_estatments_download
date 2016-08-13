from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
import requests
import shutil

sec_pwd = "some_second_password"

# Create a new instance of the Firefox driver
driver = webdriver.Chrome("/Users/kelvinleung/PycharmProjects/chromedriver")

# go to the google home page
driver.get("https://www2.ebanking.hsbc.com.hk/1/2/logon?LANGTAG=en&COUNTRYTAG=US")

# find username input
usr_name_input = driver.find_element_by_name("u_UserID")
usr_name_input.send_keys("some_UserID")

# submit the form (although google automatically searches now without submitting)
submit = driver.find_element_by_xpath("//a[@href='javascript:PC_7_0G3UNU10SD0MHTI7TQA0000000000000_validate()']")
submit.click()

# now we are on the password input page
firstPassword = driver.find_element_by_name("memorableAnswer")
firstPassword.send_keys("some_pass_word")

# find all secondary password input
all_secondPassword = []
all_secondPassword = driver.find_elements_by_xpath("//input[@type='password']")

valid_sec_pwd = []
i = 0
# fill the second password
for secondPwd in all_secondPassword:
    isDisable = secondPwd.get_attribute('disabled')
    isMemAnw = secondPwd.get_attribute('aria-required')
    if(isDisable == None and isMemAnw == None):
        index_str = secondPwd.get_attribute('id')
        index = int(index_str[len(index_str) - 1])
        if(index < 7):
            secondPwd.send_keys(sec_pwd[index])
        elif(index == 7):
            secondPwd.send_keys(sec_pwd[len(sec_pwd) - 2])
        elif(index == 8):
            secondPwd.send_keys(sec_pwd[len(sec_pwd) - 1])

# press logon
logon = driver.find_element_by_xpath("//input[@class='submit_input']")
logon.click()

# route to Cart tab page
driver.get("https://www1.personal.ebanking.hsbc.com.hk/1/3/cards?__cmd-All_MenuRefresh=")

# click e-Statement hyperlink
link = driver.find_element_by_xpath("//a[@href='https://www1.personal.ebanking.hsbc.com.hk/1/3/my-hsbc/estatement?cmd-ECorrespDummyPortlet_in=&designateType=Card']")
link.click()

# find current window handle
cur_win = driver.window_handles[0]

# find month statement download link
all_mon_odd_rows = driver.find_elements_by_xpath("//tr[@class=' rowodd']")
all_mon_eve_rows = driver.find_elements_by_xpath("//tr[@class='zebra']")

for mon_odd_row in all_mon_odd_rows:
    href_a = mon_odd_row.find_element_by_tag_name('a')
    print("Month" + href_a.text)

pdf_link = driver.find_element_by_xpath("//a[@id='viewns_7_0G3UNU10SD0MHTI7STB0000000_:list:_idJsp49ns_7_0G3UNU10SD0MHTI7STB0000000_:0:_idJsp56ns_7_0G3UNU10SD0MHTI7STB0000000_']")
pdf_link.click()

# switch to new open window
new_win = driver.window_handles[1]
driver.switch_to.window(new_win)

#print(driver.page_source)
pdf_file = driver.find_element_by_tag_name("iframe")
path = pdf_file.get_attribute("src")

#driver.get(path)

headers = {
"User-Agent":
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
}

s = requests.session()
s.headers.update(headers)

cookies = driver.get_cookies()
for cookie in driver.get_cookies():
    #c = {cookie['name']: cookie['value']}
    s.cookies.set(cookie['name'], cookie['value'])

local_filename = "some_folder"
r = s.get(path)
open(local_filename, 'wb').write(r.content)

driver.close()
driver.switch_to.window(cur_win)
