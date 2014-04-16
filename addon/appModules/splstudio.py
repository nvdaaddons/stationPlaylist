# Station Playlist Studio
# An app module and global plugin package for NVDA
# Copyright 2011, 2013, Geoff Shang, Joseph Lee and others, released under GPL.
# The primary function of this appModule is to provide meaningful feedback to users of SplStudio
# by allowing speaking of items which cannot be easily found.
# Version 0.01 - 7 April 2011:
# Initial release: Jamie's focus hack plus auto-announcement of status items.
# Additional work done by Joseph Lee and other contributors.
# For SPL Studio Controller, focus movement and other utilities, see the global plugin version of this app module.

# Because of different interfaces between 4.x and 5.x, we need to come up with a way to handle both.
# Minimum version: SPL 4.33, NvDA 2013.3.

from ctypes import windll
from functools import wraps
import controlTypes
import appModuleHandler
import api
import ui
import gui
import wx
import winUser
from NVDAObjects.IAccessible import IAccessible
import textInfos
import tones
import addonHandler
addonHandler.initTranslation()

# The finally function for the toggle scripts in this module (source: Tyler Spivey's code).
def finally_(func, final):
	"""Calls final after func, even if it fails."""
	def wrap(f):
		@wraps(f)
		def new(*args, **kwargs):
			try:
				func(*args, **kwargs)
			finally:
				final()
		return new
	return wrap(final)

# Try both 4.x and 5.x interfaces.
user32 = windll.user32
SPLWin = user32.FindWindowA("SPLStudio", None)

# Use IPC tags to decide what to do for 4.x and 5.x (may look similar to global plugin version).
SPLMinVersion = 500 # Check the version string against this. If it is less, use a different procedure for some routines.

class AppModule(appModuleHandler.AppModule):

	# Translators: Script category for Station Playlist commands in input gestures dialog.
	scriptCategory = _("Station Playlist Studio")

	# Some useful variables:
	beepAnnounce = False # Play beeps instead of announcing toggles.
	SPLCurVersion = winUser.sendMessage(SPLWin, 1024, 0, 2) # The version test variable.

	# GS: The following was written by James Teh <jamie@NVAccess.org
	#It gets around a problem where double focus events are fired when moving around the playlist.
	#Hopefully it will be possible to remove this when it is fixed in Studio.>
	# JL: Keeping this around for SPL 4.x users (and have confirmed that this works in 5.x).
	def event_NVDAObject_init(self, obj):
		if obj.windowClassName == "TListView" and obj.role in (controlTypes.ROLE_CHECKBOX, controlTypes.ROLE_LISTITEM) and controlTypes.STATE_FOCUSED not in obj.states and self.SPLCurVersion < 500:
			# These lists seem to fire a focus event on the previously focused item before firing focus on the new item.
			# Try to filter this out.
			obj.shouldAllowIAccessibleFocusEvent = False
		# Radio button group names are not recognized as grouping, so work around this.
		if obj.windowClassName == "TRadioGroup": obj.role = controlTypes.ROLE_GROUPING
		# In certain edit fields and combo boxes, the field name is written to the screen, and there's no way to fetch the object for this text. Thus use review position text.
		elif obj.windowClassName == "TEdit" or obj.windowClassName == "TComboBox" and obj.name is None:
			import review # This means at least NVDA 2013.2 is required.
			fieldName, fieldObj  = review.getScreenPosition(obj)
			fieldName.expand(textInfos.UNIT_LINE)
			if obj.windowClassName == "TComboBox":
				obj.name = fieldName.text.replace(obj.windowText, "")
			else:
				obj.name = fieldName.text

	# Check the following variable for end of track announcement.
	SPLEndOfTrackTime = "00:05" # Should be adjustable by the user in the end. Also find a way to announce this even if SPL Studio is minimized.

	# Automatically announce mic, line in, etc changes
	# These items are static text items whose name changes.
	# Note: There are two status bars, hence the need to exclude Up time so it doesn't announce every minute.
	# Unfortunately, Window handles and WindowControlIDs seem to change, so can't be used.
	# Bonus: if the user sets beep announce to on, beeps will be heard instead of announcements.
	# Bonus 2: announce when the track is about to end.
	def event_nameChange(self, obj, nextHandler):
		# Do not let NvDA get name for None object when SPL window is maximized.
		if obj.name == None: return
		else:
			if obj.windowClassName == "TStatusBar" and not obj.name.startswith("  Up time:"):
				# Special handling for Play Status
				if obj.IAccessibleChildID == 1:
					# Strip off "  Play status: " for brevity
					ui.message(obj.name[15:])
				else:
					# Even with beeps enabled, be sure to announce scheduled time.
					if self.beepAnnounce and obj.name.startswith("Scheduled for"): ui.message(obj.name)
					elif self.beepAnnounce:
						# User wishes to hear beeps instead of words. The beeps are power on and off sounds from PAC Mate Omni.
						import nvwave, os.path # The wave playback and path manipulator.
						beep = obj.name.split(" ")
						stat = beep[-1]
						wavDir, wavFile = os.path.dirname(__file__), ""
						# Play a wave file based on on/off status.
						if stat == "Off": wavFile = wavDir + "\SPL_off.wav"
						elif stat == "On": wavFile = wavDir+"\SPL_on.wav"
						nvwave.playWaveFile(wavFile)
					else:
						ui.message(obj.name)
			# Monitor the end of track time and announce it.
			elif obj.windowClassName == "TStaticText" and obj.name == self.SPLEndOfTrackTime and obj.simpleParent.name == "Remaining Time": tones.beep(440, 200) # SPL 4.x.
			elif obj.windowClassName == "TStaticText" and obj.name == self.SPLEndOfTrackTime and obj.simplePrevious != None and obj.simplePrevious.name == "Remaining Time": tones.beep(440, 200) # SPL 5.x.
			# Clean this mess with a more elegant solution.
		nextHandler()

	# JL's additions

	# Script sections (for ease of maintenance):
	# Time-related: elapsed time, end of track alarm, etc.
	# Misc scripts: track finder and others.
	# SPL Assistant layer: status commands.

	# A few time related scripts (elapsed time, remaining time, etc.).

	# Time status constants:
	SPLElapsedTime = 3 # Elapsed time of the current track.
	SPL4ElapsedTime = -4 # Elapsed time for SPL 4.x.

	def script_sayRemainingTime(self, gesture):
		fgWindow, remainingTime = api.getForegroundObject(), ""
		# For Studio 5.x: While Studio is on focus, the playback window with remaining time info is right next door. Parse the window title.
		# For Studio 4.x: this information is part of the main window. Fetch one of the objects.
		if self.SPLCurVersion >= SPLMinVersion: # See if we're running 5.00 or later.
			timeWindowStr = fgWindow.parent.next.name.split(" ")
			# We want the first part only, the time itself.
			remainingTime = timeWindowStr[0]
		else: # SPL 4.x.
			remainingTime = fgWindow.children[-3].firstChild.name
		ui.message(remainingTime)
	# Translators: Input help mode message for a command in Station Playlist Studio.
	script_sayRemainingTime.__doc__=_("Announces the remaining track time.")

	def script_sayElapsedTime(self, gesture):
		# Quite a complicated expression there.
		elapsedTime = self.getStatusChild(self.SPLElapsedTime).children[1].name if self.SPLCurVersion >= SPLMinVersion else self.getStatusChild(self.SPL4ElapsedTime).children[0].name
		ui.message(elapsedTime)
	# Translators: Input help mode message for a command in Station Playlist Studio.
	script_sayElapsedTime.__doc__=_("Announces the elapsed time for the currently playing track.")

	# Set the end of track alarm time between 1 and 59 seconds.

	def script_setEndOfTrackTime(self, gesture):
		# Borrowed from NVDA core cursorManager.py.
		timeVal = self.SPLEndOfTrackTime[-2:]
		# Translators: A dialog message to set end of track alarm (curAlarmSec is the current end of track alarm in seconds).
		timeMSG = _("Enter end of track alarm time in seconds (currently {curAlarmSec})").format(curAlarmSec = timeVal if int(timeVal) >= 10 else timeVal[-1])
		dlg = wx.TextEntryDialog(gui.mainFrame,
		timeMSG,
		# Translators: The title of end of track alarm dialog.
		_("End of track alarm"), defaultValue=timeVal if int(timeVal) >= 10 else timeVal[-1])
		def callback(result):
			if result == wx.ID_OK:
				# Check if the value is indeed between 1 and 59.
				if not dlg.GetValue().isdigit() or int(dlg.GetValue()) < 1 or int(dlg.GetValue()) > 59:
					# Translators: The error message presented when incorrect alarm time value has been entered.
					wx.CallAfter(gui.messageBox, _("Incorrect value entered."),
					# Translators: Standard title for error dialog (copy this from main nvda.po file).
					_("Error"),wx.OK|wx.ICON_ERROR)
				else:
					# To handle the case where we have single digits or two digits.
					if int(dlg.GetValue()) <= 9: newAlarmSec = "0" + dlg.GetValue()
					else: newAlarmSec = dlg.GetValue()
					self.SPLEndOfTrackTime = self.SPLEndOfTrackTime.replace(self.SPLEndOfTrackTime[-2:], newAlarmSec) # Quite a complicated replacement expression, but it works in this case.
		gui.runScriptModalDialog(dlg, callback)
	# Translators: Input help mode message for a command in Station Playlist Studio.
	script_setEndOfTrackTime.__doc__=_("sets end of track alarm (default is 5 seconds).")

	# Other commands (track finder and others)

	# Toggle whether beeps should be heard instead of toggle announcements.

	def script_toggleBeepAnnounce(self, gesture):
		if not self.beepAnnounce:
			self.beepAnnounce = True
			# Translators: Reported when toggle announcement is set to beeps in SPL Studio.
			ui.message(_("Toggle announcement beeps"))
		else:
			self.beepAnnounce = False
			# Translators: Reported when toggle announcement is set to words in SPL Studio.
			ui.message(_("Toggle announcement words"))
	# Translators: Input help mode message for a command in Station Playlist Studio.
	script_toggleBeepAnnounce.__doc__=_("Toggles option change announcements between words and beeps.")

	# The track finder utility for find track script.
	# Perform a linear search to locate the track description which matches the entered value.
	findText = ""

	# The utility function itself.

	def trackFinder(self, text, obj, directionForward=True):
		# Do some optimization later (techniques will include a bit of memoization using a cache dictionary of searched texts).
		while obj is not None:
			if text in obj.description:
				self.findText = text
				# We need to fire set focus event twice and exit this routine.
				obj.setFocus(), obj.setFocus()
				return
			else: obj = obj.next if directionForward else obj.previous
		wx.CallAfter(gui.messageBox,
		# Translators: Standard dialog message when an item one wishes to search is not found (copy this from main nvda.po).
		_("Search string not found."),
		# Translators: Standard error title for find error (copy this from main nvda.po).
		_("Find error"),wx.OK|wx.ICON_ERROR)

	# Find a specific track based on a searched text.
	# Unfortunately, the track list does not provide obj.name (it is None), however obj.description has the actual track entry.

	def script_findTrack(self, gesture):
		if api.getForegroundObject().windowClassName != "TStudioForm":
			# Translators: Presented when a user attempts to find tracks but is not at the track list.
			ui.message(_("Track finder is available only in track list."))
		elif api.getForegroundObject().windowClassName == "TStudioForm" and api.getFocusObject().role == controlTypes.ROLE_LIST:
			# Translators: Presented when a user wishes to find a track but didn't add any tracks.
			ui.message(_("You need to add at least one track to find tracks."))
		else:
			startObj = api.getFocusObject()
			# Translators: The text of the dialog for finding tracks.
			searchMSG = _("Enter the name of the track you wish to search.")
			dlg = wx.TextEntryDialog(gui.mainFrame,
			searchMSG,
			# Translators: The title of the find tracks dialog.
			_("Find track"), defaultValue=self.findText)
			def callback(result):
				if result == wx.ID_OK:
					# Tests (for performance reasons):
					# First, please either add at least one track to the list, or enter something, otherwise I'll not search it.
					if dlg.GetValue() is None: return
					# Second, if the entered values are same, do a forward search instead.
					elif dlg.GetValue() == self.findText: self.trackFinder(dlg.GetValue(), startObj.next)
					# Normal: do the search across the entire track list.
					else: self.trackFinder(dlg.GetValue(), startObj)
			gui.runScriptModalDialog(dlg, callback)
	# Translators: Input help mode message for a command in Station Playlist Studio.
	script_findTrack.__doc__=_("Finds a track in the track list.")

	# Find next and previous scripts.

	def script_findTrackNext(self, gesture):
		if api.getForegroundObject().windowClassName != "TStudioForm": ui.message(_("Track finder is available only in track list."))
		elif api.getForegroundObject().windowClassName == "TStudioForm" and api.getFocusObject().role == controlTypes.ROLE_LIST: ui.message(_("You need to add at least one track to find tracks."))
		else:
			if self.findText == "": self.script_findTrack(gesture)
			else: self.trackFinder(self.findText, api.getFocusObject().next)
	# Translators: Input help mode message for a command in Station Playlist Studio.
	script_findTrackNext.__doc__=_("Finds the next occurrence of the track with the name in the track list.")

	def script_findTrackPrevious(self, gesture):
		if api.getForegroundObject().windowClassName != "TStudioForm": ui.message(_("Track finder is available only in track list."))
		elif api.getForegroundObject().windowClassName == "TStudioForm" and api.getFocusObject().role == controlTypes.ROLE_LIST: ui.message(_("You need to add at least one track to find tracks."))
		else:
			if self.findText == "":
				self.script_findTrack(gesture)
			else: self.trackFinder(self.findText, api.getFocusObject().previous, directionForward=False)
	# Translators: Input help mode message for a command in Station Playlist Studio.
	script_findTrackPrevious.__doc__=_("Finds previous occurrence of the track with the name in the track list.")

	# SPL Assistant: reports status on playback, operation, etc.
	# Used layer command approach to save gesture assignments.
	# Most were borrowed from JFW and Window-Eyes layer scripts.

	# Set up the layer script environment.
	def getScript(self, gesture):
		if not self.SPLAssistant: return appModuleHandler.AppModule.getScript(self, gesture)
		script = appModuleHandler.AppModule.getScript(self, gesture)
		if not script: script = finally_(self.script_error, self.finish)
		return finally_(script, self.finish)

	def finish(self):
		self.SPLAssistant = False
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)

	def script_error(self, gesture):
		tones.beep(120, 100)

	# SPL Assistant flag.
	SPLAssistant = False

	# The SPL Assistant layer driver.

	def script_SPLAssistantToggle(self, gesture):
		# Enter the layer command if an only if we're in the track list to allow easier gesture assignment.
		if api.getForegroundObject().windowClassName != "TStudioForm":
			gesture.send()
			return
		if self.SPLAssistant:
			self.script_error(gesture)
			return
		self.bindGestures(self.__SPLAssistantGestures)
		self.SPLAssistant = True
		tones.beep(512, 10)
	# Translators: Input help mode message for a layer command in Station Playlist Studio.
	script_SPLAssistantToggle.__doc__=_("The SPL Assistant layer command. See the add-on guide for more information on available commands.")

	# Whichever layer we use, get the appropriate children from the foreground window.
	def getStatusChild(self, childIndex):
		childObj = api.getForegroundObject().children[childIndex]
		return childObj

	# List of children constants used in SPL Assistant
	# These are scattered throughout the screen, so one can use foreground.children[index] to fetch them.
	SPLPlayStatus = 5 # Play status, mic, etc.
	SPL4PlayStatus = 0 # Play status for Studio 4.x.
	SPLSystemStatus = -3 # The second status bar containing system status such as up time.
	SPL4SystemStatus = -2 # System status bar for 4.x.
	SPLHourTrackDuration = 17 # For track duration for the given hour marker.
	SPL4HourTrackDuration = 13 # Same as above for SPL 4.
	SPLHourSelectedDuration = 18 # In case the user selects one or more tracks in a given hour.
	SPL4HourSelectedDuration = 14 # Same as above for SPL 4.
	# Todo for 2.0: Add constants for trakc title and upcoming track. They will be assigned to the assistant layer below with commands borrowed from Winamp.

	# The layer commands themselves.

	def script_sayPlayStatus(self, gesture):
		obj = self.getStatusChild(self.SPLPlayStatus).children[0] if self.SPLCurVersion >= SPLMinVersion else self.getStatusChild(self.SPL4PlayStatus).children[0]
		ui.message(obj.name)

	def script_sayAutomationStatus(self, gesture):
		obj = self.getStatusChild(self.SPLPlayStatus).children[1] if self.SPLCurVersion >= SPLMinVersion else self.getStatusChild(self.SPL4PlayStatus).children[1]
		ui.message(obj.name)

	def script_sayMicStatus(self, gesture):
		obj = self.getStatusChild(self.SPLPlayStatus).children[2] if self.SPLCurVersion >= SPLMinVersion else self.getStatusChild(self.SPL4PlayStatus).children[2]
		ui.message(obj.name)

	def script_sayLineInStatus(self, gesture):
		obj = self.getStatusChild(self.SPLPlayStatus).children[3] if self.SPLCurVersion >= SPLMinVersion else self.getStatusChild(self.SPL4PlayStatus).children[3]
		ui.message(obj.name)

	def script_sayRecToFileStatus(self, gesture):
		obj = self.getStatusChild(self.SPLPlayStatus).children[4] if self.SPLCurVersion >= SPLMinVersion else self.getStatusChild(self.SPL4PlayStatus).children[4]
		ui.message(obj.name)

	def script_sayCartEditStatus(self, gesture):
		obj = self.getStatusChild(self.SPLPlayStatus).children[5] if self.SPLCurVersion >= SPLMinVersion else self.getStatusChild(self.SPL4PlayStatus).children[5]
		ui.message(obj.name)

	def script_sayHourTrackDuration(self, gesture):
		obj = self.getStatusChild(self.SPLHourTrackDuration).firstChild if self.SPLCurVersion >= SPLMinVersion else self.getStatusChild(self.SPL4HourTrackDuration).firstChild
		ui.message(obj.name)

	def script_sayHourSelectedTrackDuration(self, gesture):
		obj = self.getStatusChild(self.SPLHourSelectedDuration).firstChild if self.SPLCurVersion >= SPLMinVersion else self.getStatusChild(self.SPL4HourSelectedDuration).firstChild
		ui.message(obj.name)

	def script_sayUpTime(self, gesture):
		obj = self.getStatusChild(self.SPLSystemStatus).firstChild if self.SPLCurVersion >= SPLMinVersion else self.getStatusChild(self.SPL4SystemStatus).firstChild
		ui.message(obj.name)


	__SPLAssistantGestures={
		"kb:p":"sayPlayStatus",
		"kb:a":"sayAutomationStatus",
		"kb:m":"sayMicStatus",
		"kb:l":"sayLineInStatus",
		"kb:r":"sayRecToFileStatus",
		"kb:t":"sayCartEditStatus",
		"kb:h":"sayHourTrackDuration",
		"kb:shift+h":"sayHourSelectedTrackDuration",
		"kb:u":"sayUpTime"
	}

	__gestures={
		"kb:control+alt+t":"sayRemainingTime",
		"kb:alt+shift+t":"sayElapsedTime",
		"kb:control+nvda+1":"toggleBeepAnnounce",
		"kb:control+nvda+2":"setEndOfTrackTime",
		"kb:control+nvda+f":"findTrack",
		"kb:nvda+f3":"findTrackNext",
		"kb:shift+nvda+f3":"findTrackPrevious",
		#"kb:control+nvda+`":"SPLAssistantToggle"
	}
