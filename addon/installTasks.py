# StationPlaylist Studio add-on installation tasks
# Copyright 2015-2017 Joseph Lee and others, released under GPL.

# Provides needed routines during add-on installation and removal.
# Routines are partly based on other add-ons, particularly Place Markers by Noelia Martinez (thanks add-on authors).

def onInstall():
	import os, shutil
	profiles = os.path.join(os.path.dirname(__file__), "..", "stationPlaylist", "profiles")
	# Import old profiles.
	if os.path.exists(profiles):
		newProfiles = os.path.join(os.path.dirname(__file__), "profiles")
		try:
			shutil.copytree(profiles, newProfiles)
		except IOError:
			pass
	# 7.4 only: prepare LTS presentation file (an empty text file)
	#open(os.path.join(os.path.dirname(__file__), "ltsprep"), "w").close()
