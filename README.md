# Slackbot + X-Force addon and API in Python
<b>Prerequisities:</b>

You need a registration at https://exchange.xforce.ibmcloud.com/.

You need to own an app at https://api.slack.com/ .

<b>Authentication:</b>

<i>export SLACK_BOT_TOKEN='add app's token here from Slackbot'

export XFE_API_KEY='add key from X-Force API'

export XFE_API_PASSWORD='add password from X-Force API'</i>


<b>Usage:</b> <i>python slackbot.py</i>

or

<i>export SLACK_BOT_TOKEN='add app's token here from Slackbot' && export XFE_API_KEY='add key from X-Force API' && export XFE_API_PASSWORD='add password from X-Force API'</i> && python slackbot.py</i>


Slackbot starts with X-Force addon that provides information on vulnerabilities from the IBM X-Force Exchange website.


<b>TODO:</b> If you want to publish an App in Slack, your code need to support OAuth for authentication. To do that, your code need to include a web server (i.e. Flask). At this time, I did not implement but more info can be found here: https://github.com/slackapi/python-slackclient/blob/master/docs-src/auth.rst


<b>Logic:</b>
![Slackbot Diagram](https://raw.githubusercontent.com/LetaIv/Slackbot/master/slackbot_diagram.PNG)
