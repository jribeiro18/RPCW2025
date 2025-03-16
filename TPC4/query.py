import requests

def query_dbpedia(endpoint_url, query):
    headers = {
        'Accept': 'application/json'
    }

    response = requests.get(endpoint_url, params={'query': query}, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception('Query failed. Returned code: {}. {}'.format(response.status_code, response.text))