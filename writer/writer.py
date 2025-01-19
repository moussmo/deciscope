import logging
from utils.utils import gpt_request, get_today

logger = logging.getLogger("WRITER")

def _prep_decision_text(decision, cour_type):
    decision_date = decision['decision_date']
    decision_link = decision['decision_link']
    decision_chamber = decision['decision_chamber']
    decision_publication = decision['decision_publication']
    decision_summary = gpt_request(request_text=decision['text'], 
                                   request_type="summarization", 
                                   cour_type=cour_type)
    decision_linkedin = gpt_request(request_text=decision_summary, 
                                    request_type="linkedin", 
                                    cour_type=cour_type)
    html_decision_body = """ 
        <b>Date</b> : {}<br>
        <b>Chambre</b> : {}<br>
        <b>Lien</b> : {}<br>
        <b>Publication</b> : {}
        <br>
        <br>
        <b>Résumé</b> : {} 
        <br>
        <br>
        <b>Proposition LinkedIn</b> : {}
    """.format(decision_date, decision_chamber, decision_link, decision_publication, decision_summary, decision_linkedin)
    return html_decision_body

def write_mail_body(decisions, cour_type):
    logger.info("Started writing mail body for {}".format(cour_type))
    cour_type = "Conseil d'État" if cour_type.lower() == "ce" else "Cour de Cassation"
    today_date = get_today()
    html_body = """
        <html>
            <head></head>
            <body>
                <h1>Déciscope {} - {}</h1>
                <div style="height: 40px;"></div>
    """.format(cour_type, today_date)
    for decision in decisions:
        html_body += """
            <div>
            <hr style="border: 1px solid black;" />
            <br>
        """
        html_decision_body = _prep_decision_text(decision, cour_type)
        html_body = html_body + html_decision_body
        html_body += """
            <br>
            </div>
        """
        logger.info("Injected Decision {} into the mail body".format(decision['decision_link']))
    html_body += """    
        </body>
    </html>"""
    return html_body