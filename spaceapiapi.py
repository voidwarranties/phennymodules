import urllib2
import json

def SpaceapiOpen(apiURL):
    u = urllib2.urlopen(apiURL)
    jsonSpaceAPI = json.load(u)
    u.close()
    spacestatus = ""
    return jsonSpaceAPI['state']['open']
