# X-Force addon for Slack bot
# Author: Ivan Letal
# Licence: IBM intellectual property
# Date: 2018/04/19


import xforce_api
import json
import os
from datetime import datetime, timedelta


Monitor_list = [{'channel_id' : '123456789', 'text' : 'what to monitor', 'last' : 0}] # first example item to note syntax, should be ingored in further implementations
Channels = {} # {'channel_id' : {'channel_name' : string_name, 'sched_every' : int_minutes, 'sched_next' : datetime_now}}
MAX_RESULTS= 5 # search for last X vulnerabilities only

######### (OPTIONAL) INTERNAL DEFINITIONS ###################

def commands():
  return ['list', 'test', 'add', 'remove', 'run', 'restore', 'save', 'schedule']

def help_text():
  return 'Unknown command, available commands are: {}'.format(str(commands()))

def command_test(arg): # return maximum of N searches, short output
  json_obj = xforce_api.search(arg)
  if 'error' in json_obj: return 'No results found.'
  response = ''
  count = 0
  for row in json_obj['rows']:
    count += 1
    response += '*#{}* '.format(str(count)) + '\n'  
    response += '*Title:* ' + row['title'] + '\n'
    response += '*Reported:* {}'.format(row['reported']) + '\n'
    response += '*ID:* ' + str(row['xfdbid']) + '\n'
    response += '*Risk level:* ' + str(row['risk_level']) + '\n'
    if 'platforms_affected' in row: response += '*Platforms affected:* ' + ', '.join(row['platforms_affected']) + '\n'
    response += '*References:* ' + '\n'
    for reference in row['references']:
      response += reference['link_name'] + '\n' + reference['link_target'] + '\n'
      break # list only one reference
    response += '\n'
    if count == MAX_RESULTS: break
  return response

def command_add(channel, arg): # adds text to monitor list for this channel
  global Monitor_list
  Monitor_list.append({'channel_id' : channel, 'text' : arg, 'last' : 0})
  return 'Successfully added.'

def command_remove(channel, arg): # remote text from monitor list for this channel
  global Monitor_list
  new_list = []
  for i in Monitor_list:
    if not (i['channel_id'] == channel and i['text'] == arg):
      new_list.append(i)
  if Monitor_list == new_list: 
    return 'Nothing was removed.'
  else:
    Monitor_list = new_list
    return 'Successfully removed.'

def command_list(channel): # list monitor list
  response = ''
  count = 0
  for x in Monitor_list:
    if x['channel_id'] == channel:
      count += 1
      response += '#{}: {}'.format(str(count), x['text']) + '\n'
  if count == 0: return 'Nothing is monitored for this channel.'
  return response

def command_run(channel, arg): # runs report now
  if not arg == 'now': return 'Use "run now" instead.'
  global Monitor_list
  response = ''
  for idx, val in enumerate(Monitor_list):
    x = Monitor_list[idx]
    if x['channel_id'] == channel:
      last = int(x['last'])
      text = x['text']
      json_obj = xforce_api.search(text)
      if 'error' in json_obj: return 'Internal error.'
      last_new = last
      for row in json_obj['rows']:
        if int(row['xfdbid']) > last:
          # report item	  
          if int(row['xfdbid']) > last_new: 
            last_new = int(row['xfdbid']) # save the new last / highest ID          
            Monitor_list[idx]['last'] = last_new
          response += '*Title:* ' + row['title'] + '\n'
          response += '*Reported:* {}'.format(row['reported']) + '\n'
          response += '*ID:* ' + str(row['xfdbid']) + '\n'
          response += '*Risk level:* ' + str(row['risk_level']) + '\n'
          if 'platforms_affected' in row:  response += '*Platforms affected:* ' + ', '.join(row['platforms_affected']) + '\n'
          response += '*References:* ' + '\n'
          for reference in row['references']:
            response += reference['link_name'] + '\n' + reference['link_target'] + '\n'
            break # list only one reference
          response += '\n'                    
  if not response: return 'No news.'
  else: 
    command_save(channel)
    return response

def command_save(channel):
  my_file = './saved_list_' + channel + '.txt'
  with open(my_file, 'w') as f: 
    for x in Monitor_list:
      if x['channel_id'] == channel:
        f.write(x['text'] + ';' + str(x['last']) + '\n')
    f.close()
    return 'List saved successfully.'
  return 'Error while saving list.'

def command_restore(channel):
  my_file = './saved_list_' + channel + '.txt'
  if os.path.exists(my_file): 
    with open(my_file, 'r') as f: 
      for line in f.readlines():
        text, last = line.split(';')
        x = {'channel_id' : channel, 'text' : text, 'last' : int(last)}
        if not x in Monitor_list: Monitor_list.append(x)      
  else: return 'Error while loading list.'
  return 'List restored successfully.'

def command_schedule(channel, arg):
  global Channels
  try:
    x = int(arg)
    x += 1
  except:
    if not arg == 'disable':
      return 'Invalid argument. It can be "disable" or integer value in range 1-99999.'
    else: 
      Channels[channel]['sched_every'] = 0
      print '{} ADDON: Schedule for channel "{}" was disabled.'.format(log_time(), Channels[channel]['channel_name'])
      return 'Schedule was disabled.'
  if 1 <= x <= 99999:
    Channels[channel]['sched_every'] = x
    Channels[channel]['sched_next'] = datetime.now().replace(second=0, microsecond=0) + timedelta(minutes=Channels[channel]['sched_every'])
    print '{} ADDON: New schedule for channel "{}" was set to {}.'.format(log_time(), Channels[channel]['channel_name'], Channels[channel]['sched_next'])
    return 'Schedule was enabled. Next run is at {}.'.format(Channels[channel]['sched_next'])
  else:
    return 'Invalid argument. It can be "disable" or integer value in range 1-99999.'

def log_time(): # return date / time
  return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


######### (MANDATORY) EXTERNAL ADDON DEFINITIONS ######### 

def do_event_mention(channel, part1, part2):
  if part1 not in commands(): return 'Unknown command. Use: {}'.format(commands())
  if part1 == 'list': return command_list(channel)
  elif part1 == 'test' and part2: return command_test(part2)
  elif part1 == 'add' and part2: return command_add(channel, part2)
  elif part1 == 'remove' and part2: return command_remove(channel, part2)
  elif part1 == 'run' and part2: return command_run(channel, part2)
  elif part1 == 'save': return command_save(channel)
  elif part1 == 'restore': return command_restore(channel)
  elif part1 == 'schedule' and part2: return command_schedule(channel, part2)
  else: return 'Missing argument.'

def do_event_async(channel):
  global Channels
  if Channels[channel]['sched_every'] > 0:    
    today = datetime.now().replace(microsecond=0)   
    if today > Channels[channel]['sched_next']:  
      Channels[channel]['sched_next'] = today + timedelta(minutes=Channels[channel]['sched_every'])
      print '{} ADDON: New schedule for channel "{}" was set to {}.'.format(log_time(), Channels[channel]['channel_name'], Channels[channel]['sched_next'])
      return command_run(channel, 'now')
  return None # if nothing is scheduled or schedule already run

def do_event_joinchannel(channel_id, channel_name):
  global Channels
  sched_every = 0
  sched_next = datetime.now().replace(second=0, microsecond=0)
  Channels[channel_id] = {'channel_name' : channel_name, 'sched_every' : sched_every, 'sched_next' : sched_next}
  print '{} ADDON: Channel name is "{}".'.format(log_time(), Channels[channel_id]['channel_name'])
  return None
  

#############################################################

 	  
if __name__ == '__main__':
  # 1)
  # json_obj = xforce_api.search('airwatch')
  # print json.dumps(json_obj, indent = 4, sort_keys = True)
  # print '*****************************************************'

  # 2)
  # print do_event_mention(None, 'test', 'airwatch')

  #3)
  # print command_test('airwatch')
 
  # 4)
  print command_add('CB51N66S1', 'airwatch')
  print command_add('CB51N66S1', 'Blue Coat ProxySG')
  # print command_remove('CB51N66S1', 'Blue Coat ProxySG')
  print command_add('wrongID', 'does not matter')
  print command_list('CB51N66S1')

  # 5)
  print command_run('CB51N66S1', 'now')
  print command_run('CB51N66S1', 'now') # will not do anything
