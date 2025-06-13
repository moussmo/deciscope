import logging
import requests
import markdown
from datetime import datetime, time, timedelta, date
from utils.constants import DAYS_WINDOW
import openai
import json
from openai import OpenAI
import locale
import boto3

locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
logger = logging.getLogger("UTILS")

def get_piste_header(client_id, client_secret):
    logger.info("Getting PISTE API token")
    url = 'https://sandbox-oauth.piste.gouv.fr/api/oauth/token'
    post_request = requests.post(url, data={"grant_type":"client_credentials", "client_id":client_id, "client_secret": client_secret, "scope":"openid"},
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'})
    if post_request.status_code!=200:
        raise Exception('Token was not retrieved, post request failed')
    
    token = post_request.json()['access_token']
    header = {'accept': 'application/json',
              'Authorization': 'Bearer {}'.format(token)}
    
    logger.info("PISTE API token acquired")
    return header

def get_secrets():
    secret_name = "deciscope_secrets"
    region_name = "eu-north-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )
    secret = json.loads(get_secret_value_response['SecretString'])
    return secret

def get_today():
    today = date.today()
    today = today.strftime("%d %B %Y")
    return today 

def get_datetime_limits():
    current_date = datetime.now().date()
    one_day_ago = current_date - timedelta(days=DAYS_WINDOW)
    time_point = time(11, 0, 0)
    min_datetime = datetime.combine(one_day_ago, time_point)
    max_datetime = datetime.combine(current_date, time_point)
    logger.info("Start and end datetime chosen : {} to {}".format(min_datetime, max_datetime))
    return [min_datetime, max_datetime]

def gpt_request(request_text, request_type, cour_type):
    if request_type == "summarization":
        message = " Résume-moi les points de droit tranchés par {} dans la décision suivante : »): {}".format(cour_type, request_text) 
    else:
         message = "« Transforme-moi ce résumé en post linkedin (je suis avocat et m'adresse à d'autres avocats et clients intéressés par le sujet): {}»".format(request_text) 

    secrets = get_secrets()
    CHATGPT_API_KEY = secrets['CHATGPT_API_KEY']

    logger.info("Sending GPT summarization request")
    client = OpenAI(api_key=CHATGPT_API_KEY)
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[{"role": "user", "content": message}]
            )
        return markdown.markdown(completion.choices[0].message.content.replace("#", "\#"))
    except openai.error.InvalidRequestError as e:
        logging.info(f"Invalid request error: {e}")
    except openai.error.AuthenticationError as e:
        logging.info(f"Authentication error: {e}")
    except openai.error.RateLimitError as e:
        logging.info(f"Rate limit exceeded: {e}")
    except openai.error.Timeout as e:
        logging.info(f"Request timed out: {e}")
    except openai.error.APIError as e:
        logging.info(f"API error: {e}")
    except openai.error.OpenAIError as e:
        logging.info(f"An error occurred: {e}")
    return "GPT request for summarization or linkedin post generation failed for this decision." 