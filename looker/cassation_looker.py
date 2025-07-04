import logging
import requests
from utils.utils import get_piste_header
from looker.looker import Looker

logger = logging.getLogger("CASSATION-LOOKER")

class CassationLooker(Looker):
    CASSATION_PUBLICATION_FILTERS = ['r', 'c', 'b']
    CASSATION_PUBLICATION_DICT = {'b': 'Bulletin',
                                  'r' : 'Rapport',
                                  'l' : 'Lettres de chambre',
                                  'c' : 'Communiqué'}

    def __init__(self, client_id, client_secret):
        super().__init__("cassation")
        self.client_id = client_id
        self.client_secret = client_secret

    def _reduce_decisions(self, decisions):
        logger.info("Reducing Cassation Decisions")
        reduced_decisions = []
        for decision in decisions : 
            reduced_decision = {}
            reduced_decision["id"] = decision['id']
            reduced_decision['cour'] = "Cour de Cassation"
            reduced_decision["decision_date"] = decision['decision_date']
            reduced_decision["decision_datetime"] = decision['decision_datetime']
            reduced_decision["decision_chamber"] = decision['chamber']
            reduced_decision["decision_publication"] = ', '.join([self.CASSATION_PUBLICATION_DICT[p] for p in decision['publication']])
            reduced_decision["decision_link"] = "https://www.courdecassation.fr/decision/{}".format(decision['id'])
            reduced_decision["text"] = decision['text']
            reduced_decisions.append(reduced_decision)
            logger.info("Added Decision {} to the list".format(reduced_decision['decision_link']))
        return reduced_decisions

    def _get_decisions(self, endpoint, header):
        logger.info("Getting Cassation decisions")
        url = endpoint + 'export'
        decisions_request = requests.get(url, params={'batch': 0, 'batch_size' : 100, 'order':'desc','publication': self.CASSATION_PUBLICATION_FILTERS}, headers= header)
        if decisions_request.status_code!=200:
            logger.info("GET Request to get Cassation decisions failed, error code : {}".format(decisions_request.status_code))
            raise Exception('GET Export request failed')
        return decisions_request.json()['results']

    def _sort_decisions(self, decisions):
        return decisions
    
    def look_for_decisions(self):
        logger.info("Cassation looker launched")

        url = 'https://api.piste.gouv.fr/cassation/judilibre/v1.0/'
        header = get_piste_header(self.client_id, self.client_secret)

        decisions = self._get_decisions(url, header)
        filtered_decisions = self._filter_decisions(decisions)
        reduced_decisions = self._reduce_decisions(filtered_decisions)
        sorted_decisions = self._sort_decisions(reduced_decisions)

        return sorted_decisions
    