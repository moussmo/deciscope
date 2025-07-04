import smtplib
import logging
import logging_config
from email.message import EmailMessage
import ssl
from email.utils import formataddr
from utils.utils import get_today, get_secrets
from writer.writer import Writer
from looker.cassation_looker import CassationLooker
from looker.ce_looker import CELooker

def make_mail( subject, mail_body, email_sender, email_receiver):    
    email = EmailMessage()
    email['From']= formataddr(('Déciscope', email_sender))
    email['To'] = email_receiver
    email['Subject'] = subject
    email.add_alternative(mail_body, subtype="html")
    return email

if __name__=='__main__':
    logging.info("Main program started")

    secrets = get_secrets()
    email_sender = secrets['EMAIL_SENDER']
    email_password = secrets['EMAIL_PASSWORD']
    email_receivers = secrets['EMAIL_RECEIVERS']
    email_receivers = email_receivers.split(';')
    client_id = secrets['CLIENT_ID']
    client_secret = secrets['CLIENT_SECRET']

    logging.info("Main program started")
    logging.info("Launching lookers and writers")

    writer = Writer()
    cassation_default = False
    ce_default = False

    cassation_looker = CassationLooker(client_id, client_secret)
    try:
        cassation_decisions = cassation_looker.look_for_decisions()
        cassation_mailbody = writer.write_mail_body(cassation_decisions, "la cour de Cassation")
    except Exception as e:
        cassation_default = True
        cassation_mailbody = writer.get_default_mailbody("la cour de Cassation")
        logging.info("Cassation module error : {}".format(e))
    cassation_subject = 'Déciscope Cour de Cassation - {}'.format(get_today())
    cassation_mails = []
    for email_receiver in email_receivers:
        cassation_mails.append((email_receiver.strip(), make_mail(cassation_subject, cassation_mailbody, email_sender, email_receiver)))
    
    ce_looker = CELooker()
    try:
        ce_decisions = ce_looker.look_for_decisions()
        ce_mailbody = writer.write_mail_body(ce_decisions, "le Conseil D'État")
    except Exception as e:
        ce_default = True
        ce_mailbody = writer.get_default_mailbody("le Conseil D'État")
        logging.info("CE module error : {}".format(e))
    ce_subject = "Déciscope Conseil D'État - {}".format(get_today())
    ce_mails = []
    for email_receiver in email_receivers:
        ce_mails.append((email_receiver, make_mail(ce_subject, ce_mailbody, email_sender, email_receiver)))

    logging.info("Launching mail senders")
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        logging.info("Logged into email account successfully")

        for email_receiver, cassation_mail in cassation_mails:
            smtp.sendmail(email_sender, email_receiver, cassation_mail.as_string())
        logging.info("Sent Cassation mails successfully")

        for email_receiver, ce_mail in ce_mails:
            smtp.sendmail(email_sender, email_receiver, ce_mail.as_string())
        logging.info("Sent CE mail")
    
    if not cassation_default:
        cassation_looker.save_history()
    if not ce_default:
            ce_looker.save_history()

    
