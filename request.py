# Install the Python Requests library:
# `pip install requests`

import base64
import requests
import json


def send_request():
    # Request

    try:
        response = requests.get(
            url="https://api.mysportsfeeds.com/v1.0/pull/nfl/current/game_playbyplay.json?gameid=20181202-SF-SEA&quarter=4&playtype=penalty",
            params={
                "fordate": "20161121"
            },
            headers={
                "Authorization": "Basic " + base64.b64encode('{}:{}'.format("e41168e0-18e0-47b3-ad26-b2bf0f","smallbaby").encode('utf-8')).decode('ascii')
            }
        )
        print(response.status_code)
        data = response.content
        with open("outputfile.json", "w") as write_file:
            json.dump(data, write_file, indent=4)

    except requests.exceptions.RequestException:
        print('HTTP Request failed')


send_request()