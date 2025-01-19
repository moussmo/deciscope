import smtplib
import logging_config
import logging
from email.message import EmailMessage
import ssl
from email.utils import formataddr
from utils.constants import EMAIL_SENDER, EMAIL_RECEIVER, EMAIL_PASSWORD
from utils.utils import get_today
from looker.cassation_looker import look_cassation_decisions
from looker.ce_looker import look_ce_decisions
from writer.writer import write_mail_body


def get_cassation_mail():
    cassation_decisions = look_cassation_decisions()
    cassation_mail_body = write_mail_body(cassation_decisions, "cassation")

    subject = 'Déciscope Cour de Cassation - {}'.format(get_today())
    email = EmailMessage()
    email['From']= formataddr(('Déciscope', EMAIL_SENDER))
    email['To'] = EMAIL_RECEIVER
    email['Subject'] = subject
    email.add_alternative(cassation_mail_body, subtype="html")

    return email
 
def get_ce_mail():
    ce_decisions = look_ce_decisions()
    ce_mail_body = write_mail_body(ce_decisions, "ce")

    subject = "Déciscope Conseil D'État - {}".format(get_today())
    email = EmailMessage()
    email['From']= formataddr(('Déciscope', EMAIL_SENDER))
    email['To'] = EMAIL_RECEIVER
    email['Subject'] = subject
    email.add_alternative(ce_mail_body, subtype="html")

    return email

if __name__=='__main__':
    logging.info("Main program started")
    logging.info("Launching lookers and writers")

    cassation_mail = get_cassation_mail()
    ce_mail = get_ce_mail()
    context = ssl.create_default_context()
    
    logging.info("Launching mail senders")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        logging.info("Logged into email account successfully")

        smtp.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, cassation_mail.as_string())
        logging.info("Sent Cassation mail")

        # Sending CE mail
        smtp.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, ce_mail.as_string())
        logging.info("Sent CE mail")

    logging.info("Main program over")

    