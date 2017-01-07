import time
import sys, getopt, Scraper
from datetime import date

def month_digit_to_string(value):
    switcher = {
        1: "Mon",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
       10: "Oct",
       11: "Nov",
       12: "Dec"
    }
    return switcher.get(value, "Error")

def main(argv):
    crdr_type = ''
    type = ''
    month_year_str = ''
    day = 0
    try:
        opts, args = getopt.getopt(argv, "hdam:t:", ["month="])
    except getopt.GetoptError:
        print('test.py -a' + '\n' + 'test.py -m [month]' + '\n')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('[Usage]' + '\n' + 'test.py -a' )
            sys.exit()
        elif opt in ("-m", "--month"):
            type = 'm'
            month_year_str = arg
        elif opt == '-d':
            type = 'd'
            month = date.today().month
            year = date.today().year
            day = int(date.today().day)
            month_year_str = month_digit_to_string(month) + '-' + str(year)
        elif opt == '-a':
            type = 'a'
        elif opt == '-t':
            crdr_type = arg

    Scraper.download(type, month_year_str, day, crdr_type)


if __name__ == "__main__":
    main(sys.argv[1:])
