import requests
from utils.utils import get_piste_header, get_datetime_limits, filter_decisions
from datetime import datetime
from utils.constants import CASSATION_PUBLICATION_FILTERS

def _get_decisions(endpoint, header):
    url = endpoint + 'export'
    decisions_request = requests.get(url, params={'batch': 0, 'batch_size' : 100, 'publication': CASSATION_PUBLICATION_FILTERS}, headers= header)
    if decisions_request.status_code!=200:
        raise Exception('GET Export request failed')
    
    return decisions_request.json()['results']

def look_cassation_decisions():
    endpoint = 'https://sandbox-api.piste.gouv.fr/cassation/judilibre/v1.0/'
    header = get_piste_header()
    start_datetime, end_datetime = get_datetime_limits()

    decisions = _get_decisions(endpoint, header)
    filtered_decisions = filter_decisions(decisions, start_datetime, end_datetime)

    return filtered_decisions
