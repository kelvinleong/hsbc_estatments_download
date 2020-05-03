import time
import sys, getopt, Scraper
import configparser
from datetime import date
from pathlib import Path
import logging


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
    print(
        '[Usage]:\n'
        + 'python3 DownloadStatement.py -c <config.file> -t (c|d|cd) (-d | -m [mon-yyyy] | -a)' + '\n'
    )


def main(argv):
    logging.basicConfig(
        filename='AutoDownload.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s:%(message)s'
    )
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    rootlogger = logging.getLogger('AutoDownload')
    logger = logging.getLogger('AutoDownload.main')
    logger.info("*** START ***")
    logger.info("command args: [%s]", " ".join(argv))

    try:
        current_month = date.today().month
        current_year = date.today().year
        current_day = 0
        month_year_str = '{!s}-{!s}'.format(month_digit_to_string(current_month), str(current_year))

        cfgstr = "config.ini"
        card_type = 'cd'
        statement_issued_time = 'd'
        security_mode = False

        try:
            opts, args = getopt.getopt(argv, "hdasc:m:t:", ["month="])
        except getopt.GetoptError:
            logger.exception("usage error")
            print_usage()
            sys.exit(2)

        for opt, arg in opts:
            if opt == '-h':
                print_usage()
                sys.exit()
            elif opt == '-c':
                cfgstr = arg
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
                logger.error("invalid argument [%s]", opt)
                return

        cfg_path = Path(cfgstr)
        if not cfg_path.is_file():
            print("missing config file")
            logger.error("missing config file (%s)", str(cfg_path))
            return
        cfg = configparser.ConfigParser()
        cfg.read(str(cfg_path))

        new_log_level = logging.getLevelName(cfg['Log']['level'])
        logging.getLogger('AutoDownloads').setLevel(new_log_level)
        console.setLevel(new_log_level)
        logger.info("log level is %s", logger.getEffectiveLevel())
        scraper = Scraper.Scraper(cfg)
        scraper.download(statement_issued_time, month_year_str, current_day, card_type, security_mode)
        logger.info("--- DONE ---")
    except:
        logger.exception("!!! FAILED !!!")
        sys.exit(3)
    logger.info("### END ###")


if __name__ == "__main__":
    main(sys.argv[1:])
