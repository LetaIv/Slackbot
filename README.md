# Slackbot + X-Force addon and API in Python
Prerequisities:

You need a registration at https://exchange.xforce.ibmcloud.com/.

You need to own an app at https://api.slack.com/ .


Authentication:

export SLACK_BOT_TOKEN='add app's token here from Slackbot'

export XFE_API_KEY='add key from X-Force API'

export XFE_API_PASSWORD='add password from X-Force API'


Usage: python slackbot.py

Slackbot starts with X-Force addon that provides information on vulnerabilities from the IBM X-Force Exchange website.
