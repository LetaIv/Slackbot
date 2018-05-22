# X-Force Api (vulnerabilities)
# Author: Ivan Letal
# Licence: IBM intellectual property
# Date: 2018/04/19
# API documentation: https://exchange.xforce.ibmcloud.com/settings/api
# Before you use the script:	export XFE_API_KEY='<your key>'
# 						export XFE_API_PASSWORD='<your password>'


import os
import requests
import json
import base64


key = os.environ.get('XFE_API_KEY')
password = os.environ.get('XFE_API_PASSWORD')
token = base64.b64encode(key + ":" + password)
headers = {'Authorization': "Basic " + token, 'Accept': 'application/json'}
api_endpoint = 'https://api.xforce.ibmcloud.com:443'
api_url = '/vulnerabilities/fulltext?q='


def search(text): # returns json
    url = api_endpoint + api_url + text
    try:
      response = requests.get(url, params = '', headers=headers, timeout = 20)
    except:
      json_obj = json.loads('{"error" : "Remote site unavailable."}')
    finally:
      json_obj = response.json()
    return json_obj


if __name__ == "__main__":
  json_obj = search('airwatch')
  print json.dumps(json_obj, indent = 4, sort_keys = True)
