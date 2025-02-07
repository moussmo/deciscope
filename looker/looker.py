import logging
import requests
from datetime import datetime
from utils.utils import get_today, get_yesterday
from utils.constants import BUCKET_NAME
import boto3
from abc import ABC, abstractmethod

logger = logging.getLogger("UTILS")

class Looker():

    def __init__(self, court_type):
        self.court_type = court_type
        self.old_s3_history_file_name = self._get_old_s3_history_file_name()   
        self.new_s3_history_file_name = self._get_new_s3_history_file_name()   
        self.decisions_ids_to_save=[]

    def _get_old_s3_history_file_name(self):
        return "{}_history_{}.txt".format(self.court_type, get_yesterday().replace(" ", "-"))
    
    def _get_new_s3_history_file_name(self):
        return "{}_history_{}.txt".format(self.court_type, get_today().replace(" ", "-"))
    
    def _load_history(self):
        logger.info("Loading processed decisions ids")
        s3 = boto3.client("s3")
        try:
            obj = s3.get_object(Bucket=BUCKET_NAME, Key=self.s3_history_file_name)
            data = obj["Body"].read().decode("utf-8")
            return set(data.splitlines())
        except s3.exceptions.NoSuchKey:
            return set() 
        
    def _filter_decisions(self, decisions):
        logger.info("Starting filtering process - only keeping decisions that have not been sent yet")

        history_decisions_ids = self._load_history()
        current_decisions_ids = set([decision['id'] for decision in decisions])

        all_decisions_ids = current_decisions_ids.union(history_decisions_ids)
        self.decisions_ids_to_save = all_decisions_ids

        new_decisions_ids = current_decisions_ids - history_decisions_ids
        filtered_decisions = [decision for decision in decisions if decision['id'] in new_decisions_ids]
       
        logger.info("From {} decision, {} were kept".format(len(decisions), len(filtered_decisions)))
        return filtered_decisions

    def _filter_decisions_by_date(self, decisions, start_datetime, end_datetime):
        logger.info("Filtering Decisions according to date and days window")
        filtered_decisions = [decision for decision in decisions if start_datetime<=datetime.strptime(decision['decision_datetime'], '%Y-%m-%dT%H:%M:%S.%fZ')<=end_datetime]
        logger.info("From {} decision, {} were kept".format(len(decisions), len(filtered_decisions)))
        return filtered_decisions

    def save_history(self):
        logger.info("Saving new processed decisions ids")
        s3 = boto3.client("s3")
        data = "\n".join(self.decisions_ids_to_save)
        s3.put_object(Bucket=BUCKET_NAME, Key=self.s3_history_file_name, Body=data.encode("utf-8")) 

    @abstractmethod
    def _get_decisions(self):
        pass
    
    @abstractmethod
    def look_for_decisions(self):
        pass

    