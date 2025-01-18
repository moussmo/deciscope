import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from utils.utils import gpt_summarize_decision
from utils.constants import DECISION_DELIMITER, CE_PUBLICATION_DICT

def _prep_decision_text(decision):
    decision_date = decision['decision_date']
    decision_link = decision['decision_link']
    decision_publication = ', '.join([CE_PUBLICATION_DICT[p] for p in decision['publication']])
    decision_text = gpt_summarize_decision(decision['text'])
    email_text = "{}\n\n{}\nPublication : {}\n{}\n\n{}\n\n".format(DECISION_DELIMITER, decision_date, decision_publication, decision_link, decision_text)
    return email_text

def write_ce_mail_body(decisions):
    mail_body = ""
    for decision in decisions:
        decision_text = _prep_decision_text(decision)
        mail_body = mail_body + decision_text
    return 