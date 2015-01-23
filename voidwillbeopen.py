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
	fname = "{channel}{date}.log".format(channel=channel,date=dt.date().isoformat())
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


@willie.module.commands('gvw')
@willie.module.example('.gvw @3.00 i have a key')
@willie.module.example('.gvw @13.00 i have a key')
def gvw(bot, trigger):
	
	hours = []
	key_users = []
	all_users = []
	i=0
	arrival_time = 25.00
	key_found = False
	valid_input = False

	message = trigger.group(2)
	 
	###################################################
	##Register the info of sender.
	###################################################
	if message != None:
		message = message.lower()
		list_message = message.split()
	
		hour = " [HOUR] " + list_message[0].replace("@","")
		user = " [USER] " + trigger.nick
		
		if 'key' in message:
			
			f_line = "[KEY]" + hour + user + "\n"
			split_f_line = f_line.split()
			
			if split_f_line[2] in hour_range(0,24,0.01):
				bot.say("OK , user has a key and the input:%s is valid" % split_f_line[2])
				#bot.say("Niobe: What is so important about that key?") 
				#bot.say("Keymaker: The key is integral to the path of the One.")
				valid_input = True
		else:
			
			f_line = hour + user + "\n"
			split_f_line = f_line.split()
			
			if split_f_line[1] in hour_range(0,24,0.01):
				bot.say("OK , the input:%s is valid" % split_f_line[1])
				valid_input = True

	

	if valid_input:
		f=open(get_file_path(bot, trigger.sender), "a")
		f.write(f_line)
		f.close()

		###################################################
		##Return the info about users and key to the sender.
		###################################################
		
		f=open(get_file_path(bot, trigger.sender), "r")
		for line in f:
			splitline = line.split()
			

			if 'KEY' in line:
				hours.append(splitline[2])
				key_users.append(splitline[4])
				all_users.append(splitline[4])
				key_found = True
			else:
				all_users.append(splitline[3])

		f.close()

		if key_found:
			for item in hours:
				float_item = float(item)
				if float_item < arrival_time:
					arrival_time = float_item
					position = i
				i=i+1
			bot.say("Voidwarranties will be open at %s (24.00 scale) , %s will open the doors" 
					% (hours[position],key_users[position]))
			bot.say("You will see the following users @voidwarranties: %s" % all_users)
		else:
			bot.say("Greetings keyless person, the keymaker has failed us.") 
			bot.say("Maybe you will see the following users @voidwarranties: %s" % all_users)
	else:
		bot.say("The input was invalid")
def hour_range(start, stop, step):
	li = []
	while start <= stop:
		li.append('%.2f' % start)
		start += step
	return li
