from selenium import webdriver
from selenium.webdriver.support.ui import Select
import requests
import sys
import threading

type = ''
month_year_str = ''
done = ''
cur_win = ""
download_type = ''

def thread(e, t):
    while not e.isSet():
        sys.stdout.write(">")
        sys.stdout.flush()
        e.wait(t)

def clickDownload(mon_odd_row, driver):
    href_a = mon_odd_row.find_element_by_tag_name('a')
    filename = href_a.text.replace(' ', '-')

    if( (type == 'm' or type == 'd') and month_year_str in filename):
        global done
        done = True
        href_a.click()
    else:
        return

    # switch to new open window
    new_win = driver.window_handles[1]
    driver.switch_to.window(new_win)

    # print(driver.page_source)
    pdf_file = driver.find_element_by_tag_name("iframe")
    path = pdf_file.get_attribute("src")

    # driver.get(path)

    headers = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    }

    s = requests.session()
    s.headers.update(headers)

    cookies = driver.get_cookies()
    for cookie in driver.get_cookies():
        # c = {cookie['name']: cookie['value']}
        s.cookies.set(cookie['name'], cookie['value'])

    local_filename = "some_path/" + download_type + "/" + filename + ".pdf"
    r = s.get(path)
    open(local_filename, 'wb').write(r.content)

    driver.close()
    driver.switch_to.window(cur_win)

def download(_type, _month_year, _day ):
    # day checking
    # note you must change the value according to your credit card statement issue day
    if _day < 15 and _type == 'd':
        print("Current Monthly credit card statments is not issued.")
        return

    # initialize global type & month_year
    global done
    done = False
    global type
    type = _type
    global month_year_str
    month_year_str = _month_year
    print('Type:' + type + ' Month-Year: ' + month_year_str)

    e = threading.Event()
    t1 = threading.Thread(name='scheduler',
                          target=thread,
                          args=(e, 1))
    t1.start()

    sec_pwd = ['0', 's', 'e', 'c', 'p', 'w', 'd']

    # Create a new instance of the Firefox driver
    # driver = webdriver.Chrome("/Users/kelvinleung/PycharmProjects/chromedriver")
    driver = webdriver.PhantomJS(executable_path=r'/path/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs')

    # go to the google home page
    driver.get("https://www2.ebanking.hsbc.com.hk/1/2/logon?LANGTAG=en&COUNTRYTAG=US")

    # find username input
    usr_name_input = driver.find_element_by_name("u_UserID")
    usr_name_input.send_keys("your_user_id)

    # submit the form (although google automatically searches now without submitting)
    submit = driver.find_element_by_xpath("//a[@href='javascript:PC_7_0G3UNU10SD0MHTI7TQA0000000000000_validate()']")
    submit.click()

    # now we are on the password input page
    firstPassword = driver.find_element_by_name("memorableAnswer")
    firstPassword.send_keys("some_password")

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

    # route to Card tab page
    driver.get("https://www1.personal.ebanking.hsbc.com.hk/1/3/cards?__cmd-All_MenuRefresh=")

    # click e-Statement hyperlink
    link = driver.find_element_by_xpath("//a[@href='https://www1.personal.ebanking.hsbc.com.hk/1/3/my-hsbc/estatement?cmd-ECorrespDummyPortlet_in=&designateType=Card']")
    link.click()

    # find current window handle
    global cur_win
    cur_win = driver.window_handles[0]

    # find month statement download link
    all_mon_odd_rows = driver.find_elements_by_xpath("//tr[@class=' rowodd']")
    all_mon_eve_rows = driver.find_elements_by_xpath("//tr[@class='zebra']")

    global download_type
    download_type = "CrCard"
    for mon_odd_row in all_mon_odd_rows:
        if done:
            break
        clickDownload(mon_odd_row, driver)

    if type != 'd':
        for mon_eve_row in all_mon_eve_rows:
            if done:
                break
            clickDownload(mon_eve_row, driver)

    e.set()
    print('\n' + "Credit card e-Statement download finished >>>>>>>")

    # change the day to your saving account statement issue day
    if _day < 23 and _type == 'd':
        print("Current monthly saving account estatement is not issued.")
        return

    e.clear()
    t2 = threading.Thread(name='scheduler2',
                          target=thread,
                          args=(e, 1))


    t2.start()
    # route to bank statement download page
    done = False
    all_ext_elements = driver.find_elements_by_xpath("//div[@class='extBgFix']")

    for ext_element in all_ext_elements:
        link = ext_element.find_element_by_tag_name('a')
        if "eStatement" in link.text:
            link.click()
            break

    # select 5xx account
    select = Select(driver.find_element_by_xpath("//select[@id='number2']"))
    select.select_by_value('account_no')

    # click go
    go_link = driver.find_element_by_xpath("//img[@src='/1/PA_defaultName/images/go.gif']")
    go_link.click()

    # find current window handle
    # global cur_win
    cur_win = driver.window_handles[0]

    # find month statement download link
    all_mon_odd_rows = driver.find_elements_by_xpath("//tr[@class=' rowodd']")
    all_mon_eve_rows = driver.find_elements_by_xpath("//tr[@class='zebra']")

    # find month statement download link
    # global download_type
    download_type = "SavingAcc"
    for mon_odd_row in all_mon_odd_rows:
        if done:
            break
        clickDownload(mon_odd_row, driver)

    if type != 'd':
        for mon_eve_row in all_mon_eve_rows:
            if done:
                break
            clickDownload(mon_eve_row, driver)

    e.set()
    print('\n' + 'Saving Account e-Statement download finished!>>>>>>>>>>>>>>>>')
