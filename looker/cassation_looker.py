import logging
import requests
from utils.utils import get_piste_header, get_datetime_limits, filter_decisions
from utils.constants import CASSATION_PUBLICATION_FILTERS, CASSATION_PUBLICATION_DICT

logger = logging.getLogger(__name__)

def _get_decisions(endpoint, header):
    logger.info("Getting Cassation decisions")
    url = endpoint + 'export'
    decisions_request = requests.get(url, params={'batch': 0, 'batch_size' : 100, 'publication': CASSATION_PUBLICATION_FILTERS}, headers= header)
    if decisions_request.status_code!=200:
        logger.info("GET Request to get Cassation decisions failed")
        raise Exception('GET Export request failed')
    return decisions_request.json()['results']

def _reduce_cassation_decisions(decisions):
    logger.info("Reducing Cassation Decisions")
    reduced_decisions = []
    for decision in decisions : 
        reduced_decision = {}
        reduced_decision["id"] = decision['id']
        reduced_decision['cour'] = "Cour de Cassation"
        reduced_decision["decision_date"] = decision['decision_date']
        reduced_decision["decision_datetime"] = decision['decision_datetime']
        reduced_decision["decision_chamber"] = decision['chamber']
        reduced_decision["decision_publication"] = ', '.join([CASSATION_PUBLICATION_DICT[p] for p in decision['publication']])
        reduced_decision["decision_link"] = "https://www.courdecassation.fr/decision/{}".format(decision['id'])
        reduced_decision["text"] = decision['text']
        reduced_decisions.append(reduced_decision)
        logger.info("Added Decision {} into the list".format(reduced_decision['decision_link']))
    return reduced_decisions

def _sort_decisions(decisions):
    pass

def look_cassation_decisions():
    logger.info("Cassation looker launched")

    endpoint = 'https://sandbox-api.piste.gouv.fr/cassation/judilibre/v1.0/'
    header = get_piste_header()
    start_datetime, end_datetime = get_datetime_limits()

    decisions = _get_decisions(endpoint, header)
    filtered_decisions = filter_decisions(decisions, start_datetime, end_datetime)
    reduced_decisions = _reduce_cassation_decisions(filtered_decisions)

    return reduced_decisions
