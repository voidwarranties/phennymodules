"""
voidwillbeopen.py
A module for willie http://willie.dftba.net/
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
	if(option == "add"):
		new_data_struct = []

		"""Read info from the .json file"""
		with open(path,'a+') as f: 	#'r' not good enough, if file does not exists. Problems!
			try:
				j_data = json.load(f)
				data_struct = json.loads(j_data)		
				for i in range(len(data_struct)):
					new_data_struct.append(data_struct[i])
				new_data_struct.append(userInfo)

			except ValueError:		
				print(ValueError)
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
	if(option=="delete"):
		with open(path,'a+') as f:	#'r' not good enough, if file does not exists. Problems!
			try:
				j_data = json.load(f)
				data_struct = json.loads(j_data)

				for i in range(len(data_struct)):
					if data_struct[i][0] == userInfo[0]:
						del data_struct[i]
		
				with open(path,'w') as f:
					json.dump(json.dumps(data_struct), f)
					return

			except ValueError:
				bot.say("The database was empty?!")
				return
			
			
def findUserInDatabaseAndDelete(bot,userInfo,path):
	with open(path,'a+') as f: 	#'r' not good enough, if file does not exists. Problems!
		try:
			j_data =json.load(f)
			data_struct = json.loads(j_data)
			data_struct = unicode_to_utf8(data_struct)

			for i in range(len(data_struct)):
				if userInfo[0] == data_struct[i][0]:
					updateDatabase(bot,userInfo,path,"delete")
			return

		except ValueError:
			return 


def unicode_to_utf8(data):
	if isinstance(data, list):
		return [unicode_to_utf8(item) for item in data]
	elif isinstance(data, unicode):
		return data.encode('utf-8')
	else:
		return data

@willie.module.commands('gvw')
@willie.module.example('.gvw 13.00 key doorstatus attendies food update')
def gvw(bot, trigger):
	key_found = False
	valid_input_hour = False
	message = trigger.group(2)
	#dummy userInfo = [username,has_key,needsfood,arrival_hour]
	userInfo = [trigger.nick,False,False,None] 
	
	""".gvw deletes the information of the user"""
	if message == None or message == '':
		updateDatabase(bot,userInfo,get_file_path(bot, trigger.sender),"delete")
		bot.say("Your information has been deleted.")
		return		
	
	message = message.lower()
	list_message = message.split()
	hour = list_message[0].replace("@","").replace(":",".").replace("h",".").replace("H",".").replace("m","").replace("M","")

	"""Check all the variables, in the message. Construct userInfo[]"""
	if hour in hour_range(0,24,0.01):
		userInfo[3] = float(hour)
		if 'key' in message:		
			userInfo[1] = True	
		if 'food' in message:
			userInfo[2] = True

		findUserInDatabaseAndDelete(bot,userInfo,get_file_path(bot,trigger.sender))
		updateDatabase(bot,userInfo,get_file_path(bot, trigger.sender),"add")
	
	"""Search for the doorstatus, attendies and who needs food"""
	key_holder_user = []
	key_holder_arrival = []
	hungry_users_need_food = []
	attending_users = []
	key_found = False
	
	if 'doorstatus' in message or 'food' in message or 'attendies' in message:
		with open(get_file_path(bot,trigger.sender),'a+') as f: 	#'r' not good enough, if file does not exists. Problems!
			try:
				j_data = json.load(f)
				data_struct = json.loads(j_data)
				data_struct = unicode_to_utf8(data_struct) 
		
				for i in range(len(data_struct)):
					if data_struct[i][1] == True:
						key_holder_user.append(data_struct[i][0])
						key_holder_arrival.append(data_struct[i][3])
						key_found = True
					
					if data_struct[i][2] == True:
						hungry_users_need_food.append(data_struct[i][0])
					
					attending_users.append(data_struct[i][0])

				arrival = 24.01
				i = 0                                       # Using this variable because its bigger than all the vars we can get.
				position = 0
				if key_found:
					for item in key_holder_arrival:
						if item < arrival:
							arrival = item
							position = i
						i += 1
					if 'doorstatus' in message:
						bot.say("The door will be opened by %s at %.2f" 
								% (key_holder_user[position],key_holder_arrival[position]))
				else:
					bot.say("No key to open the door.")

				if 'food' in message:
					bot.say("Hungry: %s" % hungry_users_need_food)
				
				if 'attendies' in message:
					bot.say("Attending: %s" % attending_users)

			except ValueError:										#Build in ValueError , because if file empty => Problems !!! 
				bot.say("My database is empty?!")
				return
