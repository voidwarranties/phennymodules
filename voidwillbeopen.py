"""
voidwillbeopen.py
A module for willie http://willie.dftba.net/
This module is used for getting information when our hackerspace will be open
and the user who will open the doors.
http://we.voidwarranties.be/
Author: unloading
"""
import willie.module
import willie.tools
from willie.config import ConfigurationError

import os
import os.path
from datetime import datetime

import json

def configure(config):
	"""Adds settings to the config file"""

	if config.option("Configure key logging", False):
		config.add_section("keylogs")
		config.interactive_add(
			"keylogs", "dir",
			"Absolure path to key log storage directory",
			default = os.path.join("~", "keylogs")
		)

def get_file_path(bot, channel):
	
	basedir = os.path.expanduser(bot.config.keylogs.dir)
	channel = channel.lstrip("#")
	dt = datetime.utcnow()
	fname = "{channel}{date}.json".format(channel=channel,date=dt.date().isoformat())
	return os.path.join(basedir, fname)

def setup(bot):
    if not getattr(bot.config, "keylogs", None):
        raise ConfigurationError("Key logs are not configured")
    if not getattr(bot.config.keylogs, "dir", None):
        raise ConfigurationError("Key log storage directory is not defined")

    # ensure log directory exists
    basedir = os.path.expanduser(bot.config.keylogs.dir)
    if not os.path.exists(basedir):
        os.makedirs(basedir)

def hour_range(start, stop, step):
	li = []
	while start <= stop:
		li.append('%.2f' % start)
		start += step
	return li

def updateDatabase(bot,userInfo,path,option):
	if(option=="add"):
		new_data_struct=[]

		"""Read info from the .json file"""
		with open(path,'a+') as f: 	#'r' not good enough, if file does not exists. Problems!
			try:
				j_data =json.load(f)
				data_struct = json.loads(j_data)		
				for i in range(len(data_struct)):
					new_data_struct.append(data_struct[i])
				new_data_struct.append(userInfo)
			except ValueError:		#Build in ValueError , because if file empty => Problems !!! 
				new_data_struct.append(userInfo)

		"""Write new info to the .json file"""
		with open(path,'w') as f:
			json.dump(json.dumps(new_data_struct), f)
			bot.say("Your information has been stored.")
			return

	"""	
	Read info from .json file and search for entries 
	with the username userInfo[0], delete those		
	"""
	with open(path,'a+') as f:	#'r' not good enough, if file does not exists. Problems!
		try:
			j_data =json.load(f)
		except ValueError:
			bot.say("Wast of time!!!")
			return
		
		data_struct = json.loads(j_data)
		i=0
	
		while i < len(data_struct):
			#print data_struct[i][0]
			if data_struct[i][0] == userInfo[0]:
				del data_struct[i]
				print data_struct
				i=0 #Should be optimalized !!!!!
			if len(data_struct) != 1: #If jos was the only guy in the database, his entry would stay in the database. Not cool for jos.
				i = i + 1
	
	with open(path,'w') as f:
		json.dump(json.dumps(data_struct), f)
		bot.say("Your information has been deleted.")
		return

def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv

@willie.module.commands('gvw')
@willie.module.example('.gvw 13.00 key doorstatus attendies food')
def gvw(bot, trigger):
	key_found = False
	valid_input_hour = False
	message = trigger.group(2)
	#dummy userInfo = [username,has_key,needsfood,arrival_hour]
	userInfo = [trigger.nick,False,False,None] 

	#Fix bug if user types : .gvw with a space after it.
	if message == None:
		updateDatabase(bot,userInfo,get_file_path(bot, trigger.sender),None)
		return		
	
	message = message.lower()
	list_message = message.split()
	hour = list_message[0].replace("@","").replace(":",".").replace("h",".").replace("H",".").replace("m","").replace("M","")

	"""Check all the variables, in the message. Construct userInfo[]"""
	if hour in hour_range(0,24,0.01):
		userInfo[3] = hour
		if 'key' in message:		
			userInfo[1] = True
		if 'food' in message:
			userInfo[2] = True
		updateDatabase(bot,userInfo,get_file_path(bot, trigger.sender),"add")

	"""Check when the door will open"""
	key_holder_user = []
	key_holder_arrival = []
	hungry_users_need_food = []
	attending_users = []
	key_found = False

	with open(get_file_path(bot,trigger.sender),'a+') as f: 	#'r' not good enough, if file does not exists. Problems!
		try:
			j_data =json.load(f)
			data_struct = json.loads(j_data,object_hook=_decode_list) 
			#encoding not working !!!!!!!!!! Fix with line 157 and 158, not nice.		
	
			for i in range(len(data_struct)):
				data_struct[i][0] = data_struct[i][0].encode('utf-8')
				data_struct[i][3] = float(data_struct[i][3])
				if data_struct[i][1] == True:
					key_holder_user.append(data_struct[i][0])
					key_holder_arrival.append(data_struct[i][3])
					key_found = True
				if data_struct[i][2] == True:
					hungry_users_need_food.append(data_struct[i][0])
				attending_users.append(data_struct[i][0])

			arrival = 24.01
			i=0                                       # Using this variable because its bigger than all the vars we can get.
			position=0
			
			if key_found:
				for item in key_holder_arrival:
					if item < arrival:
						arrival = item
						position = i
					i = i + 1
				if 'doorstatus' in message:
					bot.say("The door will be opened by %s at %.2f" 
							% (key_holder_user[position],key_holder_arrival[position]))
			if 'food' in message:
				bot.say("The hungry citizens are %s" % hungry_users_need_food)
			if 'attendies' in message:
				bot.say("Attending: %s" % attending_users)

		except ValueError:										#Build in ValueError , because if file empty => Problems !!! 
			bot.say("My database is empty!!!")
			return

