import requests
from utils.utils import get_header, get_datetime_limits
from datetime import datetime
from utils.constants import PUBLICATION_FILTERS

def _get_decisions(endpoint, header):
    url = endpoint + 'export'
    decisions_request = requests.get(url, params={'batch': 0, 'batch_size' : 100, 'publication': PUBLICATION_FILTERS}, headers= header)
    if decisions_request.status_code!=200:
        raise Exception('GET Export request failed')
    
    return decisions_request.json()['results']

def _filter_decisions(decisions, start_datetime, end_datetime):
    filtered_decisions = [decision for decision in decisions if start_datetime<=datetime.strptime(decision['decision_datetime'], '%Y-%m-%dT%H:%M:%S.%fZ')<=end_datetime]
    return filtered_decisions

def _reduce_decisions(decisions):
    return decisions

def look_cassation_decisions():
    endpoint = 'https://sandbox-api.piste.gouv.fr/cassation/judilibre/v1.0/'
    header = get_header()
    start_datetime, end_datetime = get_datetime_limits()

    decisions = _get_decisions(endpoint, header)
    filtered_decisions = _filter_decisions(decisions, start_datetime, end_datetime)
    reduced_decisions = _reduce_decisions(filtered_decisions)

    return reduced_decisions
