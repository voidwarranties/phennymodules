#!/usr/bin/env python
"""
status.py - Phenny spacestatus module
Author: Ward De Ridder
"""

import urllib2
import json

def SpaceapiOpen(apiURL):
    u = urllib2.urlopen(apiURL)
    jsonSpaceAPI = json.load(u)
    u.close()
    spacestatus = ""
    return jsonSpaceAPI['state']['open']

def status(phenny, input): 
	if SpaceapiOpen("http://spaceapi.voidwarranties.be/") == True:
		spacestatus = "open"
	else:
		spacestatus = "closed"
	phenny.say("The space is currently " + spacestatus)
status.commands = ["status"]

if __name__ == '__main__': 
   print __doc__.strip()
