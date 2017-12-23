#!/usr/bin/env python
"""
Check hashrate of each worker
"""
import urllib2
import json
import smtplib
from email.mime.text import MIMEText


def send_email(subject, text):
    me = 'Jingshao'
    to = 'jingshaochen@gmail.com'
    msg = MIMEText(text)
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = to
    s = smtplib.SMTP('localhost')
    s.sendmail(me, [to], msg.as_string())
    s.quit()
    print "sent mail"


def main():
    """
    main function
    """
    api_url = 'https://api.nanopool.org/v1/eth/user/'
    account = '0x3b862fd6142af29f5321c0993d4bad81e5325080'
    user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46'
    req = urllib2.Request(api_url + account, data=None,
                          headers={'User-Agent': user_agent})
    connection = urllib2.urlopen(req)
    body = connection.read()
    result = json.loads(body)
    workers = result['data']['workers']
    not_working = ""
    for worker in workers:
        print '%s %s' % (worker['id'], worker['hashrate'])
        if float(worker['hashrate']) == 0:
            not_working += "worker: %s, hashrate %s\n" % (
                worker['id'], worker['hashrate'])

    if not_working:
        send_email('Work is down!!!!', not_working)
    else:
        print 'Everything is ok!!!'

if __name__ == '__main__':
    main()
