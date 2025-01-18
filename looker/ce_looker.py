import requests
from bs4 import BeautifulSoup
from utils.utils import get_header, get_datetime_limits, filter_decisions
from datetime import datetime
from utils.constants import CASSATION_PUBLICATION_FILTERS, CE_PUBLICATION_FILTERS

def _get_decision(url):
    decision = requests.get(url).content
    decision_soup = BeautifulSoup(decision)
    decision_text = decision_soup.find("div", class_="ezrichtext-field").get_text()
    return decision_text

def _get_decisions(url, header):
    documents = requests.post(url, headers=header).json()['Documents']
    decision_url = "https://www.conseil-etat.fr/fr/arianeweb/CE/decision/{}/{}"
    decisions = []
    for document in documents:
        decision_id = document['SourceCsv1']
        decision_datetime = document["SourceDateTime1"]
        decision_publication = document["SourceTree2"]
        decision_date = decision_datetime[:10]
        decision_link = decision_url.format(decision_date, decision_id)
        decision_text = _get_decision(decision_link)
        decision = {"id": decision_id,
                    "decision_date" : decision_date,
                    "decision_datetime" : decision_datetime,
                    "publication": decision_publication[-2:-1],
                    "decision_link" : decision_link,
                    "text": decision_text
                    }
        decisions.append(decision)
    return decisions

def look_ce_decisions():
    url = "https://www.conseil-etat.fr/xsearch?advanced=1&type=json&SourceStr4=AW_DCE&text.add=&synonyms=true&scmode=smart&SkipCount=50&SkipFrom=0&sort=SourceDateTime1.desc,SourceStr5.desc"

    header = {
        "content-type":"application/json"
    }

    start_datetime, end_datetime = get_datetime_limits()

    decisions = _get_decisions(url, header)
    filtered_decisions = filter_decisions(decisions, start_datetime, end_datetime)

    return filtered_decisions
