import logging
import requests
from datetime import datetime, time, timedelta, date
from utils.constants import DAYS_WINDOW, API_KEY
from openai import OpenAI

logger = logging.getLogger(__name__)

def get_piste_header():
    url = 'https://sandbox-oauth.piste.gouv.fr/api/oauth/token'
    post_request = requests.post(url, data={"grant_type":"client_credentials", "client_id":"69021959-e7d7-4faf-bc79-04bc3fed3bc3", 
                                            "client_secret":"3c7b3ad7-169c-43d9-b9ea-a4f03394c61d", "scope":"openid"},
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'})
    if post_request.status_code!=200:
        raise Exception('Token was not retrieved, post request failed')
    
    token = post_request.json()['access_token']
    header = {'accept': 'application/json',
              'Authorization': 'Bearer {}'.format(token)}
    
    logger.info("PISTE API token acquired")
    return header

def get_today():
    today = date.today()
    logger.info("Today is : {}".format(today))
    return today 

def get_datetime_limits():
    current_date = datetime.now().date()
    one_day_ago = current_date - timedelta(days=DAYS_WINDOW)
    time_point = time(11, 0, 0)
    min_datetime = datetime.combine(one_day_ago, time_point)
    max_datetime = datetime.combine(current_date, time_point)
    logger.info("Start and end datetime chosen : {} to {}".format(min_datetime, max_datetime))
    return [min_datetime, max_datetime]


def gpt_summarize_decision(decision_text, cour_type):
    client = OpenAI(
        api_key=API_KEY
        )
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    store=True,
    messages=[
        {"role": "user", "content": " Résume-moi les points de droit tranchés par la {} dans la décision suivante : »): {}".format(cour_type, decision_text)}
    ]
    )
    return completion.choices[0].message.content

def gpt_generate_linkedin_post(decision_summary):
    client = OpenAI(
        api_key=API_KEY
        )
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    store=True,
    messages=[
        {"role": "user", "content": " « Transforme-moi ce résumé en post linkedin (je suis avocat et m'adresse à d'autres avocats et clients intéressés par le sujet) : {}»".format(decision_summary)}
    ]
    )
    return completion.choices[0].message.content

def filter_decisions(decisions, start_datetime, end_datetime):
    logger.info("Filtering Decisions according to date and days window")
    filtered_decisions = [decision for decision in decisions if start_datetime<=datetime.strptime(decision['decision_datetime'], '%Y-%m-%dT%H:%M:%S.%fZ')<=end_datetime]
    return filtered_decisions
