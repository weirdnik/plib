#! /usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib, re

from email.MIMEText import MIMEText
from email.Header import Header
from time import gmtime, strftime

FROM_ADDR = 'Plan B <blip@hell.pl>'
TEMPLATE = '''Aby potwierdzić utworzenie konta kliknij w poniższy odnośnik:

%s

Jesli nie rejestrowałes/aś się w Planie B, to ktoś uzył Twojego adresu,
żeby to zrobić. W takim wypadku mozesz zignorować niniejsza wiadomosc.

Załoga Planu B
'''


def sendmail(recipient, message):

  def envelope(addr):
    emailre = re.compile('<(.+@.+)>')
    return emailre.search(addr).group().strip('<>')
    
  message = MIMEText(message,'plain', 'UTF-8')
  message['From'] = FROM_ADDR
  message['To'] = recipient
  message['Priority'] = 'normal'
  message['X-Mailer'] = 'Plan B'
  message['Message-ID'] = '<%s-planb@hell>' % strftime("%S%M%H%d%m%Y", gmtime())
  message['Date'] = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
  message['Subject'] = Header(u'Potwierdź utworzenie konta w #nowyblip', 'utf-8')
                          
  smtp = smtplib.SMTP()
  smtp.connect()
  smtp.sendmail(envelope(FROM_ADDR), recipient, message.as_string())
  smtp.close()


def confirm (recipient, message):
  sendmail (recipient, TEMPLATE % message)
      