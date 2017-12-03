#!/usr/bin/env python3


"""Calculate the number of days, weeks, and months since Annelies and Jim
were married.

This module can print the results to stdout
or send the message by email or SNS.
"""


import configparser
import datetime
import os.path
import smtplib


class Anniversary:
    def __init__(self):
        thisdir = os.path.abspath(os.path.dirname(__file__))
        config_file = os.path.join(thisdir, 'anniversary.cfg')
        self.config = configparser.ConfigParser()
        self.config.read_file(open(config_file))

    def message(self):
        """Create the "anniversary" text message.

        This calculates the number of days, weeks, and months since Annelies
        and Jim were married.

        Other functions in this module deliver this message.
        """
        event = self.config['event']
        today=datetime.date.today()
        original_date_str = event['original_date']
        wedding=datetime.datetime.strptime(original_date_str, '%Y-%m-%d').date()

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
        template = "{names} {did_this} on {original_date}.\r\n" \
        "Today is {today}.\r\n" \
        "It has been {days} days since the wedding.\r\n" \
        "On {week_date}, it will have been {weeks} weeks since the wedding.\r\n" \
        "On {month_date}, it will have been {months} months since the wedding."
        date_format = "%A, %B %d, %Y"
        format_args = {'names': event['names'],
                'did_this': event['did_this'],
                'original_date': wedding.strftime(date_format),
                'today': today.strftime(date_format),
                'days': days,
                'week_date': saturday.strftime(date_format),
                'weeks': weeks,
                'month_date': first_of_month.strftime(date_format),
                'months': months}
        message = template.format(**format_args)
        return message

    def send_email(self, message=None):
        """Send the anniversary message by email."""
        # get some values from the config
        fromaddr = self.config['email']['fromaddr'].strip()
        toaddrs = self.config['email']['toaddrs'].split()
        smtp = self.config['smtp']

        # If no message was passed in, calculate a fresh message.
        message = self.message()

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

    def send_sns(self, message=None):
        """Send anniversary message via AWS SNS."""
        import boto3

        # If no message was passed in, calculate a fresh message.
        message = self.message()

        topic_arn = self.config['sns']['topic_arn']

        sns = boto3.resource('sns')
        topic = sns.Topic(topic_arn)
        response = topic.publish(
                Subject='Anniversary Calculations',
                Message=message)
        return response


def aws_lambda_handler(event, context):
    """Calculate and send anniversary messages with AWS Lambda ."""
    anniversary = Anniversary()
    message = anniversary.message()
    sns_response = anniversary.send_sns(message)
    return {'message': message,
            'sns_response': sns_response}


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

    anniversary = Anniversary()
    message = anniversary.message()
    if options.stdout:
        print(message)

    if options.email:
        anniversary.send_email(message)
