#!/usr/bin/env python
"""
status.py - Phenny spacestatus module
Author: Ward De Ridder
"""

import spaceapiapi

def status(phenny, input): 
	if spaceapiapi.SpaceapiOpen(apiURL) == True:
		spacestatus = "open"
	else:
		spacestatus = "closed"
	phenny.say("The space is currently " + spacestatus)
status.commands = ["status"]

if __name__ == '__main__': 
   print __doc__.strip()
