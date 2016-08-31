This script is a bot to auto login your HSBC account which free you from the tedious two way authentication!

## New Feature

* Support to auto login and download eStatement from HSBC credit card account.

## Prerequisite

- Python2.7 or above
- selenium (python library)
- chrome browser (above v51.0 update-to-date version is recommended)
- [Chrome Driver](https://sites.google.com/a/chromium.org/chromedriver/downloads)

## Setup

Replace Username, first password, second password to yours in the "Src/Scrapper".

For example,

```Python
    sec_pwd ="some_second_password"

    usr_name_input.send_keys("your_usr_name")

    firstPassword.send_keys("your_pass_word")
```

Specify the location of your chromedriver

```Python
  # Create a new instance of the Firefox driver
  driver = webdriver.Chrome("your_path/chromedriver")
```

Change the location where you want to save statements

```Python
  local_filename = "Your_path" + filename + ".pdf"
```

## Usage

To download all statements from your account:

```
  Python AutoDownload.py -a
```

If you just want to download current monthly statement,

```
  Python AutoDownload.py -d
```

To retrieve a specific monthly statement, you can type (currently, HSBC only stores the latest 24 months' statements for their client):

```
Python AutoDownload.py -m Mon-YYYY (e.g., Python AutoDownload.py -m Jun-2016)
```
