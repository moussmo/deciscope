import logging
from utils.utils import gpt_request, get_today
from datetime import datetime
logger = logging.getLogger("WRITER")

def _prep_decision_text(decision, cour_type):
    decision_date = datetime.strptime(decision['decision_date'], "%Y-%m-%d").strftime("%d %B %Y")
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
        <span style="color: teal;"> <b>Date</b> </span> : {}<br>
        <span style="color: teal;"> <b>Chambre</b> </span> : {}<br>
        <span style="color: teal;"> <b>Lien</b> </span> : {}<br>
        <span style="color: teal;"> <b>Publication</b> </span> : {}<br>
        <span style="color: teal;"> <b>Résumé</b> </span>  : {} <br>
        <span style="color: teal;"> <b>Proposition LinkedIn</b> </span>  : {}<br>
    """.format(decision_date, decision_chamber, decision_link, decision_publication, decision_summary, decision_linkedin)
    return html_decision_body

def write_mail_body(decisions, cour_type):
    logger.info("Started writing mail body for {}".format(cour_type))
    today_date = get_today()
    html_body = """
        <html>
            <head></head>
            <body>
                <h1>Déciscope {} - {}</h1>
    """.format(cour_type[3:], today_date)

    if len(decisions)==0:
        html_body += """
            Hier, <b>aucune</b> importante décision juridique n'a été rendue par {}.
            <br>
            <br>
        """.format(cour_type)
    elif len(decisions)==1:
        html_body += """
            Hier, <b>1</b> importante décision juridique a été rendue par {}. Veuillez la-découvrir ci-dessous dans cette nouvelle édition de Déciscope : 
            <br>
            <br>
        """.format(cour_type)
    else :
        html_body += """
                Hier, {} importantes décisions juridiques ont été rendues par {}. Veuillez les-découvrir ci-dessous dans cette nouvelle édition de Déciscope : 
                <br>
                <br>
        """.format(len(decisions), cour_type)
        
    for decision in decisions:
        html_body += """
            <div>
            <hr style="border: 1px solid black;" />
        """
        html_decision_body = _prep_decision_text(decision, cour_type)
        html_body = html_body + html_decision_body
        html_body += """
            </div>
        """
        logger.info("Injected Decision {} into the mail body".format(decision['decision_link']))
    html_body += """    
        </body>
    </html>"""
    return html_body