import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from utils.utils import get_datetime_limits, filter_decisions
from utils.constants import CE_PUBLICATION_FILTERS, CE_PUBLICATION_DICT

logger = logging.getLogger(__name__)

def _get_decision(url):
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

def _get_decisions(url, header):
    logger.info("Getting CE decisions")
    documents = requests.post(url, headers=header).json()['Documents']
    if documents.status_code!=200 :
        logger.info("GET Request to get CE decisions failed")
        raise Exception('GET Export request failed')
    
    decision_url = "https://www.conseil-etat.fr/fr/arianeweb/CE/decision/{}/{}"
    decisions = []
    for document in documents:
        decision_publication = document["SourceTree2"][-2:-1]
        if decision_publication not in CE_PUBLICATION_FILTERS:
            continue
        decision_id = document['SourceCsv1'].split(';')[0]
        decision_chamber = document["SourceStr7"]
        decision_datetime =  datetime.strptime(document["SourceDateTime1"], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        decision_date = decision_datetime[:10]
        decision_link = decision_url.format(decision_date, decision_id)
        decision_text = _get_decision(decision_link)
        decision = {"id": decision_id,
                    "cour" : "Conseil d'Etat",
                    "decision_date" : decision_date,
                    "decision_datetime" : decision_datetime,
                    "decision_chamber" : decision_chamber,
                    "decision_publication": CE_PUBLICATION_DICT[decision_publication],
                    "decision_link" : decision_link,
                    "text": decision_text
                    }
        decisions.append(decision)
        logger.info("Added Decision {} into the list".format(decision['decision_link']))
    return decisions

def look_ce_decisions():
    logger.info("CE looker launched")
    url = "https://www.conseil-etat.fr/xsearch?advanced=1&type=json&SourceStr4=AW_DCE&text.add=&synonyms=true&scmode=smart&SkipCount=50&SkipFrom=0&sort=SourceDateTime1.desc,SourceStr5.desc"
    header = {"content-type":"application/json"}

    start_datetime, end_datetime = get_datetime_limits()

    decisions = _get_decisions(url, header)
    filtered_decisions = filter_decisions(decisions, start_datetime, end_datetime)

    return filtered_decisions
