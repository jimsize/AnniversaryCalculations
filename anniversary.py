#!/usr/bin/env python3


import configparser
import datetime
import os.path
import smtplib


def message():
    """Create the "anniversary" text message.

    This calculates the number of days, weeks, and months since Annelies
    and Jim were married.

    Other functions in this module deliver this message.
    """
    today=datetime.date.today()
    wedding=datetime.date(2004, 5, 1)

    # Calculate Days
    days = (today-wedding).days

    # Calculate Weeks
    saturday = today + datetime.timedelta( (5-today.weekday()) % 7 )
    weeks = ((saturday-wedding).days // 7)

    # Calculate Months
    if today.day == 1: 
        first_of_month = today
    else:
        next_month = today.month + 1
        next_months_year = today.year
        if next_month==13: 
            next_month = 1
            next_months_year += 1
        first_of_month = today.replace(year=next_months_year, month=next_month, day=1)
    months = (first_of_month.year - wedding.year) * 12 + (first_of_month.month - 5)

    # Output
    format = "%A, %B %d, %Y"
    message = "Annelies and Jim were married on %s.\r\n" % wedding.strftime(format)
    message = message + "Today is %s.\r\n" % today.strftime(format)
    message = message + "We have been married for %s days.\r\n" % days
    message = message + "On %s, it will have been %s weeks since the wedding.\r\n" % (saturday.strftime(format), weeks)
    message = message + "On %s, it will have been %s months since the wedding.\r\n" % (first_of_month.strftime(format), months)
    return message


def send_email(fromaddr, toaddrs, smtp, message):
    # add headers to the start of the message
    headers = "Date: %s\r\n" % datetime.datetime.now().strftime("%a, %b %d, %Y at %I:%M %p")
    headers = headers + "From: %s\r\n" % fromaddr
    headers = headers + "Subject: Anniversary Calculations\r\n"
    headers = headers + "To: %s\r\n" % ", ".join(toaddrs)
    headers = headers + "\r\n" # null line to indicate end of the headers

    server = smtplib.SMTP(smtp['host'], port=smtp.getint('port'))
    server.set_debuglevel(1)
    server.login(smtp['username'], smtp['password'])
    server.sendmail(fromaddr, toaddrs, headers + message)
    server.quit()


if __name__=='__main__':
    import sys
    from optparse import OptionParser

    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-e", "--email", 
            action="store_true", dest="email",
            help="send anniversary calculations by email")
    parser.add_option("-p", "--print", 
            action="store_true", dest="stdout",
            help="print anniversary calculations to stdout")

    if not sys.argv[1:]:
        parser.print_help()
        sys.exit()

    options, args = parser.parse_args()

    message = message()
    if options.stdout:
        print(message)

    if options.email:
        thisdir = os.path.abspath(os.path.dirname(__file__))
        config = configparser.ConfigParser()
        config.read(os.path.join(thisdir, 'anniversary.cfg'))

        send_email(config['email']['fromaddr'].strip(),
                config['email']['toaddrs'].split(),
                config['smtp'],
                message)
