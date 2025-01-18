import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.message import EmailMessage
import ssl
from email.utils import formataddr
from utils.constants import EMAIL_SENDER, EMAIL_RECEIVER, EMAIL_PASSWORD
from utils.utils import get_today
from looker.cassation_looker import look_cassation_decisions
from writer.cassation_writer import write_cassation_mail_body
from looker.ce_looker import look_ce_decisions
from writer.ce_writer import write_ce_mail_body


def get_cassation_mail():
    subject = 'Déciscope CASSATION - {}'.format(get_today())

    cassation_decisions = look_cassation_decisions()
    cassation_mail_body = write_cassation_mail_body(cassation_decisions)

    email = EmailMessage()
    email['From']= formataddr(('Déciscope', EMAIL_SENDER))
    email['To'] = EMAIL_RECEIVER
    email['Subject'] = subject
    email.set_content(cassation_mail_body)

    return email
 
def get_ce_mail():
    subject = "Déciscope CONSEIL D'ETAT - {}".format(get_today())

    ce_decisions = look_ce_decisions()
    ce_mail_body = write_ce_mail_body(ce_decisions)

    email = EmailMessage()
    email['From']= formataddr(('Déciscope', EMAIL_SENDER))
    email['To'] = EMAIL_RECEIVER
    email['Subject'] = subject
    email.set_content(ce_mail_body)

    return email

if __name__=='__main__':
    cassation_mail = get_cassation_mail()
    ce_mail = get_ce_mail()

    context = ssl.create_default_context()
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)

        smtp.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, cassation_mail.as_string())
        print("CASSATION EMAIL ENVOYE")

        smtp.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, ce_mail.as_string())
        print("CE EMAIL ENVOYE")

    