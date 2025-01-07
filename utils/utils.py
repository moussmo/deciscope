import requests

def get_header():
    url = 'https://sandbox-oauth.piste.gouv.fr/api/oauth/token'
    post_request = requests.post(url, data={"grant_type":"client_credentials", "client_id":"69021959-e7d7-4faf-bc79-04bc3fed3bc3", "client_secret":"3c7b3ad7-169c-43d9-b9ea-a4f03394c61d", "scope":"openid"},
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'})
    if post_request.status_code!=200:
        raise Exception('Token was not retrieved, post request failed')
    
    token = post_request.json()['access_token']
    header = {'accept': 'application/json',
              'Authorization': 'Bearer {}'.format(token)}
    return header