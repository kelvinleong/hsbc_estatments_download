This script is a bot to auto login your HSBC account which free you from the tedious two way authentication!

## New Feature

* Support to auto login and download eStatement from HSBC credit card account
* Support Saving account and Credit card account statements download
* Support statement type (credit and/or debit card) download configuration

## Prerequisite

- Python3.6+
- selenium (python library) 3.141.0+
- chrome browser (above v77.0.3865.75+)
- [Chrome Driver](https://sites.google.com/a/chromium.org/chromedriver/downloads 77.0.3865.40+)

## Setup

create a config file as per Src/sample_config.ini

Using base64 encoded secrets to configure account info

```ini
[Account]
# Bank login info (more secured way to be implemented)

username = <base64encrypted(username)>
memorable = <base64encrypted(memorable sentence)>
secret2 = <base64encrypted(second password)>
accounts = <account_number1>,<account_number2>,...
```

Specify the location of your chromedriver in the config file

```ini
[Paths.os]
# paths config for linux

# Driver path
   driver_path = <path_to>/chromedriver
   # chrome path can be empty if bin in $PATH
   chrome_path = <path_to>/chrome
```

Change the location where you want to save statements still in the config file

```ini
[Paths.Linux]
# paths config for linux
# File download location
   FILE_DIR = <path_to>/files
```

Set issue dates for credit card and statement

```ini
[IssueDate]
credit_card = 12
statement = 26
```
## Usage

To download all statements (both credit and debit card) from your account:

```
  Python AutoDownload.py -c <config_file> -a -t cd
```

If you just want to download current monthly credit card statement,

```
  Python AutoDownload.py -c <config_file> -d -t c
```

To retrieve a specific monthly debit card statement, you can type (currently, HSBC only stores the latest 24 months' statements for their client):

```
Python AutoDownload.py -c <config_file> -m Mon-YYYY -t d(e.g., Python AutoDownload.py -m Jun-2016)
```

New:

-Download type setting

```
 Syntax
    [-t type]

 Flags
    Item
          Description
    -t    type
          specify download type for credit and/or debit card statement. ("c" for credit card, "d" for debit card)
          for example,
          -t cd (download both credit and debit card statement)
          -t c (only download credit card statement)
```
