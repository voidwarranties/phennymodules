#!/usr/bin/env python
"""
status.py - Phenny spacestatus module
Author: Ward De Ridder
"""

import urllib2
import json

def status(phenny, input): 
	u = urllib2.urlopen('http://voidwarranties.be/SpaceAPI/')
	jsonSpaceAPI = json.load(u)
	u.close()
	spacestatus = ""
	if jsonSpaceAPI['state']['open'] == True:
		spacestatus = "open"
	else:
		spacestatus = "closed"
	phenny.say("The space is currently " + spacestatus)
status.commands = ["status"]

if __name__ == '__main__': 
   print __doc__.strip()
