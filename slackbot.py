# Slack bot
# Author: Ivan Letal
# Licence: IBM intellectual property
# Date: 2018/04/19
# Before you use the script:	export SLACK_BOT_TOKEN='<your slack bot token>'


import xforce_addon as addon # you can code your own and replace this
						 # addon must contain functions: do_event_mention(), do_event_async(), do_event_joinchannel(), do_event_message()
from slackclient import SlackClient # Slack API
import re
import os
import time
from datetime import datetime


channels = [] # channels the bot is in, used for listening to channels
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
starterbot_id = None # value is assigned after the bot starts up
RTM_READ_DELAY = 1 # number of second delay between reading from RTM
MENTION_REGEX = '^<@(|[WU].+?)>(.*)'
VERBOSE = False

def parse_events(slack_events): # parses a list of events coming from the Slack RTM API
  for event in slack_events:
    if event['type'] == 'message' and not 'subtype' in event:   
      global channels
      channel = event['channel']
      if not channel in channels:
        channels.append(channel)
        do_event_joinchannel(channel)
      user_id, command = test_if_mentioned(event['text'])
      if user_id == starterbot_id: # bot is mentioned
        return 'mention', command, event['channel']
      if starterbot_id <> event['user']: # bot is not mentioned, some message arrived in channel (from other user than bot itself)
        return 'message', command, event['channel']
  return None, None, None

def test_if_mentioned(msg_text): # tests for a direct mention (@) in message text and returns the user id which was mentioned
  matches = re.search(MENTION_REGEX, msg_text)
  return (matches.group(1), matches.group(2).strip()) if matches else (None, None) # the first group contains the username, the second group contains the remaining message

def log_time(): # return date / time
  return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_channel_name(channel_id): # return channel name
  channel_info = slack_client.api_call('channels.info', channel=channel_id)
  if 'channel' in channel_info: return channel_info['channel']['name']
  else: return channel_id # unable to get channel name, e.g. direct message was received, return ID

def do_event_mention(channel, command): # run event when bot is mentioned, execute command
  print '{} {} Bot was mentioned.'.format(log_time(), channel)
  default_response = 'Internal error, addon did not provide any answer.' # default response is help text for the user
  parts = command.split(' ') # syntax: command_text some_text
  part1 = parts[0]
  part2 = ' '.join(parts[1:])
  response = addon.do_event_mention(channel, part1, part2)
  slack_client.api_call('chat.postMessage', channel=channel, text=response or default_response, as_user=True)

def do_event_message(channel, command): # run event when a new message is posted to a channel
  if VERBOSE: print '{} {} Someone wrote to the channel.'.format(log_time(), channel)
  response = 'Spam, sorry.'
  # not implemented
  # slack_client.api_call('chat.postMessage', channel=channel, text=response, as_user=True)

def do_event_async(channel): # run event for every channel periodically, usually every 1 second
  if VERBOSE: print '{} {} Asynchronous event.'.format(log_time(), channel)
  message = addon.do_event_async(channel)
  if message <> None: slack_client.api_call('chat.postMessage', channel=channel, text=message, as_user=True)

def do_event_joinchannel(channel): # run event when bot joins a new channel
  print '{} {} Slackbot joined channel.'.format(log_time(), channel)
  print '{} Current channel list: {}.'.format(log_time(), str(channels))
  message = addon.do_event_joinchannel(channel, get_channel_name(channel))
  if message <> None: slack_client.api_call('chat.postMessage', channel=channel, text='{}'.format(message), as_user=True)


if __name__ == '__main__':
  if slack_client.rtm_connect(with_team_state = False):
    while True: # keep reconnecting
      try:
        starterbot_id = slack_client.api_call('auth.test')['user_id'] # read bot's user id by calling web api method 'auth.test'
        print '{} Slackbot connected and running.'.format(log_time())
        while True:            
          for ch in channels: do_event_async(ch)
          msg_type, command, channel = parse_events(slack_client.rtm_read())            
          if msg_type == 'mention': 
            if command: do_event_mention(channel, command)
          elif msg_type == 'message': 
            if command: do_event_message(channel, command)
          time.sleep(RTM_READ_DELAY)
      except:
        print '{} Lost connection to Slack, reconnecting in 10 seconds.'.format(log_time())
        time.sleep(10)
        if slack_client.rtm_connect(with_team_state = False): pass
  else:
    print '{} Error connecting to Slack.'.format(log_time())
