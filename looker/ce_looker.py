import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from looker.looker import Looker

logger = logging.getLogger("CE-LOOKER")

class CELooker(Looker):
    CE_PUBLICATION_FILTERS = ['A', 'B']
    CE_PUBLICATION_DICT = {"A" : "Recueil Lebon",
                           "B" : "Mentionné dans les tables",
                           "R" : "Non publié mais présentant un intérêt majeur",
                           "C" : "Non publiée et dont l'intérêt particulier"}

    def __init__(self):
        super().__init__("ce")

    def _get_decision(self, url):
        decision = requests.get(url)
        if decision.status_code!=200:
            return ""
        decision_content = decision.content
        decision_soup = BeautifulSoup(decision_content, "html.parser")
        try : 
            decision_text = decision_soup.find("div", class_="ezrichtext-field").get_text()
        except:
            decision_text = "DECISION TEXT NOT RETRIEVED CORRECTLY, CHECK LINK OR CONTACT ADMIN"
            logger.info("Decision text not retrieved for this URL")
        return decision_text

    def _get_decisions(self, url, header):
        logger.info("Getting CE decisions")
        response = requests.post(url, headers=header)
        if response.status_code!=200 :
            logger.info("GET Request to get CE decisions failed")
            raise Exception('GET Export request failed')
        documents = response.json()['Documents']

        decision_url = "https://www.conseil-etat.fr/fr/arianeweb/CE/decision/{}/{}"
        decisions = []
        for document in documents:
            decision_publication = document["SourceTree2"][-2:-1]
            if decision_publication not in self.CE_PUBLICATION_FILTERS:
                continue
            decision_id = document['SourceCsv1'].split(';')[0]
            decision_chamber = document["SourceStr7"]
            decision_datetime =  datetime.strptime(document["SourceDateTime1"], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            decision_date = decision_datetime[:10]
            decision_link = decision_url.format(decision_date, decision_id)
            decision_text = self._get_decision(decision_link)
            decision = {"id": decision_id,
                        "cour" : "Conseil d'Etat",
                        "decision_date" : decision_date,
                        "decision_datetime" : decision_datetime,
                        "decision_chamber" : decision_chamber,
                        "decision_publication": self.CE_PUBLICATION_DICT[decision_publication],
                        "decision_link" : decision_link,
                        "text": decision_text
                        }
            decisions.append(decision)
            logger.info("Added Decision {} into the unfiltered list".format(decision['decision_link']))
        return decisions

    def look_for_decisions(self):
        logger.info("CE looker launched")
        url = "https://www.conseil-etat.fr/xsearch?advanced=1&type=json&SourceStr4=AW_DCE&text.add=&synonyms=true&scmode=smart&SkipCount=50&SkipFrom=0&sort=SourceDateTime1.desc,SourceStr5.desc"
        header = {"content-type":"application/json"}

        decisions = self._get_decisions(url, header)
        filtered_decisions = self._filter_decisions(decisions)

        return filtered_decisions