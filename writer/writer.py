import logging
from utils.utils import gpt_request, get_today
from datetime import datetime
logger = logging.getLogger("WRITER")

class Writer():
    def __init__(self):
        pass

    def _prep_decision_text(self, decision, court_type):
        decision_date = datetime.strptime(decision['decision_date'], "%Y-%m-%d").strftime("%d %B %Y")
        decision_link = decision['decision_link']
        decision_chamber = decision['decision_chamber']
        decision_publication = decision['decision_publication']
        decision_summary = gpt_request(request_text=decision['text'], 
                                       request_type="summarization", 
                                       cour_type=court_type)
        decision_linkedin = gpt_request(request_text=decision_summary, 
                                        request_type="linkedin", 
                                        cour_type=court_type)
        html_decision_body = """ 
            <span style="color: teal;"> <b>Date</b> </span> : {}<br>
            <span style="color: teal;"> <b>Chambre</b> </span> : {}<br>
            <span style="color: teal;"> <b>Lien</b> </span> : {}<br>
            <span style="color: teal;"> <b>Publication</b> </span> : {}<br>
            <span style="color: teal;"> <b>Résumé</b> </span>  : {} <br>
            <span style="color: teal;"> <b>Proposition LinkedIn</b> </span>  : {}<br>
        """.format(decision_date, decision_chamber, decision_link, decision_publication, decision_summary, decision_linkedin)
        return html_decision_body

    def write_mail_body(self, decisions, court_type):
        logger.info("Started writing mail body for {}".format(court_type))
        today_date = get_today()
        html_body = """
            <html>
                <head></head>
                <body>
                    <h1>Déciscope {} - {}</h1>
        """.format(court_type[3:], today_date)

        if len(decisions)==0:
            html_body += """
                Hier, <b>aucune</b> importante décision juridique n'a été rendue par {}.
                <br>
                <br>
            """.format(court_type)
        elif len(decisions)==1:
            html_body += """
                Hier, <b>1</b> importante décision juridique a été rendue par {}. Veuillez la-découvrir ci-dessous dans cette nouvelle édition de Déciscope : 
                <br>
                <br>
            """.format(court_type)
        else :
            html_body += """
                    Hier, {} importantes décisions juridiques ont été rendues par {}. Veuillez les-découvrir ci-dessous dans cette nouvelle édition de Déciscope : 
                    <br>
                    <br>
            """.format(len(decisions), court_type)
            
        for decision in decisions:
            html_body += """
                <div>
                <hr style="border: 1px solid black;" />
            """
            html_decision_body = self._prep_decision_text(decision, court_type)
            html_body = html_body + html_decision_body
            html_body += """
                </div>
            """
            logger.info("Injected Decision {} into the mail body".format(decision['decision_link']))
        html_body += """    
            </body>
        </html>"""
        return html_body
    
    def get_default_mailbody(self, court_type):
        return "Désolé, une erreur inattendue est survenue lors du lancement du module de "" de Déciscope.".format(court_type)