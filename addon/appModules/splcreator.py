# StationPlaylist Creator
# An app module and global plugin package for NVDA
# Copyright 2016-2020 Joseph Lee and others, released under GPL.

# Basic support for StationPlaylist Creator.

import appModuleHandler
import addonHandler
import globalVars
import ui
import api
from NVDAObjects.IAccessible import IAccessible, sysListView32
from .splstudio import splconfig, SPLTrackItem
addonHandler.initTranslation()

# Return a tuple of column headers.
# This is just a thinly disguised indexOf function from Studio's track item class.
def indexOf(creatorVersion):
	if creatorVersion >= "5.31":
		return ("Artist", "Title", "Position", "Cue", "Intro", "Outro", "Segue", "Duration", "Last Scheduled", "7 Days", "Date Restriction", "Year", "Album", "Genre", "Mood", "Energy", "Tempo", "BPM", "Gender", "Rating", "File Created", "Filename", "Client", "Other", "Intro Link", "Outro Link", "Language")
	else:
		return ("Artist", "Title", "Position", "Cue", "Intro", "Outro", "Segue", "Duration", "Last Scheduled", "7 Days", "Date Restriction", "Year", "Album", "Genre", "Mood", "Energy", "Tempo", "BPM", "Gender", "Rating", "File Created", "Filename", "Client", "Other", "Intro Link", "Outro Link")

class SPLCreatorItem(SPLTrackItem):
	"""An entry in SPL Creator (mostly tracks).
	"""

	# Keep a record of which column is being looked at.
	_curColumnNumber = 0

	def indexOf(self, header):
		try:
			return indexOf(self.appModule.productVersion).index(header)
		except ValueError:
			return None

	@property
	def exploreColumns(self):
		return splconfig.SPLConfig["General"]["ExploreColumnsCreator"]

	def script_trackColumnsViewer(self, gesture):
		# #61 (18.06): a direct copy of column data gatherer from playlist transcripts.
		# 20.02: customized for Creator (no status column).
		columnHeaders = indexOf(self.appModule.productVersion)
		columns = list(range(len(columnHeaders)))
		columnContents = [self._getColumnContentRaw(col) for col in columns]
		for pos in range(len(columnContents)):
			if columnContents[pos] is None: columnContents[pos] = "blank"
			# Manually add header text until column gatherer adds headers support.
			columnContents[pos] = ": ".join([columnHeaders[pos], columnContents[pos]])
		# Translators: Title of the column data window.
		ui.browseableMessage("\n".join(columnContents), title=_("Track data"))
	# Translators: input help mode message for columns viewer command.
	script_trackColumnsViewer.__doc__ = _("Presents data for all columns in the currently selected track")

	__gestures={
		"kb:control+alt+downArrow": None,
		"kb:control+alt+upArrow": None,
		"kb:control+NVDA+-":"trackColumnsViewer",
	}


class SPLPlaylistEditorItem(SPLTrackItem):
	"""An entry in SPL Creator's Playlist Editor.
	"""

	# Keep a record of which column is being looked at.
	_curColumnNumber = 0

	def indexOf(self, header):
		try:
			return self.exploreColumns.index(header)
		except ValueError:
			return None

	@property
	def exploreColumns(self):
		columns = ['Artist', 'Title', 'Duration', 'Intro', 'Outro', 'Category', 'Filename']
		if self.appModule.productVersion >= "5.40":
			columns.append('Rating')
		return columns

	__gestures={
		"kb:control+alt+downArrow": None,
		"kb:control+alt+upArrow": None,
	}


class AppModule(appModuleHandler.AppModule):

	def __init__(self, *args, **kwargs):
		super(AppModule, self).__init__(*args, **kwargs)
		# Announce Creator version at startup unless minimal flag is set.
		try:
			if not globalVars.appArgs.minimal:
				# No translation.
				ui.message("SPL Creator {SPLVersion}".format(SPLVersion = self.productVersion))
		except:
			pass
		# #64 (18.07): load config database if not done already.
		splconfig.openConfig("splcreator")

	def terminate(self):
		super(AppModule, self).terminate()
		splconfig.closeConfig("splcreator")
		SPLCreatorItem._curColumnNumber = 0

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		import controlTypes
		# 20.02: tracks list uses a different window class name other than "TListView".
		# Resort to window style and other tricks if other lists with the class name below is found and are not tracks list.
		if obj.windowClassName == "TTntListView.UnicodeClass":
			if obj.role == controlTypes.ROLE_LISTITEM:
				clsList.insert(0, SPLCreatorItem if obj.windowStyle == 1443958857 else SPLPlaylistEditorItem)
			elif obj.role == controlTypes.ROLE_LIST:
				clsList.insert(0, sysListView32.List)
		elif obj.windowClassName in ("TDemoRegForm", "TAboutForm"):
			from NVDAObjects.behaviors import Dialog
			clsList.insert(0, Dialog)

	# The following scripts are designed to work while using Playlist Editor.

	def isPlaylistEditor(self):
		if api.getForegroundObject().windowClassName != "TEditMain":
			ui.message("You are not in playlist editor")
			return False
		return True

	def script_playlistDateTime(self, gesture):
		if self.isPlaylistEditor():
			playlistDateTime = api.getForegroundObject().simpleLastChild.firstChild.next
			playlistHour = playlistDateTime.simpleNext
			playlistDay = playlistHour.simpleNext.simpleNext
			ui.message(" ".join([playlistDay.value, playlistHour.value]))

	def script_playlistDuration(self, gesture):
		if self.isPlaylistEditor():
			playlistDuration = api.getForegroundObject().simpleLastChild.firstChild
			ui.message(playlistDuration.name)

	def script_playlistScheduled(self, gesture):
		if self.isPlaylistEditor():
			statusBar = api.getForegroundObject().firstChild.firstChild
			ui.message(statusBar.getChild(2).name)

	def script_playlistRotation(self, gesture):
		if self.isPlaylistEditor():
			statusBar = api.getForegroundObject().firstChild.firstChild
			ui.message(statusBar.getChild(3).name)

	__gestures = {
		"kb:alt+NVDA+1": "playlistDateTime",
		"kb:alt+NVDA+2": "playlistDuration",
		"kb:alt+NVDA+3": "playlistScheduled",
		"kb:alt+NVDA+4": "playlistRotation",
	}
