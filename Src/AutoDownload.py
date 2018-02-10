import time
import sys, getopt, Scraper
from datetime import date


def month_digit_to_string(value):
    switcher = {
        1: "Jan",
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


def print_usage():
    print('[Usage]:' + '\n' + 'python3 DownloadStatement.py -t [c/d/cd] -d -m [mon-yyyy] -s -a' + '\n')


def main(argv):
    current_month = date.today().month
    current_year = date.today().year
    current_day = 0
    month_year_str = '{!s}-{!s}'.format(month_digit_to_string(current_month), str(current_year))

    card_type = 'cd'
    statement_issued_time = 'd'
    security_mode = False

    try:
        opts, args = getopt.getopt(argv, "hdasm:t:", ["month="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt == "-m":
            statement_issued_time = 'm'
            month_year_str = arg
        elif opt == '-d':
            statement_issued_time = 'd'
            current_day = int(date.today().day)
        elif opt == '-a':
            statement_issued_time = 'a'
        elif opt == '-t':
            card_type = arg
        elif opt == '-s':
            security_mode = True
        else:
            print("Invalid arguments!")
            return;

    scraper = Scraper.Scraper()
    scraper.download(statement_issued_time, month_year_str, current_day, card_type, security_mode)

if __name__ == "__main__":
    main(sys.argv[1:])