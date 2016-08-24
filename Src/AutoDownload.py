import sys, getopt, StatementScraper
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
    type = ''
    month_year_str = ''
    try:
        opts, args = getopt.getopt(argv, "hdam:", ["month="])
    except getopt.GetoptError:
        print('AutoDownload -a' + '\n' + 'test.py -m [month]' + '\n')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('[Usage]' + '\n' + 'AutoDownload.py -a' )
            sys.exit()
        elif opt in ("-m", "--month"):
            type = 'm'
            month_year_str = arg
        elif opt == '-d':
            type = 'd'
            month = date.today().month
            year = date.today().year
            month_year_str = month_digit_to_string(month) + '-' + str(year)
        elif opt == '-a':
            type = 'a'

    StatementScraper.download(type, month_year_str)

if __name__ == "__main__":
    main(sys.argv[1:])
