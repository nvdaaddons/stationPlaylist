# StationPlaylist (formerly StationPlaylist Studio)
# An app module and global plugin package for NVDA
# Copyright 2011, 2013-2020, Geoff Shang, Joseph Lee and others, released under GPL.
# The primary function of this appModule is to provide meaningful feedback to users of SplStudio
# by allowing speaking of items which cannot be easily found.
# Version 0.01 - 7 April 2011:
# Initial release: Jamie's focus hack plus auto-announcement of status items.
# Additional work done by Joseph Lee and other contributors.
# Renamed to StationPlaylist in 2019 in order to describe the scope of this add-on.
# For SPL Studio Controller, focus movement, SAM Encoder support and other utilities, see the global plugin version of this app module.

# Minimum version: SPL 5.20, NvDA 2019.3.

from functools import wraps
from comtypes import COMError
import os
import time
import threading
from abc import abstractmethod
import controlTypes
import appModuleHandler
import api
import globalVars
import scriptHandler
import ui
import nvwave
import speech
import braille
import touchHandler
import gui
import wx
from winUser import user32, OBJID_CLIENT
from NVDAObjects import NVDAObjectTextInfo
from NVDAObjects.IAccessible import IAccessible, getNVDAObjectFromEvent, sysListView32
from NVDAObjects.behaviors import Dialog
import textInfos
import tones
from . import splbase
from . import splconfig
from . import splconfui
from . import splmisc
from . import splactions
import addonHandler
addonHandler.initTranslation()
from .spldebugging import debugOutput
from ..skipTranslation import translate


# The finally function for status announcement scripts in this module (source: Tyler Spivey's code).
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


# Make sure the broadcaster is running a compatible version.
SPLMinVersion = "5.20"

# Threads pool.
micAlarmT = None
micAlarmT2 = None
libScanT = None

# Versions of Studio where library scanning functionality is broken.
noLibScanMonitor = []


# Braille and play a sound in response to an alarm or an event.
def messageSound(wavFile, message):
	nvwave.playWaveFile(wavFile)
	braille.handler.message(message)


# A special version for microphone alarm (continuous or not).
def _micAlarmAnnouncer():
	if splconfig.SPLConfig["General"]["AlarmAnnounce"] in ("beep", "both"):
		nvwave.playWaveFile(os.path.join(os.path.dirname(__file__), "SPL_MicAlarm.wav"))
	if splconfig.SPLConfig["General"]["AlarmAnnounce"] in ("message", "both"):
		# Translators: Presented when microphone has been active for a while.
		ui.message(_("Microphone active"))


# Manage microphone alarm announcement.
def micAlarmManager(micAlarmWav, micAlarmMessage):
	messageSound(micAlarmWav, micAlarmMessage)
	# Play an alarm sound (courtesy of Jerry Mader from Mader Radio).
	global micAlarmT2
	# Use a timer to play a tone when microphone was active for more than the specified amount.
	# Mechanics come from Clock add-on.
	if splconfig.SPLConfig["MicrophoneAlarm"]["MicAlarmInterval"]:
		micAlarmT2 = wx.PyTimer(_micAlarmAnnouncer)
		wx.CallAfter(micAlarmT2.Start, splconfig.SPLConfig["MicrophoneAlarm"]["MicAlarmInterval"] * 1000)


# Category sounds dictionary (key = category, value = tone pitch).
_SPLCategoryTones = {
	"Break Note": 415,
	"Timed Break Note": 208,
	"<Manual Intro>": 600,
}


# Routines for track items themselves (prepare for future work).
# #65 (18.07): this base class represents trakc items across StationPlaylist suites such as Studio, Creator and Track Tool.
class SPLTrackItem(sysListView32.ListItem):
	"""An abstract class representing track items across SPL suite of applications such as Studio, Creator and Track Tool.
	This class provides basic properties, scripts and methods such as Columns Explorer and others.
	Subclasses should provide custom routines for various attributes, including global ones to suit their needs.

	Each subclass is named after the app module name where tracks are encountered, such as SPLStudioTrackItem for Studio.
	Subclasses of module-specific subclasses are named after SPL version, for example SPL510TrackItem for studio 5.10 if version-specific handling is required.
	Classes representing different parts of an app are given descriptive names such as StudioPlaylistViewerItem for tracks found in Studio's Playlist Viewer (main window).
	"""

	def _get_name(self):
		# 20.07: COM error is thrown when attempting to look up the name of this "track" when a playlist is cleared.
		try:
			return self.IAccessibleObject.accName(self.IAccessibleChildID)
		except COMError:
			return""

	def _get_description(self):
		# SysListView32.ListItem nullifies description, so resort to fetching it via IAccessible.
		# 19.04/18.09.8-LTS: sometimes, description must be None because it is already dealing with what appears to be a SysListView32 object, resulting in COM error.
		try:
			return self.IAccessibleObject.accDescription(self.IAccessibleChildID)
		except COMError:
			return ""

	# #103: provide an abstract index of function.
	@abstractmethod
	def indexOf(self, columnHeader):
		return None

	@scriptHandler.script(gesture="kb:control+alt+home")
	def script_firstColumn(self, gesture):
		self._moveToColumnNumber(1)

	@scriptHandler.script(gesture="kb:control+alt+end")
	def script_lastColumn(self, gesture):
		self._moveToColumnNumber(self.childCount)

	@scriptHandler.script(
		# Translators: input help mode message for column explorer commands.
		description=_("Pressing once announces data for a track column, pressing twice will present column data in a browse mode window"),
		# 19.02: script decorator can take in a list of gestures, thus take advantage of it.
		gestures=[f"kb:control+nvda+{i}" for i in range(10)],
		category=_("StationPlaylist"))
	def script_columnExplorer(self, gesture):
		# Due to the below formula, columns explorer will be restricted to number commands.
		columnPos = int(gesture.displayName.split("+")[-1])
		if columnPos == 0:
			columnPos = 10
		# #115 (20.02): do not proceed if parent list reports less than 10 columns.
		if columnPos > self.parent.columnCount:
			debugOutput(f"Column {columnPos} is out of range for this item")
			# Translators: Presented when column is out of range.
			ui.message(_("Column {columnPosition} not found").format(columnPosition=columnPos))
			return
		columnPos -= 1
		header = None
		try:
			header = self.exploreColumns[columnPos]
			# #103: only concrete implementations will return the correct index.
			column = self.indexOf(header)
		except AttributeError:
			# #117 (20.02): for track items with no custom Columns Explorer support, refer to visual column layout.
			# #72: probe column order array from the list (parent).
			# #65 (18.08): use column header method (at least the method body) provided by the class itself.
			# This will work properly if the list (parent) is (or recognized as) SysListView32.List.
			# Note that for column announcement, zero-based indexing is still used.
			column = self.parent._columnOrderArray[columnPos]
			header = self._getColumnHeaderRaw(column)
		if column is not None:
			columnContent = self._getColumnContentRaw(column)
			# #61 (18.06): pressed once will announce column data, twice will present it in a browse mode window.
			if scriptHandler.getLastScriptRepeatCount() == 0:
				if columnContent:
					# Translators: Standard message for announcing column content.
					ui.message(_("{header}: {content}").format(header=header, content=columnContent))
				else:
					# Translators: Spoken when column content is blank.
					speech.speakMessage(_("{header}: blank").format(header=header))
					# Translators: Brailled to indicate empty column content.
					braille.handler.message(_("{header}: ()").format(header=header))
			else:
				if columnContent is None:
					# Translators: presented when column information for a track is empty.
					columnContent = _("blank")
				ui.browseableMessage(
					"{0}: {1}".format(header, columnContent),
					# Translators: Title of the column data window.
					title=_("Track data"))
		else:
			# Translators: Presented when a specific column header is not found.
			ui.message(_("{headerText} not found").format(headerText=header))

	@scriptHandler.script(
		# Translators: input help mode message for columns viewer command.
		description=_("Presents data for all columns in the currently selected track"),
		gesture="kb:control+NVDA+-")
	def script_trackColumnsViewer(self, gesture):
		# #61 (18.06): a direct copy of column data gatherer from playlist transcripts.
		# 18.07: just call the gatherer function with "blank" as the readable string and add column header afterwards.
		# 20.09: fetch column headers and texts from child columns, meaning columns viewer will reflect visual display order.
		columnContents = []
		for column in self.children:
			columnContents.append("{}: {}".format(column.columnHeaderText, column.name if column.name is not None else _("blank")))
		# Translators: Title of the column data window.
		ui.browseableMessage("\n".join(columnContents), title=_("Track data"))


class SPLStudioTrackItem(SPLTrackItem):
	"""A representative class of Studio track items outside of Playlist Viewer."""
	pass


class StudioPlaylistViewerItem(SPLTrackItem):
	"""A class representing items found in Playlist Viewer (main window).
	It provides utility scripts when Playlist Viewer entries are focused, such as location text and enhanced column navigation."""

	def event_stateChange(self):
		# Why is it that NVDA keeps announcing "not selected" when track items are scrolled?
		if controlTypes.STATE_SELECTED not in self.states:
			pass

	@scriptHandler.script(gesture="kb:space")
	def script_select(self, gesture):
		gesture.send()
		speech.speakMessage(self.name)
		braille.handler.handleUpdate(self)

	# Read selected columns.
	# But first, find where the requested column lives.
	# 8.0: Make this a public function.
	# #109 (19.08): now standardized around this function.
	# #142 (20.09): do not ignore Status column (0) just because it is the name of the track as reported by MSAA.
	def indexOf(self, columnHeader):
		try:
			columnHeaders = ["Status"] + splconfig._SPLDefaults["ColumnAnnouncement"]["ColumnOrder"]
			return columnHeaders.index(columnHeader)
		except ValueError:
			return None

	def reportFocus(self):
		if splconfig.SPLConfig["General"]["CategorySounds"]:
			category = self._getColumnContentRaw(self.indexOf("Category"))
			if category in _SPLCategoryTones:
				tones.beep(_SPLCategoryTones[category], 50)
		# 7.0: Comments please.
		if splconfig.SPLConfig["General"]["TrackCommentAnnounce"] != "off":
			self.announceTrackComment(0)
		# 6.3: Catch an unusual case where screen order is off yet column order is same as screen order and NvDA is told to announce all columns.
		# 17.04: Even if vertical column commands are performed, build description pieces for consistency.
		# 19.06: have the column inclusion and order keys handy in order to avoid attribute lookup.
		columnsToInclude = splconfig.SPLConfig["ColumnAnnouncement"]["IncludedColumns"]
		columnOrder = splconfig.SPLConfig["ColumnAnnouncement"]["ColumnOrder"]
		if (
			not splconfig.SPLConfig["ColumnAnnouncement"]["UseScreenColumnOrder"]
			and (columnOrder != splconfig._SPLDefaults["ColumnAnnouncement"]["ColumnOrder"] or len(columnsToInclude) != 17)
		):
			descriptionPieces = []
			includeColumnHeaders = splconfig.SPLConfig["ColumnAnnouncement"]["IncludeColumnHeaders"]
			for header in columnOrder:
				if header in columnsToInclude:
					index = self.indexOf(header)
					if index is None:
						continue  # Header not found, mostly encountered in Studio 5.0x.
					content = self._getColumnContentRaw(index)
					if content:
						descriptionPieces.append("{}: {}".format(header, content) if includeColumnHeaders else content)
			self.description = ", ".join(descriptionPieces)
		if self._savedColumnNumber is None:
			super(IAccessible, self).reportFocus()
		else:
			# Don't forget that column position starts at 1, not 0 (therefore subtract 1).
			colNumber = self._savedColumnNumber - 1
			verticalColumnAnnounce = splconfig.SPLConfig["General"]["VerticalColumnAnnounce"]
			if verticalColumnAnnounce == "Status" or (verticalColumnAnnounce is None and self._savedColumnNumber == 1):
				colNumber = 0
			else:
				colNumber = self._savedColumnNumber - 1 if verticalColumnAnnounce is None else self.indexOf(verticalColumnAnnounce)
			# Add track check status to column data if needed by using a customized move to column number method.
			cell = self.getChild(colNumber)
			if colNumber > 0 and self.name:
				cell.name = "{0} {1}".format(self.name, cell.name)
			self._moveToColumn(cell)
		# 7.0: Let the app module keep a reference to this track.
		self.appModule._focusedTrack = self
		# #142 (20.09): just like fake table row behavior class, nullify saved column number.
		self.__class__._savedColumnNumber = None

	# A friendly way to report track position via location text.
	def _get_locationText(self):
		# Translators: location text for a playlist item (example: item 1 of 10).
		return _("Item {current} of {total}").format(current=self.IAccessibleChildID, total=splbase.studioAPI(0, 124))

	# #12 (18.04): select and set focus to this track.
	def doAction(self, index=None):
		self.setFocus(), self.setFocus()
		splbase.selectTrack(self.IAccessibleChildID - 1)

	# Obtain column contents for all columns for this track.
	# A convenience method that calls column content getter for a list of columns.
	# Readable flag will transform None into an empty string, suitable for output.
	# #61 (18.07): readable flag will become a string parameter to be used in columns viewer.
	def _getColumnContents(self, columns=None, readable=False):
		if columns is None:
			columns = list(range(18))
		columnContents = [self._getColumnContentRaw(col) for col in columns]
		if readable:
			# #148 (20.10): Use enumerate function to obtain both column content and position in one go rather than using a range based on list length.
			for pos, content in enumerate(columnContents):
				if content is None:
					columnContents[pos] = ""
		return columnContents

	# Now the scripts.

	# Track movement scripts.
	# Detects top/bottom of a playlist if told to do so.

	@scriptHandler.script(gesture="kb:downArrow")
	def script_nextTrack(self, gesture):
		gesture.send()
		if self.IAccessibleChildID == self.parent.childCount - 1 and splconfig.SPLConfig["General"]["TopBottomAnnounce"]:
			tones.beep(2000, 100)

	@scriptHandler.script(gesture="kb:upArrow")
	def script_prevTrack(self, gesture):
		gesture.send()
		if self.IAccessibleChildID == 1 and splconfig.SPLConfig["General"]["TopBottomAnnounce"]:
			tones.beep(2000, 100)

	# Vertical column navigation.
	# The following move to row method was customized for Studio track item.

	def _moveToRow(self, row):
		if not row:
			return self._moveToColumn(None) if splconfig.SPLConfig["General"]["TopBottomAnnounce"] else None
		nav = api.getNavigatorObject()
		if nav != self and nav.parent == self:
			self.__class__._savedColumnNumber = nav.columnNumber
		# Do action method will set focus to and select the row in question.
		row.doAction()

	# Overlay class version of Columns Explorer.

	@property
	def exploreColumns(self):
		return splconfig.SPLConfig["General"]["ExploreColumns"]

	# Track comments.

	# Track comment announcer.
	# Levels indicate what should be done.
	# 0 indicates reportFocus, subsequent levels indicate script repeat count+1.
	def announceTrackComment(self, level):
		filename = self._getColumnContentRaw(self.indexOf("Filename"))
		if filename is not None and filename in splconfig.trackComments:
			if level == 0:
				if splconfig.SPLConfig["General"]["TrackCommentAnnounce"] in ("message", "both"):
					# Message comes from NVDA Core.
					ui.message(translate("has comment"))
				if splconfig.SPLConfig["General"]["TrackCommentAnnounce"] in ("beep", "both"):
					tones.beep(1024, 100)
			elif level == 1:
				ui.message(splconfig.trackComments[filename])
			elif level == 2:
				api.copyToClip(splconfig.trackComments[filename])
				# Translators: Presented when track comment has been copied to clipboard.
				ui.message(_("Track comment copied to clipboard"))
			else:
				self._trackCommentsEntry(filename, splconfig.trackComments[filename])
		else:
			if level in (1, 2):
				# Translators: Presented when there is no track comment for the focused track.
				ui.message(_("No comment"))
			elif level >= 3:
				# 16.12: timed break notes shows an odd value for filename (seconds in integers followed by a colon), potentially confusing users.)
				if filename and not filename.endswith(":"):
					self._trackCommentsEntry(filename, "")
				else:
					# Translators: Presented when focused on a track other than an actual track (such as hour marker).
					ui.message(_("Comments cannot be added to this kind of track"))

	# A proxy function to call the track comments entry dialog.
	def _trackCommentsEntry(self, filename, comment):
		dlg = wx.TextEntryDialog(
			gui.mainFrame, _("Track comment"),
			# Translators: The title of the track comments dialog.
			_("Track comment"), value=comment)

		def callback(result):
			if result == wx.ID_OK:
				if dlg.GetValue() is None:
					return
				elif dlg.GetValue() == "":
					del splconfig.trackComments[filename]
				else:
					splconfig.trackComments[filename] = dlg.GetValue()
		gui.runScriptModalDialog(dlg, callback)

	@scriptHandler.script(
		# Translators: Input help message for track comment announcemnet command in SPL Studio.
		description=_("Announces track comment if any. Press twice to copy this information to the clipboard, and press three times to open a dialog to add, change or remove track comments"),
		gesture="kb:Alt+NVDA+C",
		category=_("StationPlaylist"))
	def script_announceTrackComment(self, gesture):
		self.announceTrackComment(scriptHandler.getLastScriptRepeatCount() + 1)


SPLAssistantHelp = {
	# Translators: The text of the help command in SPL Assistant layer.
	"off": _("""After entering SPL Assistant, press:
A: Automation.
C: Announce name of the currently playing track.
D: Remaining time for the playlist.
E: Overall metadata streaming status.
Shift+1 through shift+4, shift+0: Metadata streaming status for DSP encoder and four additional URL's.
H: Duration of trakcs in this hour slot.
Shift+H: Duration of remaining trakcs in this hour slot.
I: Listener count.
K: Move to place marker track.
Control+K: Set place marker track.
L: Line-in status.
M: Microphone status.
N: Next track.
P: Playback status.
Shift+P: Pitch for the current track.
R: Record to file.
Shift+R: Monitor library scan.
S: Scheduled time for the track.
Shift+S: Time until the selected track will play.
T: Cart edit/insert mode.
U: Studio up time.
W: Weather and temperature.
Y: Playlist modification.
F8: Take playlist snapshots such as track count, longest track and so on.
Shift+F8: Obtain playlist transcripts in a variety of formats.
F9: Mark current track as start of track time analysis.
F10: Perform track time analysis.
F12: Switch to an instant switch profile.
Shift+F1: Open online user guide."""),
	# Translators: The text of the help command in SPL Assistant layer when JFW layer is active.
	"jfw": _("""After entering SPL Assistant, press:
A: Automation.
C: Toggle cart explorer.
Shift+C: Announce name of the currently playing track.
E: Overall metadata streaming status.
Shift+1 through shift+4, shift+0: Metadata streaming status for DSP encoder and four additional URL's.
Shift+E: Record to file.
F: Track finder.
H: Duration of trakcs in this hour slot.
Shift+H: Duration of remaining trakcs in this hour slot.
K: Move to place marker track.
Control+K: Set place marker track.
L: Listener count.
Shift+L: Line-in status.
M: Microphone status.
N: Next track.
P: Playback status.
Shift+P: Pitch for the current track.
R: Remaining time for the playlist.
Shift+R: Monitor library scan.
S: Scheduled time for the track.
Shift+S: Time until the selected track will play.
T: Cart edit/insert mode.
U: Studio up time.
W: Weather and temperature.
Y: Playlist modification.
F8: Take playlist snapshots such as track count, longest track and so on.
Shift+F8: Obtain playlist transcripts in a variety of formats.
F9: Mark current track as start of track time analysis.
F10: Perform track time analysis.
F12: Switch to an instant switch profile.
Shift+F1: Open online user guide.""")}


# Provide a way to fetch dialog description in reverse order.
# This is used in Studio's About dialog as children are in reverse tab order somehow.
class ReversedDialog(Dialog):
	"""Overrides the description property to obtain dialog text except in reverse order.
	This is employed in Studio's help/About dialog.
	"""

	@classmethod
	def getDialogText(cls, obj, allowFocusedDescendants=True):
		"""This classmethod walks through the children of the given object, and collects up and returns any text that seems to be  part of a dialog's message text.
		@param obj: the object who's children you want to collect the text from
		@type obj: L{IAccessible}
		@param allowFocusedDescendants: if false no text will be returned at all if one of the descendants is focused.
		@type allowFocusedDescendants: boolean
		"""
		children = obj.children
		textList = []
		childCount = len(children)
		# For these dialogs, children are arranged in reverse tab order (very strange indeed).
		for index in range(childCount - 1, -1, -1):
			child = children[index]
			childStates = child.states
			childRole = child.role
			# We don't want to handle invisible or unavailable objects
			if controlTypes.STATE_INVISIBLE in childStates or controlTypes.STATE_UNAVAILABLE in childStates:
				continue
			# For particular objects, we want to descend in to them and get their children's message text
			if childRole in (controlTypes.ROLE_PROPERTYPAGE, controlTypes.ROLE_PANE, controlTypes.ROLE_PANEL, controlTypes.ROLE_WINDOW, controlTypes.ROLE_GROUPING, controlTypes.ROLE_PARAGRAPH, controlTypes.ROLE_SECTION, controlTypes.ROLE_TEXTFRAME, controlTypes.ROLE_UNKNOWN):
				# Grab text from descendants, but not for a child which inherits from Dialog and has focusable descendants
				# Stops double reporting when focus is in a property page in a dialog
				childText = cls.getDialogText(child, not isinstance(child, Dialog))
				if childText:
					textList.append(childText)
				elif childText is None:
					return None
				continue
			# If the child is focused  we should just stop and return None
			if not allowFocusedDescendants and controlTypes.STATE_FOCUSED in child.states:
				return None
			# We only want text from certain controls.
			if not (
				# Static text, labels and links
				childRole in (controlTypes.ROLE_STATICTEXT, controlTypes.ROLE_LABEL, controlTypes.ROLE_LINK)
				# Read-only, non-multiline edit fields
				or (childRole == controlTypes.ROLE_EDITABLETEXT and controlTypes.STATE_READONLY in childStates and controlTypes.STATE_MULTILINE not in childStates)
			):
				continue
			# We should ignore a text object directly after a grouping object, as it's probably the grouping's description
			if index > 0 and children[index - 1].role == controlTypes.ROLE_GROUPING:
				continue
			# Like the last one, but a graphic might be before the grouping's description
			if index > 1 and children[index - 1].role == controlTypes.ROLE_GRAPHIC and children[index - 2].role == controlTypes.ROLE_GROUPING:
				continue
			childName = child.name
			if childName and index < (childCount - 1) and children[index + 1].role not in (controlTypes.ROLE_GRAPHIC, controlTypes.ROLE_STATICTEXT, controlTypes.ROLE_SEPARATOR, controlTypes.ROLE_WINDOW, controlTypes.ROLE_PANE, controlTypes.ROLE_BUTTON) and children[index + 1].name == childName:
				# This is almost certainly the label for the next object, so skip it.
				continue
			isNameIncluded = child.TextInfo is NVDAObjectTextInfo or childRole in (controlTypes.ROLE_LABEL, controlTypes.ROLE_STATICTEXT)
			childText = child.makeTextInfo(textInfos.POSITION_ALL).text
			if not childText or childText.isspace() and child.TextInfo is not NVDAObjectTextInfo:
				childText = child.basicText
				isNameIncluded = True
			if not isNameIncluded:
				# The label isn't in the text, so explicitly include it first.
				if childName:
					textList.append(childName)
			if childText:
				textList.append(childText)
		return "\n".join(textList)


# Temporary Cue time pickers does not expose the correct tree.
# Thankfully, when up or down arrows are pressed, display text changes.
class SPLTimePicker(IAccessible):

	@scriptHandler.script(gestures=["kb:upArrow", "kb:downArrow"])
	def script_changeTimePickerValue(self, gesture):
		gesture.send()
		import treeInterceptorHandler
		obj = api.getFocusObject()
		treeInterceptor = obj.treeInterceptor
		if isinstance(treeInterceptor, treeInterceptorHandler.DocumentTreeInterceptor) and not treeInterceptor.passThrough:
			obj = treeInterceptor
		try:
			info = obj.makeTextInfo(textInfos.POSITION_CARET)
		except (NotImplementedError, RuntimeError):
			info = obj.makeTextInfo(textInfos.POSITION_FIRST)
		info.expand(textInfos.UNIT_LINE)
		# 20.03: NVDA 2020.1 includes output reason enumeration, deprecating output reason flags.
		# Until support for NVDA 2019.3 is dropped, use both paths.
		if hasattr(controlTypes, "OutputReason"):
			speech.speakTextInfo(info, unit=textInfos.UNIT_LINE, reason=controlTypes.OutputReason.CARET)
		else:
			speech.speakTextInfo(info, unit=textInfos.UNIT_LINE, reason=controlTypes.REASON_CARET)


class AppModule(appModuleHandler.AppModule):

	# Translators: Script category for StationPlaylist add-on commands in input gestures dialog.
	scriptCategory = _("StationPlaylist")
	SPLCurVersion = appModuleHandler.AppModule.productVersion
	_focusedTrack = None
	# Monitor Studio API routines.
	_SPLStudioMonitor = None

	# Prepare the settings dialog among other things.
	def __init__(self, *args, **kwargs):
		# #110 (19.08): assertion thrown when attempting to locate Studio window handle because the locator thread is queued from main thread when app is gone.
		# This is seen when restarting NVDA while studio add-on settings screen was active.
		if wx.GetApp() is None:
			return
		super(AppModule, self).__init__(*args, **kwargs)
		if self.SPLCurVersion < SPLMinVersion:
			raise RuntimeError("Unsupported version of Studio is running, exiting app module")
		debugOutput(f"Using SPL Studio version {self.SPLCurVersion}")
		# #84: if foreground object is defined, this is a true Studio start, otherwise this is an NVDA restart with Studio running.
		# The latter is possible because app module constructor can run before NVDA finishes initializing, particularly if system focus is located somewhere other than Taskbar.
		# Note that this is an internal implementation detail and is subject to change without notice.
		debugOutput("Studio is starting" if api.getForegroundObject() is not None else "Studio is already running")
		# 17.09: do this if minimal startup flag is not present.
		try:
			if not globalVars.appArgs.minimal:
				# No translation.
				ui.message("SPL Studio {SPLVersion}".format(SPLVersion=self.SPLCurVersion))
		except Exception:
			pass
		# #40 (17.12): react to profile switches.
		# #94 (19.03/18.09.7-LTS): also listen to profile reset action.
		splactions.SPLActionProfileSwitched.register(self.actionProfileSwitched)
		splactions.SPLActionSettingsReset.register(self.actionSettingsReset)
		# 20.09: to avoid a resource leak, metadata actions must be registered here, not when splmisc module is being imported.
		splactions.SPLActionProfileSwitched.register(splmisc.metadata_actionProfileSwitched)
		splactions.SPLActionSettingsReset.register(splmisc.metadata_actionSettingsReset)
		debugOutput("loading add-on settings")
		splconfig.initialize()
		# Announce status changes while using other programs.
		# This requires NVDA core support and will be available in 6.0 and later (cannot be ported to earlier versions).
		# For now, handle all background events, but in the end, make this configurable.
		import eventHandler
		eventHandler.requestEvents(eventName="nameChange", processId=self.processID, windowClassName="TStatusBar")
		eventHandler.requestEvents(eventName="nameChange", processId=self.processID, windowClassName="TStaticText")
		# Also for requests window.
		eventHandler.requestEvents(eventName="show", processId=self.processID, windowClassName="TRequests")
		debugOutput("preparing GUI subsystem")
		try:
			self.prefsMenu = gui.mainFrame.sysTrayIcon.preferencesMenu
			self.SPLSettings = self.prefsMenu.Append(wx.ID_ANY, _("SPL Studio Settings..."), _("SPL settings"))
			gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, splconfui.onConfigDialog, self.SPLSettings)
		except AttributeError:
			debugOutput("failed to initialize GUI subsystem")
			self.prefsMenu = None
		# #82 (18.11/18.09.5-lts): notify others when Studio window gets focused the first time in order to synchronize announcement order.
		self._initStudioWindowFocused = threading.Event()
		# Let me know the Studio window handle.
		# 6.1: Do not allow this thread to run forever (seen when evaluation times out and the app module starts).
		self.noMoreHandle = threading.Event()
		debugOutput("locating Studio window handle")
		# If this is started right away, foreground and focus objects will be NULL according to NVDA if NVDA restarts while Studio is running.
		t = threading.Thread(target=self._locateSPLHwnd)
		wx.CallAfter(t.start)
		# Display startup dialogs if any.
		# 17.10: not when minimal startup flag is set.
		# 18.08.1: sometimes, wxPython 4 says wx.App isn't ready.
		try:
			wx.CallAfter(splconfig.showStartupDialogs, oldVer=self.SPLCurVersion == SPLMinVersion)
		except Exception:
			pass

	# Locate the handle for main window for caching purposes.
	def _locateSPLHwnd(self):
		hwnd = user32.FindWindowW("SPLStudio", None)
		while not hwnd:
			time.sleep(1)
			# If the demo copy expires and the app module begins, this loop will spin forever.
			# Make sure this loop catches this case.
			if self.noMoreHandle.isSet():
				self.noMoreHandle.clear()
				self.noMoreHandle = None
				return
			hwnd = user32.FindWindowW("SPLStudio", None)
		# Only this thread will have privilege of notifying handle's existence.
		with threading.Lock():
			splbase._SPLWin = hwnd
			debugOutput(f"Studio handle is {hwnd}")
		# #41 (18.04): start background monitor.
		# 18.08: unless Studio is exiting.
		try:
			self._SPLStudioMonitor = wx.PyTimer(self.studioAPIMonitor)
			wx.CallAfter(self._SPLStudioMonitor.Start, 1000)
		except Exception:
			pass
		# Remind me to broadcast metadata information.
		# 18.04: also when delayed action is needed because metadata action handler couldn't locate Studio handle itself.
		if splconfig.SPLConfig["General"]["MetadataReminder"] == "startup" or splmisc._delayMetadataAction:
			splmisc._delayMetadataAction = False
			# If told to remind and connect, metadata streaming will be enabled at this time.
			# 6.0: Call Studio API twice - once to set, once more to obtain the needed information.
			# 6.2/7.0: When Studio API is called, add the value into the stream count list also.
			# 17.11: call the connector.
			splmisc.metadataConnector()
			# #40 (18.02): call the internal announcer in order to not hold up action handler queue.
			# #51 (18.03/15.14-LTS): if this is called within two seconds (status time-out), status will be announced multiple times.
			# 18.04: hopefully the error message won't be shown as this is supposed to run right after locating Studio handle.
			# #82 (18.11/18.09.5-lts): wait until Studio window shows up (foreground or background) for the first time.
			# #83: if NVDA restarts while Studio is running and foreground window is something other than playlist viewer, the below method won't work at all.
			# Thankfully, NVDA's notion of foreground window depends on a global variable, and if it is not set, this is a restart with Studio running, so just announce it.
			if api.getForegroundObject() is not None:
				self._initStudioWindowFocused.wait()
			splmisc._earlyMetadataAnnouncerInternal(splmisc.metadataStatus(), startup=True)

	# Studio API heartbeat.
	# Although useful for library scan detection, it can be extended to cover other features.

	def studioAPIMonitor(self):
		# Only proceed if Studio handle is valid.
		if not user32.FindWindowW("SPLStudio", None):
			if self._SPLStudioMonitor is not None:
				self._SPLStudioMonitor.Stop()
				self._SPLStudioMonitor = None
				return
		# #41 (18.04): background library scan detection.
		# Thankfully, current lib scan reporter function will not proceed when library scan is happening via Insert Tracks dialog.
		# #92 (19.01.1/18.09.7-LTS): if Studio dies, zero will be returned, so check for window handle once more.
		if splbase.studioAPI(1, 32) >= 0:
			if not user32.FindWindowW("SPLStudio", None):
				return
			if not self.libraryScanning:
				self.script_libraryScanMonitor(None)
		# #86 (18.12/18.09.6-LTS): certain internal markers require presence of a playlist, otherwise unexpected things may happen.
		trackCount = splbase.studioAPI(0, 124)
		if not trackCount:
			if self._focusedTrack is not None:
				self._focusedTrack = None
			if self._analysisMarker is not None:
				self._analysisMarker = None
		# #145 (20.09: playlist analysis marker value must be below track count.
		if self._analysisMarker is not None and not 0 <= self._analysisMarker < trackCount:
			self._analysisMarker = None

	# Let the global plugin know if SPLController passthrough is allowed.
	def SPLConPassthrough(self):
		return splconfig.SPLConfig["Advanced"]["SPLConPassthrough"]

	# The only job of the below event is to notify others that Studio window has appeared for the first time.
	# This is used to coordinate various status announcements.

	def event_foreground(self, obj, nextHandler):
		if not self._initStudioWindowFocused.isSet() and obj.windowClassName == "TStudioForm":
			self._initStudioWindowFocused.set()
		nextHandler()

	def event_NVDAObject_init(self, obj):
		# From 0.01: previously focused item fires focus event when it shouldn't.
		if obj.windowClassName == "TListView" and obj.role in (controlTypes.ROLE_CHECKBOX, controlTypes.ROLE_LISTITEM) and controlTypes.STATE_FOCUSED not in obj.states:
			obj.shouldAllowIAccessibleFocusEvent = False
		# Radio button group names are not recognized as grouping, so work around this.
		elif obj.windowClassName == "TRadioGroup":
			obj.role = controlTypes.ROLE_GROUPING
		# In certain edit fields and combo boxes, the field name is written to the screen, and there's no way to fetch the object for this text. Thus use review position text.
		elif obj.windowClassName in ("TEdit", "TComboBox") and not obj.name:
			import review
			fieldName, fieldObj = review.getScreenPosition(obj)
			fieldName.expand(textInfos.UNIT_LINE)
			if obj.windowClassName == "TComboBox":
				obj.name = fieldName.text.replace(obj.windowText, "")
			else:
				obj.name = fieldName.text

	# Some controls which needs special routines.
	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		role = obj.role
		try:
			windowStyle = obj.windowStyle
		except AttributeError:
			windowStyle = 0
		if obj.windowClassName == "TTntListView.UnicodeClass":
			if role == controlTypes.ROLE_LISTITEM:
				# Track item window style has changed in Studio 5.31.
				trackItemWindowStyle = 1443991617 if self.productVersion >= "5.31" else 1443991625
				if abs(windowStyle - trackItemWindowStyle) % 0x100000 == 0:
					clsList.insert(0, StudioPlaylistViewerItem)
				else:
					clsList.insert(0, SPLStudioTrackItem)
			# #69 (18.08): allow actual list views to be treated as SysListView32.List so column count and other data can be retrieved easily.
			elif role == controlTypes.ROLE_LIST:
				clsList.insert(0, sysListView32.List)
		# 7.2: Recognize known dialogs.
		elif obj.windowClassName in ("TDemoRegForm", "TOpenPlaylist"):
			clsList.insert(0, Dialog)
		# For About dialog in Studio 5.1x and later.
		elif obj.windowClassName == "TAboutForm" and self.SPLCurVersion >= "5.1":
			clsList.insert(0, ReversedDialog)
		# Temporary cue time picker and friends.
		elif obj.windowClassName == "TDateTimePicker":
			clsList.insert(0, SPLTimePicker)

	# Keep an eye on library scans in insert tracks window.
	libraryScanning = False
	scanCount = 0
	# Prevent NVDA from announcing scheduled time multiple times.
	scheduledTimeCache = ""
	# Prevent NVDA from announcing match results in Insert Tracks/search.
	matchedResultsCache = ""

	# Automatically announce mic, line in, etc changes
	# These items are static text items whose name changes.
	# Note: There are two status bars, hence the need to exclude Up time so it doesn't announce every minute.
	# Unfortunately, Window handles and WindowControlIDs seem to change, so can't be used.
	# Only announce changes if told to do so via the following function.
	def _TStatusBarChanged(self, obj):
		name = obj.name
		if name.startswith("  Up time:"):
			return False
		elif name.startswith("Scheduled for"):
			if self.scheduledTimeCache == name:
				return False
			self.scheduledTimeCache = name
			return splconfig.SPLConfig["SayStatus"]["SayScheduledFor"]
		elif "Listener" in name:
			return splconfig.SPLConfig["SayStatus"]["SayListenerCount"]
		elif name.startswith("Cart") and obj.IAccessibleChildID == 3:
			return splconfig.SPLConfig["SayStatus"]["SayPlayingCartName"]
		# 20.07: in insert tracks dialog, name change event is fired continuously until actual result is known.
		# To prevent an event flood risk, say "no" if the same result text was cached.
		elif "match" in name and api.getForegroundObject().windowClassName == "TTrackInsertForm":
			return self.matchedResultsCache != name
		return True

	# Now the actual event.
	def event_nameChange(self, obj, nextHandler):
		# Do not let NvDA get name for None object when SPL window is maximized.
		if not obj.name:
			return
		# Only announce changes in status bar objects when told to do so.
		if obj.windowClassName == "TStatusBar" and self._TStatusBarChanged(obj):
			# Special handling for Play Status
			if obj.IAccessibleChildID == 1:
				if "Play status" in obj.name:
					# Strip off "  Play status: " for brevity only in main playlist window.
					ui.message(obj.name.split(":")[1][1:])
				elif "Loading" in obj.name:
					if splconfig.SPLConfig["General"]["LibraryScanAnnounce"] not in ("off", "ending"):
						# If library scan is in progress, announce its progress when told to do so.
						self.scanCount += 1
						if self.scanCount % 100 == 0:
							self._libraryScanAnnouncer(obj.name[1:obj.name.find("]")], splconfig.SPLConfig["General"]["LibraryScanAnnounce"])
					if not self.libraryScanning:
						if self.productVersion not in noLibScanMonitor:
							self.libraryScanning = True
				elif "match" in obj.name:
					# 20.07: announce search/match results from insert tracks dialog while there is no library rescan in progress.
					# Only announce match count as the whole thing is very verbose, and results text would have been checked by status bar checker anyway.
					if not self.libraryScanning:
						self.matchedResultsCache = obj.name
						ui.message(" ".join(obj.name.split()[:2]))
					else:
						if splconfig.SPLConfig["General"]["LibraryScanAnnounce"] != "off" and self.libraryScanning:
							if splconfig.SPLConfig["General"]["BeepAnnounce"]:
								tones.beep(370, 100)
							else:
								# Translators: Presented when library scan is complete.
								ui.message(_("Scan complete with {scanCount} items").format(scanCount=obj.name.split()[3]))
						if self.libraryScanning:
							self.libraryScanning = False
						self.scanCount = 0
			else:
				# 16.12: Because cart edit text shows cart insert status, exclude this from toggle state announcement.
				if obj.name.endswith((" On", " Off")) and not obj.name.startswith("Cart "):
					self._toggleMessage(obj.name)
				else:
					ui.message(obj.name)
				if self.cartExplorer or splconfig.SPLConfig["MicrophoneAlarm"]["MicAlarm"]:
					# Activate mic alarm or announce when cart explorer is active.
					self.doExtraAction(obj.name)
		# Monitor the end of track and song intro time and announce it.
		elif obj.windowClassName == "TStaticText":
			if obj.simplePrevious is not None:
				if obj.simplePrevious.name == "Remaining Time":
					# End of track for SPL 5.x.
					if splconfig.SPLConfig["General"]["BrailleTimer"] in ("outro", "both") and api.getForegroundObject().processID == self.processID:
						braille.handler.message(obj.name)
					if (
						obj.name == "00:{0:02d}".format(splconfig.SPLConfig["IntroOutroAlarms"]["EndOfTrackTime"])
						and splconfig.SPLConfig["IntroOutroAlarms"]["SayEndOfTrack"]
					):
						self.alarmAnnounce(obj.name, 440, 200)
				elif obj.simplePrevious.name == "Remaining Song Ramp":
					# Song intro for SPL 5.x.
					if splconfig.SPLConfig["General"]["BrailleTimer"] in ("intro", "both") and api.getForegroundObject().processID == self.processID:
						braille.handler.message(obj.name)
					if (
						obj.name == "00:{0:02d}".format(splconfig.SPLConfig["IntroOutroAlarms"]["SongRampTime"])
						and splconfig.SPLConfig["IntroOutroAlarms"]["SaySongRamp"]
					):
						self.alarmAnnounce(obj.name, 512, 400, intro=True)
		nextHandler()

	# JL's additions

	# Handle toggle messages.
	def _toggleMessage(self, msg):
		if splconfig.SPLConfig["General"]["MessageVerbosity"] != "beginner":
			msg = msg.split()[-1]
		if splconfig.SPLConfig["General"]["BeepAnnounce"]:
			# User wishes to hear beeps instead of words. The beeps are power on and off sounds from PAC Mate Omni.
			if msg.endswith("Off"):
				if splconfig.SPLConfig["General"]["MessageVerbosity"] == "beginner":
					wavFile = os.path.join(os.path.dirname(__file__), "SPL_off.wav")
					try:
						messageSound(wavFile, msg)
					except Exception:
						pass
				else:
					tones.beep(500, 100)
					braille.handler.message(msg)
			elif msg.endswith("On"):
				if splconfig.SPLConfig["General"]["MessageVerbosity"] == "beginner":
					wavFile = os.path.join(os.path.dirname(__file__), "SPL_on.wav")
					try:
						messageSound(wavFile, msg)
					except Exception:
						pass
				else:
					tones.beep(1000, 100)
					braille.handler.message(msg)
		else:
			ui.message(msg)

	# Perform extra action in specific situations (mic alarm, for example).
	def doExtraAction(self, status):
		# Be sure to only deal with cart mode changes if Cart Explorer is on.
		# Optimization: Return early if the below condition is true.
		if self.cartExplorer and status.startswith("Cart") and status.endswith((" On", " Off")):
			# 17.01: The best way to detect Cart Edit off is consulting file modification time.
			# Automatically reload cart information if this is the case.
			if status in ("Cart Edit Off", "Cart Insert On"):
				self.carts = splmisc.cartExplorerRefresh(api.getForegroundObject().name, self.carts)
			# Translators: Presented when cart modes are toggled while cart explorer is on.
			ui.message(_("Cart explorer is active"))
			return
		# Microphone alarm and alarm interval if defined.
		global micAlarmT, micAlarmT2
		micAlarm = splconfig.SPLConfig["MicrophoneAlarm"]["MicAlarm"]
		# #38 (17.11/15.10-lts): only enter microphone alarm area if alarm should be turned on.
		if not micAlarm:
			if micAlarmT is not None:
				micAlarmT.cancel()
			micAlarmT = None
			if micAlarmT2 is not None:
				micAlarmT2.Stop()
			micAlarmT2 = None
		else:
			# Play an alarm sound (courtesy of Jerry Mader from Mader Radio).
			micAlarmWav = os.path.join(os.path.dirname(__file__), "SPL_MicAlarm.wav")
			# Translators: Presented when microphone was on for more than a specified time in microphone alarm dialog.
			micAlarmMessage = _("Warning: Microphone active")
			# Use a timer to play a tone when microphone was active for more than the specified amount.
			if status == "Microphone On":
				micAlarmT = threading.Timer(micAlarm, micAlarmManager, args=[micAlarmWav, micAlarmMessage])
				try:
					micAlarmT.start()
				except RuntimeError:
					micAlarmT = threading.Timer(micAlarm, messageSound, args=[micAlarmWav, micAlarmMessage])
					micAlarmT.start()
			elif status == "Microphone Off":
				if micAlarmT is not None:
					micAlarmT.cancel()
				micAlarmT = None
				if micAlarmT2 is not None:
					micAlarmT2.Stop()
				micAlarmT2 = None

	# Respond to profile switches if asked.
	def actionProfileSwitched(self):
		# #38 (17.11/15.10-LTS): obtain microphone alarm status.
		if splbase._SPLWin is not None:
			self.doExtraAction(self.sayStatus(2, statusText=True))

	def actionSettingsReset(self, factoryDefaults=False):
		global micAlarmT, micAlarmT2
		# Regardless of factory defaults flag, turn off microphone alarm timers.
		if micAlarmT is not None:
			micAlarmT.cancel()
		micAlarmT = None
		if micAlarmT2 is not None:
			micAlarmT2.Stop()
		micAlarmT2 = None
		if splbase._SPLWin is not None:
			self.doExtraAction(self.sayStatus(2, statusText=True))

	# Alarm announcement: Alarm notification via beeps, speech or both.
	def alarmAnnounce(self, timeText, tone, duration, intro=False):
		if splconfig.SPLConfig["General"]["AlarmAnnounce"] in ("beep", "both"):
			tones.beep(tone, duration)
		if splconfig.SPLConfig["General"]["AlarmAnnounce"] in ("message", "both"):
			alarmTime = int(timeText.split(":")[1])
			if intro:
				# Translators: Presented when end of introduction is approaching (example output: 5 sec left in track introduction).
				ui.message(_("Warning: {seconds} sec left in track introduction").format(seconds=str(alarmTime)))
			else:
				# Translators: Presented when end of track is approaching.
				ui.message(_("Warning: {seconds} sec remaining").format(seconds=str(alarmTime)))

	# Hacks for gain focus events.
	def event_gainFocus(self, obj, nextHandler):
		if self.deletedFocusObj or (obj.windowClassName == "TListView" and obj.role == 0):
			self.deletedFocusObj = False
			return
		nextHandler()

	# Add or remove SPL-specific touch commands.
	# Code comes from Enhanced Touch Gestures add-on from the same author.
	# This may change if NVDA core decides to abandon touch mode concept.

	def event_appModule_gainFocus(self):
		if touchHandler.handler:
			if "SPL" not in touchHandler.availableTouchModes:
				touchHandler.availableTouchModes.append("SPL")
				# Add the human-readable representation also.
				touchHandler.touchModeLabels["spl"] = _("SPL mode")

	def event_appModule_loseFocus(self):
		if touchHandler.handler:
			# Switch to object mode.
			touchHandler.handler._curTouchMode = touchHandler.availableTouchModes[1]
			if "SPL" in touchHandler.availableTouchModes:
				# If we have too many touch modes, pop all except the original entries.
				for mode in touchHandler.availableTouchModes:
					if mode == "SPL":
						touchHandler.availableTouchModes.pop()
			try:
				del touchHandler.touchModeLabels["spl"]
			except KeyError:
				pass

	# React to show events from certain windows.

	def event_show(self, obj, nextHandler):
		if obj.windowClassName == "TRequests" and splconfig.SPLConfig["General"]["RequestsAlert"]:
			nvwave.playWaveFile(os.path.join(os.path.dirname(__file__), "SPL_Requests.wav"))
		nextHandler()

	# Save configuration and perform other tasks when terminating.
	def terminate(self):
		super(AppModule, self).terminate()
		debugOutput("terminating app module")
		# #39 (17.11/15.10-lts): terminate microphone alarm/interval threads, otherwise errors are seen.
		# #40 (17.12): replace this with a handler that responds to app module exit signal.
		# Also allows profile switch handler to unregister itself as well.
		# At the same time, close any opened SPL add-on dialogs.
		splactions.SPLActionProfileSwitched.unregister(self.actionProfileSwitched)
		splactions.SPLActionSettingsReset.unregister(self.actionSettingsReset)
		# 20.09: don't forget about metadata connection announcement handlers.
		splactions.SPLActionProfileSwitched.unregister(splmisc.metadata_actionProfileSwitched)
		splactions.SPLActionSettingsReset.unregister(splmisc.metadata_actionSettingsReset)
		splactions.SPLActionAppTerminating.notify()
		debugOutput("closing microphone alarm/interval thread")
		global micAlarmT, micAlarmT2
		if micAlarmT is not None:
			micAlarmT.cancel()
		micAlarmT = None
		if micAlarmT2 is not None:
			micAlarmT2.Stop()
		micAlarmT2 = None
		debugOutput("saving add-on settings")
		splconfig.terminate()
		# Delete focused track reference.
		self._focusedTrack = None
		# #86: track time analysis marker should be gone, too.
		self._analysisMarker = None
		# #41: We're done monitoring Studio API.
		if self._SPLStudioMonitor is not None:
			self._SPLStudioMonitor.Stop()
			self._SPLStudioMonitor = None
		# #54 (18.04): no more PyDeadObjectError in wxPython 4, so catch ALL exceptions until NVDA stable release with wxPython 4 is out.
		# 18.08: call appropriate Remove function based on wxPython version in use.
		# 18.09: use wx.Menu.Remove directly.
		try:
			self.prefsMenu.Remove(self.SPLSettings)
		except (RuntimeError, AttributeError):
			pass
		# Tell the handle finder thread it's time to leave this world.
		self.noMoreHandle.set()
		# Manually clear the following dictionaries.
		self.carts.clear()
		self._cachedStatusObjs.clear()
		# Don't forget to reset timestamps for cart files.
		splmisc._cartEditTimestamps = [0, 0, 0, 0]
		# Just to make sure:
		if splbase._SPLWin:
			splbase._SPLWin = None
		# 17.10: remove add-on specific command-line switches.
		# This is necessary in order to restore full config functionality when NVDA restarts.
		for cmdSwitch in globalVars.appArgsExtra:
			if cmdSwitch.startswith("--spl-"):
				globalVars.appArgsExtra.remove(cmdSwitch)

	# Script sections (for ease of maintenance):
	# Time-related: elapsed time, end of track alarm, etc.
	# Misc scripts: track finder and others.
	# SPL Assistant layer: status commands.

	# A few time related scripts (elapsed time, remaining time, etc.).

	# Specific to time scripts using Studio API.
	# 6.0: Split this into two functions: the announcer (below) and formatter.
	# 7.0: The ms (millisecond) argument will be used when announcing playlist remainder.
	# 16.12: Include hours by default unless told not to do so.
	def announceTime(self, t, offset=None, ms=True, includeHours=None):
		if t <= 0:
			ui.message("00:00")
		else:
			ui.message(self._ms2time(t, offset=offset, ms=ms, includeHours=includeHours))

	# Formatter: given time in milliseconds, convert it to human-readable format.
	# 7.0: There will be times when one will deal with time in seconds.
	# 16.12: For some cases, do not include hour slot when trying to conform to what Studio displays.)
	def _ms2time(self, t, offset=None, ms=True, includeHours=None):
		if t <= 0:
			return "00:00"
		else:
			if ms:
				# 19.11.1/18.09.13-LTS: be sure to convert time into integer indirectly via floor division for maximum compatibility between Python 2 and 3.
				t = (t // 1000) if not offset else (t // 1000) + offset
			mm, ss = divmod(t, 60)
			if mm > 59 and (includeHours or (includeHours is None and splconfig.SPLConfig["General"]["TimeHourAnnounce"])):
				hh, mm = divmod(mm, 60)
				# Hour value is also filled with leading zero's.
				# 6.1: Optimize the string builder so it can return just one string.
				# 17.08: Return the generated string directly.
				# 17.09: use modulo formatter to reduce instruction count.
				return "{hh:02d}:{mm:02d}:{ss:02d}".format(hh=hh, mm=mm, ss=ss)
			else:
				return "{mm:02d}:{ss:02d}".format(mm=mm, ss=ss)

	# Scripts which rely on API.
	@scriptHandler.script(
		# Message comes from Foobar 2000 app module, part of NVDA Core.
		description=translate("Reports the remaining time of the currently playing track, if any"),
		gestures=["kb:control+alt+t", "ts(SPL):2finger_flickDown"])
	def script_sayRemainingTime(self, gesture):
		if splbase.studioIsRunning():
			self.announceTime(splbase.studioAPI(3, 105), offset=1)

	@scriptHandler.script(
		# Message comes from Foobar 2000 app module, part of NVDA Core.
		description=translate("Reports the elapsed time of the currently playing track, if any"),
		gesture="kb:alt+shift+t")
	def script_sayElapsedTime(self, gesture):
		if splbase.studioIsRunning():
			self.announceTime(splbase.studioAPI(0, 105))

	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Announces broadcaster time. If pressed twice, reports minutes and seconds left to top of the hour."),
		gestures=["kb:shift+nvda+f12", "ts(SPL):2finger_flickUp"])
	def script_sayBroadcasterTime(self, gesture):
		if not splbase.studioIsRunning():
			return
		# Says things such as "25 minutes to 2" and "5 past 11".
		# #29: Also announces top of hour timer (mm:ss), the clock next to broadcaster time.
		# Parse the local time and say it similar to how Studio presents broadcaster time.
		localtime = time.localtime()
		# For both broadcaster time and top of hour, minute is needed.
		m = localtime[4]
		if scriptHandler.getLastScriptRepeatCount() == 0:
			h = localtime[3]
			if h not in (0, 12):
				h %= 12
			if m == 0:
				if h == 0:
					h += 12
				# Messages in this method should not be translated.
				ui.message("{hour} o'clock".format(hour=h))
			elif 1 <= m <= 30:
				if h == 0:
					h += 12
				ui.message("{minute} min past {hour}".format(minute=m, hour=h))
			else:
				if h == 12:
					h = 1
				m = 60 - m
				ui.message("{minute} min to {hour}".format(minute=m, hour=h + 1))
		else:
			self.announceTime(3600 - (m * 60 + localtime[5]), ms=False)

	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Announces time including seconds."))
	def script_sayCompleteTime(self, gesture):
		if not splbase.studioIsRunning():
			return
		import winKernel
		# Says complete time in hours, minutes and seconds via kernel32's routines.
		ui.message(winKernel.GetTimeFormat(winKernel.LOCALE_USER_DEFAULT, 0, None, None))

	# Show the Alarms panel in add-on settings screen.

	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Opens SPL Studio alarms settings."),
		gestures=["kb:alt+nvda+1", "ts(SPL):2finger_flickRight"])
	def script_openAlarmsSettings(self, gesture):
		wx.CallAfter(splconfui.openAddonSettingsPanel, splconfui.AlarmsPanel)

	# SPL Config management among others.

	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Opens SPL Studio add-on configuration dialog."),
		gesture="kb:alt+NVDA+0")
	def script_openConfigDialog(self, gesture):
		# 20.05: rather than calling the config dialog open event, call the open dialog function directly to avoid indirection.
		wx.CallAfter(splconfui.openAddonSettingsPanel, None)

	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Opens SPL add-on broadcast profiles dialog."),
		gesture="kb:alt+NVDA+p")
	def script_openBroadcastProfilesDialog(self, gesture):
		wx.CallAfter(splconfui.onBroadcastProfilesDialog, None)

	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Opens SPL Studio add-on welcome dialog."),
		gesture="kb:alt+NVDA+f1")
	def script_openWelcomeDialog(self, gesture):
		gui.mainFrame.prePopup()
		splconfig.WelcomeDialog(gui.mainFrame).Show()
		gui.mainFrame.postPopup()

	# Other commands (track finder and others)

	# Braille timer.
	# Announce end of track and other info via braille.

	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Toggles between various braille timer settings."),
		gesture="kb:control+shift+x")
	def script_setBrailleTimer(self, gesture):
		brailleTimer = splconfig.SPLConfig["General"]["BrailleTimer"]
		if brailleTimer == "off":
			brailleTimer = "outro"
		elif brailleTimer == "outro":
			brailleTimer = "intro"
		elif brailleTimer == "intro":
			brailleTimer = "both"
		else:
			brailleTimer = "off"
		splconfig.SPLConfig["General"]["BrailleTimer"] = brailleTimer
		splconfig.message("BrailleTimer", brailleTimer)

	# The track finder utility for find track script and other functions
	# Perform a linear search to locate the track name and/or description which matches the entered value.
	# Also, find column content for a specific column if requested.
	# 6.0: Split this routine into two functions, with the while loop moving to a function of its own.
	# This new function will be used by track finder and place marker locator.
	# 17.08: now it is a list that records search history.
	findText = None

	def trackFinder(self, text, obj, directionForward=True, column=None):
		speech.cancelSpeech()
		# #32 (17.06/15.8 LTS): Update search text even if the track with the search term in columns does not exist.
		# #27 (17.08): especially if the search history is empty.
		# Thankfully, track finder dialog will populate the first item, but it is better to check a second time for debugging purposes.
		if self.findText is None:
			self.findText = []
		if text not in self.findText:
			self.findText.insert(0, text)
		# #33 (17.06/15.8-LTS): In case the track is NULL (seen when attempting to perform forward search from the last track and what not), this function should fail instead of raising attribute error.
		if obj is not None and column is None:
			column = [obj.indexOf("Artist"), obj.indexOf("Title")]
		track = self._trackLocator(text, obj=obj, directionForward=directionForward, columns=column)
		if track:
			# We need to fire set focus event twice and exit this routine (return if 5.0x).
			# 16.10.1/15.2 LTS: Just select this track in order to prevent a dispute between NVDA and SPL in regards to focused track.
			# 16.11: Call setFocus if it is post-5.01, as SPL API can be used to select the desired track.
			# 20.09: doAction method will do this instead.
			track.doAction()
		else:
			# Translators: Standard dialog message when an item one wishes to search is not found (copy this from main nvda.po).
			wx.CallAfter(gui.messageBox, _("Search string not found."), translate("Find Error"), wx.OK | wx.ICON_ERROR)

	# Split from track finder in 2015.
	# Return a track with the given search criteria.
	# Column is a list of columns to be searched (if none, it'll be artist and title).
	def _trackLocator(self, text, obj=api.getFocusObject(), directionForward=True, columns=None):
		nextTrack = "next" if directionForward else "previous"
		while obj is not None:
			# Do not use column content attribute, because sometimes NVDA will say it isn't a track item when in fact it is.
			# If this happens, use the module level version of column content getter.
			# Optimization: search column texts.
			for column in columns:
				columnText = obj._getColumnContentRaw(column)
				if columnText and text in columnText:
					return obj
			obj = getattr(obj, nextTrack)
		return None

	# Find a specific track based on a searched text.
	# But first, check if track finder can be invoked.
	# Attempt level specifies which track finder to open (0 = Track Finder, 1 = Column Search, 2 = Time range).
	def _trackFinderCheck(self, attemptLevel):
		if not splbase.studioIsRunning():
			return False
		playlistErrors = self.canPerformPlaylistCommands(announceErrors=False)
		if playlistErrors == self.SPLPlaylistNotFocused:
			if attemptLevel == 0:
				# Translators: Presented when a user attempts to find tracks but is not at the track list.
				ui.message(_("Track finder is available only in track list."))
			elif attemptLevel == 1:
				# Translators: Presented when a user attempts to find tracks but is not at the track list.
				ui.message(_("Column search is available only in track list."))
			elif attemptLevel == 2:
				# Translators: Presented when a user attempts to find tracks but is not at the track list.
				ui.message(_("Time range finder is available only in track list."))
			return False
		# 17.06/15.8-LTS: use Studio API to find out if a playlist is even loaded, otherwise Track Finder will fail to notice a playlist.
		# #81 (18.12): all taken care of by playlist checker method.
		elif playlistErrors == self.SPLPlaylistNotLoaded:
			# Translators: Presented when a user wishes to find a track but didn't add any tracks.
			ui.message(_("You need to add at least one track to find tracks."))
			return False
		return True

	def trackFinderGUI(self, columnSearch=False):
		try:
			if not columnSearch:
				# Translators: Title for track finder dialog.
				title = _("Find track")
			else:
				# Translators: Title for column search dialog.
				title = _("Column search")
			startObj = api.getFocusObject()
			if api.getForegroundObject().windowClassName == "TStudioForm" and startObj.role == controlTypes.ROLE_LIST:
				startObj = startObj.firstChild
			d = splmisc.SPLFindDialog(gui.mainFrame, startObj, self.findText[0] if self.findText and len(self.findText) else "", title, columnSearch=columnSearch)
			gui.mainFrame.prePopup()
			d.Raise()
			d.Show()
			gui.mainFrame.postPopup()
			splmisc._findDialogOpened = True
		except RuntimeError:
			wx.CallAfter(splmisc._finderError)

	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Finds a track in the track list."),
		gesture="kb:control+nvda+f")
	def script_findTrack(self, gesture):
		if self._trackFinderCheck(0):
			self.trackFinderGUI()

	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Finds text in columns."))
	def script_columnSearch(self, gesture):
		if self._trackFinderCheck(1):
			self.trackFinderGUI(columnSearch=True)

	# Find next and previous scripts.

	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Finds the next occurrence of the track with the name in the track list."),
		gesture="kb:nvda+f3")
	def script_findTrackNext(self, gesture):
		if self._trackFinderCheck(0):
			if self.findText is None:
				self.trackFinderGUI()
			else:
				startObj = api.getFocusObject()
				if api.getForegroundObject().windowClassName == "TStudioForm" and startObj.role == controlTypes.ROLE_LIST:
					startObj = startObj.firstChild
				self.trackFinder(self.findText[0], obj=startObj.next)

	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Finds previous occurrence of the track with the name in the track list."),
		gesture="kb:shift+nvda+f3")
	def script_findTrackPrevious(self, gesture):
		if self._trackFinderCheck(0):
			if self.findText is None:
				self.trackFinderGUI()
			else:
				startObj = api.getFocusObject()
				if api.getForegroundObject().windowClassName == "TStudioForm" and startObj.role == controlTypes.ROLE_LIST:
					startObj = startObj.lastChild
				self.trackFinder(self.findText[0], obj=startObj.previous, directionForward=False)

	# Time range finder.
	# Locate a track with duration falling between min and max.

	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Locates track with duration within a time range"))
	def script_timeRangeFinder(self, gesture):
		if self._trackFinderCheck(2):
			try:
				d = splmisc.SPLTimeRangeDialog(gui.mainFrame, api.getFocusObject())
				gui.mainFrame.prePopup()
				d.Raise()
				d.Show()
				gui.mainFrame.postPopup()
				splmisc._findDialogOpened = True
			except RuntimeError:
				wx.CallAfter(splmisc._finderError)

	# Cart explorer
	cartExplorer = False
	# The carts dictionary (key = cart gesture, item = cart name).
	carts = {}

	# Assigning carts.

	def buildFNCarts(self):
		for i in range(12):
			self.bindGesture("kb:f{}".format(i + 1), "cartExplorer")
			self.bindGesture("kb:shift+f{}".format(i + 1), "cartExplorer")
			self.bindGesture("kb:control+f{}".format(i + 1), "cartExplorer")
			self.bindGesture("kb:alt+f{}".format(i + 1), "cartExplorer")

	def buildNumberCarts(self):
		# It is much faster to work directly with number row keys.
		for i in "1234567890-=":
			self.bindGesture("kb:{}".format(i), "cartExplorer")
			self.bindGesture("kb:shift+{}".format(i), "cartExplorer")
			self.bindGesture("kb:control+{}".format(i), "cartExplorer")
			self.bindGesture("kb:alt+{}".format(i), "cartExplorer")

	def cartsBuilder(self, build=True):
		# A function to build and return cart commands.
		# #147 (20.10): fetch cart keys from a dedicated tuple found in splmisc module.
		if build:
			for cart in splmisc.cartKeys:
				self.bindGesture(f"kb:{cart}", "cartExplorer")
				self.bindGesture(f"kb:shift+{cart}", "cartExplorer")
				self.bindGesture(f"kb:control+{cart}", "cartExplorer")
				self.bindGesture(f"kb:alt+{cart}", "cartExplorer")
		else:
			self.clearGestureBindings()
			self.bindGestures(self.__gestures)

	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Toggles cart explorer to learn cart assignments."),
		gesture="kb:alt+nvda+3")
	def script_toggleCartExplorer(self, gesture):
		if not splbase.studioIsRunning():
			return
		if not self.cartExplorer:
			# Prevent cart explorer from being engaged outside of playlist viewer.
			# Todo for 6.0: Let users set cart banks.
			fg = api.getForegroundObject()
			if fg.windowClassName != "TStudioForm":
				# Translators: Presented when cart explorer cannot be entered.
				ui.message(_("You are not in playlist viewer, cannot enter cart explorer"))
				return
			self.carts = splmisc.cartExplorerInit(fg.name)
			if self.carts["faultyCarts"]:
				# Translators: presented when cart explorer could not be switched on.
				ui.message(_("Some or all carts could not be assigned, cannot enter cart explorer"))
				return
			else:
				self.cartExplorer = True
				self.cartsBuilder()
				# Translators: Presented when cart explorer is on.
				ui.message(_("Entering cart explorer"))
		else:
			self.cartExplorer = False
			self.cartsBuilder(build=False)
			self.carts.clear()
			splmisc._cartEditTimestamps = None
			# Translators: Presented when cart explorer is off.
			ui.message(_("Exiting cart explorer"))

	def script_cartExplorer(self, gesture):
		if api.getForegroundObject().windowClassName != "TStudioForm":
			gesture.send()
			return
		if scriptHandler.getLastScriptRepeatCount() >= 1:
			gesture.send()
		else:
			if gesture.displayName in self.carts:
				ui.message(self.carts[gesture.displayName])
			elif self.carts["standardLicense"] and (len(gesture.displayName) == 1 or gesture.displayName[-2] == "+"):
				# Translators: Presented when cart command is unavailable.
				ui.message(_("Cart command unavailable"))
			else:
				# Translators: Presented when there is no cart assigned to a cart command.
				ui.message(_("Cart unassigned"))

	# Library scan announcement
	# Announces progress of a library scan (launched from insert tracks dialog by pressing Control+Shift+R or from rescan option from Options dialog).

	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Toggles library scan progress settings."),
		gesture="kb:alt+nvda+r")
	def script_setLibraryScanProgress(self, gesture):
		libraryScanAnnounce = splconfig.SPLConfig["General"]["LibraryScanAnnounce"]
		if libraryScanAnnounce == "off":
			libraryScanAnnounce = "ending"
		elif libraryScanAnnounce == "ending":
			libraryScanAnnounce = "progress"
		elif libraryScanAnnounce == "progress":
			libraryScanAnnounce = "numbers"
		else:
			libraryScanAnnounce = "off"
		splconfig.SPLConfig["General"]["LibraryScanAnnounce"] = libraryScanAnnounce
		splconfig.message("LibraryScanAnnounce", libraryScanAnnounce)

	@scriptHandler.script(gesture="kb:control+shift+r")
	def script_startScanFromInsertTracks(self, gesture):
		gesture.send()
		fg = api.getForegroundObject()
		if fg.windowClassName == "TTrackInsertForm":
			# Translators: Presented when library scan has started.
			ui.message(_("Scan start")) if not splconfig.SPLConfig["General"]["BeepAnnounce"] else tones.beep(740, 100)
			if self.productVersion not in noLibScanMonitor:
				self.libraryScanning = True

	# Report library scan (number of items scanned) in the background.
	def monitorLibraryScan(self):
		global libScanT
		if libScanT and libScanT.is_alive() and api.getForegroundObject().windowClassName == "TTrackInsertForm":
			return
		if splbase.studioAPI(1, 32) < 0:
			self.libraryScanning = False
			return
		time.sleep(0.1)
		if api.getForegroundObject().windowClassName == "TTrackInsertForm" and self.productVersion in noLibScanMonitor:
			self.libraryScanning = False
			return
		# 17.04: Library scan may have finished while this thread was sleeping.
		if splbase.studioAPI(1, 32) < 0:
			self.libraryScanning = False
			# Translators: Presented when library scanning is finished.
			ui.message(_("{itemCount} items in the library").format(itemCount=splbase.studioAPI(0, 32)))
		else:
			libScanT = threading.Thread(target=self.libraryScanReporter)
			libScanT.daemon = True
			libScanT.start()

	def libraryScanReporter(self):
		scanIter = 0
		# 17.04: Use the constant directly, as 5.10 and later provides a convenient method to detect completion of library scans.
		scanCount = splbase.studioAPI(1, 32)
		while scanCount >= 0:
			if not self.libraryScanning or not user32.FindWindowW("SPLStudio", None):
				return
			time.sleep(1)
			# Do not continue if we're back on insert tracks form or library scan is finished.
			if api.getForegroundObject().windowClassName == "TTrackInsertForm" or not self.libraryScanning:
				return
			# Scan count may have changed during sleep.
			scanCount = splbase.studioAPI(1, 32)
			if scanCount < 0:
				break
			scanIter += 1
			if scanIter % 5 == 0 and splconfig.SPLConfig["General"]["LibraryScanAnnounce"] not in ("off", "ending"):
				self._libraryScanAnnouncer(scanCount, splconfig.SPLConfig["General"]["LibraryScanAnnounce"])
		self.libraryScanning = False
		# 18.04: what if config database died?
		if splconfig.SPLConfig and splconfig.SPLConfig["General"]["LibraryScanAnnounce"] != "off":
			if splconfig.SPLConfig["General"]["BeepAnnounce"]:
				tones.beep(370, 100)
			else:
				# Translators: Presented after library scan is done.
				ui.message(_("Scan complete with {itemCount} items").format(itemCount=splbase.studioAPI(0, 32)))

	# Take care of library scanning announcement.
	def _libraryScanAnnouncer(self, count, announcementType):
		if announcementType == "progress":
			# Translators: Presented when library scan is in progress.
			tones.beep(550, 100) if splconfig.SPLConfig["General"]["BeepAnnounce"] else ui.message(_("Scanning"))
		elif announcementType == "numbers":
			if splconfig.SPLConfig["General"]["BeepAnnounce"]:
				tones.beep(550, 100)
				# No need to provide translatable string - just use index.
				ui.message("{0}".format(count))
			else:
				# Translators: Presented when library scan is in progress.
				ui.message(_("{itemCount} items scanned").format(itemCount=count))

	# Place markers.
	placeMarker = None

	# Is the place marker set on this track?
	# Track argument is None (only useful for debugging purposes).
	def isPlaceMarkerTrack(self, track=None):
		if track is None:
			track = api.getFocusObject()
		# 20.07: no, only list items can become place marker tracks.
		if track.role != controlTypes.ROLE_LISTITEM:
			raise ValueError("Only list items can be marked as a place marker track")
		index = track.indexOf("Filename")
		filename = track._getColumnContentRaw(index)
		if self.placeMarker == (index, filename):
			return True
		return False

	# Used in delete track workaround routine.
	def preTrackRemoval(self):
		try:
			if self.isPlaceMarkerTrack(track=api.getFocusObject()):
				self.placeMarker = None
		except ValueError:
			pass

	# Metadata streaming manager
	# Obtains information on metadata streaming for each URL, notifying the broadcaster if told to do so upon startup.
	# Also allows broadcasters to toggle metadata streaming.

	# The script version to open the manage metadata URL's dialog.
	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Opens a dialog to quickly enable or disable metadata streaming."))
	def script_manageMetadataStreams(self, gesture):
		# Do not even think about opening this dialog if handle to Studio isn't found.
		if splbase._SPLWin is None:
			# Translators: Presented when streaming dialog cannot be shown.
			ui.message(_("Cannot open metadata streaming dialog"))
			return
		if splconfui._configDialogOpened:
			# #125 (20.04) temporary: call centralized error handler.
			wx.CallAfter(splconfui._configDialogOpenError)
			return
		try:
			# #44 (18.02): do not rely on Studio API function object as its workings (including arguments) may change.
			# Use a flag to tell the streaming dialog that this is invoked from somewhere other than add-on settings dialog.
			d = splconfui.MetadataStreamingDialog(gui.mainFrame)
			gui.mainFrame.prePopup()
			d.Raise()
			d.Show()
			gui.mainFrame.postPopup()
			splconfui._configDialogOpened = True
		except RuntimeError:
			pass

	# Playlist Analyzer
	# These include track time analysis, playlist snapshots, and some form of playlist transcripts and others.
	# Although not directly related to this, track finder and its friends, as well as remaining playlist duration command also fall under playlist analyzer.
	# A playlist must be loaded and visible in order for these to work, or for some, most recent focused track must be known.

	# Possible playlist errors.
	SPLPlaylistNoErrors = 0
	SPLPlaylistNotFocused = 1
	SPLPlaylistNotLoaded = 2
	SPLPlaylistLastFocusUnknown = 3

	def canPerformPlaylistCommands(self, playlistViewerRequired=True, mustSelectTrack=False, announceErrors=True):
		# #81: most commands do require that playlist viewer must be the foreground window (focused), hence the keyword argument.
		# Also let NvDA announce generic error messages listed below if told to do so, and for some cases, not at all because the caller will announce them.
		playlistViewerFocused = api.getForegroundObject().windowClassName == "TStudioForm"
		if playlistViewerRequired and not playlistViewerFocused:
			if announceErrors:
				# Translators: an error message presented when performing some playlist commands while focused on places other than Playlist Viewer.
				ui.message(_("Please return to playlist viewer before invoking this command."))
			return self.SPLPlaylistNotFocused
		if not splbase.studioAPI(0, 124):
			if announceErrors:
				# Translators: an error message presented when performing some playlist commands while no playlist has been loaded.
				ui.message(_("No playlist has been loaded."))
			return self.SPLPlaylistNotLoaded
		if mustSelectTrack and self._focusedTrack is None:
			if announceErrors:
				# Translators: an error message presented when performing some playlist commands while no tracks are selected/focused.
				ui.message(_("Please select a track from playlist viewer before invoking this command."))
			return self.SPLPlaylistLastFocusUnknown
		return self.SPLPlaylistNoErrors

	# Track time analysis/Playlist snapshots
	# Return total length of the selected tracks upon request.
	# Analysis command (SPL Assistant) will be assignable.
	# Also gather various data about the playlist.
	_analysisMarker = None

	# Trakc time analysis and playlist snapshots, and to some extent, some parts of playlist transcripts  require main playlist viewer to be the foreground window.
	# Track time analysis does require knowing the start and ending track, while others do not.
	def _trackAnalysisAllowed(self, mustSelectTrack=True):
		if not splbase.studioIsRunning():
			return False
		# #81 (18.12): just return result of consulting playlist dispatch along with error messages if any.
		playlistErrors = self.canPerformPlaylistCommands(mustSelectTrack=mustSelectTrack, announceErrors=False)
		if playlistErrors == self.SPLPlaylistNotFocused:
			# Translators: Presented when playlist analyzer cannot be performed because user is not focused on playlist viewer.
			ui.message(_("Not in playlist viewer, cannot perform playlist analysis."))
			return False
		elif playlistErrors == self.SPLPlaylistNotLoaded:
			# Translators: reported when no playlist has been loaded when trying to perform playlist analysis.
			ui.message(_("No playlist to analyze."))
			return False
		elif playlistErrors == self.SPLPlaylistLastFocusUnknown:
			# Translators: Presented when playlist analysis cannot be activated.
			ui.message(_("No tracks are selected, cannot perform playlist analysis."))
			return False
		return True

	# Return total duration of a range of tracks.
	# This is used in track time analysis when multiple tracks are selected.
	# This is also called from playlist duration scripts.
	def playlistDuration(self, start=None, end=None):
		if start is None:
			start = api.getFocusObject()
		duration = start.indexOf("Duration")
		totalDuration = 0
		obj = start
		while obj not in (None, end):
			# Technically segue.
			segue = obj._getColumnContentRaw(duration)
			if segue not in (None, "00:00"):
				hms = segue.split(":")
				totalDuration += (int(hms[-2]) * 60) + int(hms[-1])
				if len(hms) == 3:
					totalDuration += int(hms[0]) * 3600
			obj = obj.next
		return totalDuration

	# Playlist snapshots
	# Data to be gathered comes from a set of flags.
	# By default, playlist duration (including shortest and average), category summary and other statistics will be gathered.
	def playlistSnapshots(self, obj, end, snapshotFlags=None):
		# #55 (18.05): is this a complete snapshot?
		completePlaylistSnapshot = obj.IAccessibleChildID == 1 and end is None
		# Track count and total duration are always included.
		snapshot = {}
		if snapshotFlags is None:
			snapshotFlags = [flag for flag in splconfig.SPLConfig["PlaylistSnapshots"] if splconfig.SPLConfig["PlaylistSnapshots"][flag]]
		duration = obj.indexOf("Duration")
		title = obj.indexOf("Title")
		artist = obj.indexOf("Artist")
		artists = []
		min, max = None, None
		minTitle, maxTitle = None, None
		totalDuration = 0
		category = obj.indexOf("Category")
		categories = []
		genre = obj.indexOf("Genre")
		genres = []
		# A specific version of the playlist duration loop is needed in order to gather statistics.
		while obj not in (None, end):
			segue = obj._getColumnContentRaw(duration)
			trackTitle = obj._getColumnContentRaw(title)
			categories.append(obj._getColumnContentRaw(category))
			# Don't record artist and genre information for an hour marker (reported by a broadcaster).
			if categories[-1] != "Hour Marker":
				artists.append(obj._getColumnContentRaw(artist))
				genres.append(obj._getColumnContentRaw(genre))
			# Shortest and longest tracks.
			# #22: assign min to the first segue in order to not forget title of the shortest track.
			if segue and (min is None or segue < min):
				min = segue
				minTitle = trackTitle
			# 19.11.1/18.09.13-LTS: also do the same for max as Python 3 does not allow comparison between objects and None.
			if segue and (max is None or segue > max):
				max = segue
				maxTitle = trackTitle
			if segue not in (None, "00:00"):
				hms = segue.split(":")
				totalDuration += (int(hms[-2]) * 60) + int(hms[-1])
				if len(hms) == 3:
					totalDuration += int(hms[0]) * 3600
			obj = obj.next
		# #55 (18.05): use total track count if it is an entire playlist, if not, resort to categories count.
		if completePlaylistSnapshot:
			snapshot["PlaylistItemCount"] = splbase.studioAPI(0, 124)
		else:
			snapshot["PlaylistItemCount"] = len(categories)
		snapshot["PlaylistTrackCount"] = len(artists)
		snapshot["PlaylistDurationTotal"] = self._ms2time(totalDuration, ms=False)
		if "DurationMinMax" in snapshotFlags:
			snapshot["PlaylistDurationMin"] = "{} ({})".format(minTitle, min)
			snapshot["PlaylistDurationMax"] = "{} ({})".format(maxTitle, max)
		if "DurationAverage" in snapshotFlags:
			# #57 (18.04): zero division error may occur if the playlist consists of hour markers only.
			try:
				# 19.11.1/18.09.13-LTS: track count is an integer, so use floor division.
				snapshot["PlaylistDurationAverage"] = self._ms2time(totalDuration // snapshot["PlaylistTrackCount"], ms=False)
			except ZeroDivisionError:
				snapshot["PlaylistDurationAverage"] = "00:00"
		if "CategoryCount" in snapshotFlags or "ArtistCount" in snapshotFlags or "GenreCount" in snapshotFlags:
			import collections
			if "CategoryCount" in snapshotFlags:
				snapshot["PlaylistCategoryCount"] = collections.Counter(categories)
			if "ArtistCount" in snapshotFlags:
				snapshot["PlaylistArtistCount"] = collections.Counter(artists)
			if "GenreCount" in snapshotFlags:
				snapshot["PlaylistGenreCount"] = collections.Counter(genres)
		return snapshot

	# Output formatter for playlist snapshots.
	# Pressing once will speak and/or braille it, pressing twice or more will output this info to an HTML file.

	def playlistSnapshotOutput(self, snapshot, scriptCount):
		# Translators: one of the results for playlist snapshots feature for announcing total number of items in a playlist.
		statusInfo = [_("Items: {playlistItemCount}").format(playlistItemCount=snapshot["PlaylistItemCount"])]
		# Translators: one of the results for playlist snapshots feature for announcing total number of tracks in a playlist.
		statusInfo.append(_("Tracks: {playlistTrackCount}").format(playlistTrackCount=snapshot["PlaylistTrackCount"]))
		# Translators: one of the results for playlist snapshots feature for announcing total duration of a playlist.
		statusInfo.append(_("Duration: {playlistTotalDuration}").format(playlistTotalDuration=snapshot["PlaylistDurationTotal"]))
		if "PlaylistDurationMin" in snapshot:
			# Translators: one of the results for playlist snapshots feature for announcing shortest track name and duration of a playlist.
			statusInfo.append(_("Shortest: {playlistShortestTrack}").format(playlistShortestTrack=snapshot["PlaylistDurationMin"]))
			# Translators: one of the results for playlist snapshots feature for announcing longest track name and duration of a playlist.
			statusInfo.append(_("Longest: {playlistLongestTrack}").format(playlistLongestTrack=snapshot["PlaylistDurationMax"]))
		if "PlaylistDurationAverage" in snapshot:
			# Translators: one of the results for playlist snapshots feature for announcing average duration for tracks in a playlist.
			statusInfo.append(_("Average: {playlistAverageDuration}").format(playlistAverageDuration=snapshot["PlaylistDurationAverage"]))
		# 20.09 optimization: for top artists and genres, report statistics if there is an actual common entries counter.
		if "PlaylistArtistCount" in snapshot:
			artistCount = splconfig.SPLConfig["PlaylistSnapshots"]["ArtistCountLimit"]
			artists = snapshot["PlaylistArtistCount"].most_common(None if not artistCount else artistCount)
			if scriptCount == 0:
				try:
					# Translators: one of the results for playlist snapshots feature for announcing top artist in a playlist.
					statusInfo.append(_("Top artist: {} ({})").format(artists[0][0], artists[0][1]))
				except IndexError:
					# Translators: one of the results for playlist snapshots feature when there is no top artist.
					statusInfo.append(_("Top artist: none"))
			elif scriptCount == 1:
				if len(artists) == 0:
					# Translators: one of the results for playlist snapshots feature when there is no top artist (formatted for browse mode).
					statusInfo.append(_("Top artists: none"))
				else:
					artistList = []
					# Translators: one of the results for playlist snapshots feature, a heading for a group of items.
					header = _("Top artists:")
					for item in artists:
						artist, count = item
						if artist is None:
							# Translators: one of the results for playlist snapshots feature when there is no artist information.
							info = _("No artist information ({artistCount})").format(artistCount=count)
						else:
							# Translators: one of the results for playlist snapshots feature for artist count information.
							info = _("{artistName} ({artistCount})").format(artistName=artist, artistCount=count)
						artistList.append("<li>{}</li>".format(info))
					statusInfo.append("".join([header, "<ol>", "\n".join(artistList), "</ol>"]))
		if "PlaylistCategoryCount" in snapshot:
			categoryCount = splconfig.SPLConfig["PlaylistSnapshots"]["CategoryCountLimit"]
			categories = snapshot["PlaylistCategoryCount"].most_common(None if not categoryCount else categoryCount)
			if scriptCount == 0:
				# Translators: one of the results for playlist snapshots feature for announcing top track category in a playlist.
				statusInfo.append(_("Top category: {} ({})").format(categories[0][0], categories[0][1]))
			elif scriptCount == 1:
				categoryList = []
				# Translators: one of the results for playlist snapshots feature, a heading for a group of items.
				header = _("Categories:")
				for item in categories:
					category, count = item
					category = category.replace("<", "")
					category = category.replace(">", "")
					info = _("{categoryName} ({categoryCount})").format(categoryName=category, categoryCount=count)
					categoryList.append("<li>{}</li>".format(info))
				statusInfo.append("".join([header, "<ol>", "\n".join(categoryList), "</ol>"]))
		if "PlaylistGenreCount" in snapshot:
			genreCount = splconfig.SPLConfig["PlaylistSnapshots"]["GenreCountLimit"]
			genres = snapshot["PlaylistGenreCount"].most_common(None if not genreCount else genreCount)
			if scriptCount == 0:
				try:
					# Translators: one of the results for playlist snapshots feature for announcing top genre in a playlist.
					statusInfo.append(_("Top genre: {} ({})").format(genres[0][0], genres[0][1]))
				except IndexError:
					# Translators: one of the results for playlist snapshots feature when there is no top genre.
					statusInfo.append(_("Top genre: none"))
			elif scriptCount == 1:
				if len(genres) == 0:
					# Translators: one of the results for playlist snapshots feature when there is no top genre (formatted for browse mode).
					statusInfo.append(_("Top genres: none"))
				else:
					genreList = []
					# Translators: one of the results for playlist snapshots feature, a heading for a group of items.
					header = _("Top genres:")
					for item in genres:
						genre, count = item
						if genre is None:
							# Translators: one of the results for playlist snapshots feature when there is no genre information for an item.
							info = _("No genre information ({genreCount})").format(genreCount=count)
						else:
							# Translators: one of the results for playlist snapshots feature for genre count information.
							info = _("{genreName} ({genreCount})").format(genreName=genre, genreCount=count)
						genreList.append("<li>{}</li>".format(info))
					statusInfo.append("".join([header, "<ol>", "\n".join(genreList), "</ol>"]))
		if scriptCount == 0:
			ui.message(", ".join(statusInfo))
		else:
			# Translators: The title of a window for displaying playlist snapshots information.
			ui.browseableMessage("<p>".join(statusInfo), title=_("Playlist snapshots"), isHtml=True)

	# Some handlers for native commands.

	# In Studio 5.0x, when deleting a track, NVDA announces wrong track item due to focus bouncing (not the case in 5.10 and later).
	# The below hack is sensitive to changes in NVDA core.
	deletedFocusObj = False

	@scriptHandler.script(gestures=["kb:Shift+delete", "kb:Shift+numpadDelete"])
	def script_deleteTrack(self, gesture):
		self.preTrackRemoval()
		gesture.send()

	# When Escape is pressed, activate background library scan if conditions are right.
	@scriptHandler.script(gesture="kb:escape")
	def script_escape(self, gesture):
		gesture.send()
		if self.libraryScanning:
			if not libScanT or (libScanT and not libScanT.is_alive()):
				self.monitorLibraryScan()

	# The developer would like to get feedback from you.
	@scriptHandler.script(
		description="Opens the default email client to send an email to the add-on developer",
		gesture="kb:alt+nvda+-")
	def script_sendFeedbackEmail(self, gesture):
		os.startfile("mailto:joseph.lee22590@gmail.com")

	# SPL Assistant: reports status on playback, operation, etc.
	# Used layer command approach to save gesture assignments.
	# Most were borrowed from JFW and Window-Eyes layer scripts (Window-Eyes command layout removed in 2020).

	# Set up the layer script environment.
	def getScript(self, gesture):
		if not self.SPLAssistant:
			return appModuleHandler.AppModule.getScript(self, gesture)
		script = appModuleHandler.AppModule.getScript(self, gesture)
		if not script:
			script = self.script_error
		return finally_(script, self.finish)

	def finish(self):
		self.SPLAssistant = False
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)
		if self.cartExplorer:
			self.cartsBuilder()

	def script_error(self, gesture):
		tones.beep(120, 100)
		self.finish()

	# SPL Assistant flag.
	SPLAssistant = False

	# The SPL Assistant layer driver.

	@scriptHandler.script(
		# Translators: Input help mode message for a layer command in StationPlaylist add-on.
		description=_("The SPL Assistant layer command. See the add-on guide for more information on available commands."))
	def script_SPLAssistantToggle(self, gesture):
		# Enter the layer command if an only if we're in the track list to allow easier gesture assignment.
		# 7.0: This requirement has been relaxed (commands themselves will check for specific conditions).
		# Also, do not bother if the app module is not running.
		if scriptHandler.getLastScriptRepeatCount() > 0:
			gesture.send()
			self.finish()
			return
		try:
			# 7.0: Don't bother if handle to Studio isn't found.
			if splbase._SPLWin is None:
				# Translators: Presented when SPL Assistant cannot be invoked.
				ui.message(_("Failed to locate Studio main window, cannot enter SPL Assistant"))
				return
			if self.SPLAssistant:
				self.script_error(gesture)
				return
			# To prevent entering wrong gesture while the layer is active.
			self.clearGestureBindings()
			# 7.0: choose the required compatibility layer.
			if splconfig.SPLConfig["Advanced"]["CompatibilityLayer"] == "off":
				self.bindGestures(self.__SPLAssistantGestures)
			elif splconfig.SPLConfig["Advanced"]["CompatibilityLayer"] == "jfw":
				self.bindGestures(self.__SPLAssistantJFWGestures)
			for i in range(5):
				self.bindGesture(f"kb:shift+{i}", "metadataEnabled")
			self.SPLAssistant = True
			tones.beep(512, 50)
			if splconfig.SPLConfig["Advanced"]["CompatibilityLayer"] == "jfw":
				ui.message("JAWS")
		except WindowsError:
			return

	# Status table keys
	SPLSystemStatus = 1
	SPLNextTrackTitle = 3
	SPLNextPlayer = 4
	SPLCurrentTrackTitle = 5
	SPLCurrentPlayer = 6
	SPLTemperature = 7

	# Table of child constants based on versions
	# These are scattered throughout the screen, so one can use foreground.getChild(index) to fetch them (getChild tip from Jamie Teh (NV Access)).
	# Because 5.x (an perhaps future releases) uses different screen layout, look up the needed constant from the table below (row = info needed, column = version).
	# As of 19.08, the below table is based on Studio 5.20.
	# #119 (20.03): a list indicates iterative descent to locate the actual objects.
	statusObjs = {
		SPLSystemStatus: -2,  # The second status bar containing system status such as up time.
		SPLNextTrackTitle: [8, 0],  # Name and duration of the next track if any.
		SPLNextPlayer: [11, 0],  # Name and duration of the next track if any.
		SPLCurrentTrackTitle: [9, 0],  # Name of the currently playing track.
		SPLCurrentPlayer: [12, 0],  # Name of the currently playing track.
		SPLTemperature: [7, 0],  # Temperature for the current city.
	}

	_cachedStatusObjs = {}

	# Called in the layer commands themselves.
	# 16.11: in Studio 5.20, it is possible to obtain some of these via the API, hence the API method is used.
	def status(self, infoIndex):
		# Look up the cached objects first for faster response.
		if infoIndex not in self._cachedStatusObjs:
			fg = api.getForegroundObject()
			if fg is not None and fg.windowClassName != "TStudioForm":
				# 6.1: Allow gesture-based functions to look up status information even if Studio window isn't focused.
				# 17.08: several SPL Controller commands will use this route.
				fg = getNVDAObjectFromEvent(user32.FindWindowW("TStudioForm", None), OBJID_CLIENT, 0)
			statusIndex = self.statusObjs[infoIndex]
			# 7.0: sometimes (especially when first loaded), OBJID_CLIENT fails, so resort to retrieving focused object instead.
			if fg is not None and fg.childCount > 1:
				obj = fg
				# #119 (20.03): for some status items, an object one level below info index must be fetched, evidenced by different window handles.
				# For situations like this (a list of navigational child indecies), an iterative descent will be used.
				if isinstance(statusIndex, list):
					for child in statusIndex:
						obj = obj.getChild(child)
				else:
					obj = fg.getChild(statusIndex)
				self._cachedStatusObjs[infoIndex] = obj
			else:
				return api.getFocusObject()
		return self._cachedStatusObjs[infoIndex]

	# Status flags for Studio 5.20 API.
	_statusBarMessages = (
		("Play status: Stopped", "Play status: Playing"),
		("Automation Off", "Automation On"),
		("Microphone Off", "Microphone On"),
		("Line-In Off", "Line-In On"),
		("Record to file Off", "Record to file On"),
	)

	# In the layer commands below, sayStatus function is used if screen objects or API must be used (API is for Studio 5.20 and later).
	def sayStatus(self, index, statusText=False):
		status = self._statusBarMessages[index][splbase.studioAPI(index, 39)]
		# #38 (17.11/15.10-LTS): return status text if asked.
		if statusText:
			return status
		ui.message(status if splconfig.SPLConfig["General"]["MessageVerbosity"] == "beginner" else status.split()[-1])

	# The layer commands themselves.

	def script_sayPlayStatus(self, gesture):
		self.sayStatus(0)

	def script_sayAutomationStatus(self, gesture):
		self.sayStatus(1)

	def script_sayMicStatus(self, gesture):
		self.sayStatus(2)

	def script_sayLineInStatus(self, gesture):
		self.sayStatus(3)

	def script_sayRecToFileStatus(self, gesture):
		self.sayStatus(4)

	def script_sayCartEditStatus(self, gesture):
		# 16.12: Because cart edit status also shows cart insert status, verbosity control will not apply.
		cartEdit = splbase.studioAPI(5, 39)
		cartInsert = splbase.studioAPI(6, 39)
		if cartEdit:
			ui.message("Cart Edit On")
		elif not cartEdit and cartInsert:
			ui.message("Cart Insert On")
		else:
			ui.message("Cart Edit Off")

	def script_sayHourTrackDuration(self, gesture):
		self.announceTime(splbase.studioAPI(0, 27))

	def script_sayHourRemaining(self, gesture):
		# 7.0: Split from playlist remaining script (formerly the playlist remainder command).
		self.announceTime(splbase.studioAPI(1, 27))

	def script_sayPlaylistRemainingDuration(self, gesture):
		if self.canPerformPlaylistCommands() == self.SPLPlaylistNoErrors:
			obj = api.getFocusObject()
			if obj.role == controlTypes.ROLE_LIST:
				obj = obj.firstChild
			self.announceTime(self.playlistDuration(start=obj), ms=False)

	def script_sayPlaylistModified(self, gesture):
		obj = self.status(self.SPLSystemStatus).getChild(5)
		# Translators: presented when playlist modification message isn't shown.
		ui.message(obj.name if obj.name else _("Playlist modification not available"))

	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Announces title of the next track if any"))
	def script_sayNextTrackTitle(self, gesture):
		if not splbase.studioIsRunning():
			self.finish()
			return
		try:
			if not splbase.studioAPI(0, 39):
				# Message comes from Foobar 2000 app module, part of NVDA Core.
				nextTrack = translate("No track playing")
			else:
				obj = self.status(self.SPLNextTrackTitle)
				# Translators: Presented when there is no information for the next track.
				nextTrack = _("No next track scheduled") if obj.name is None else obj.name
			# #34 (17.08): normally, player position (name of the internal player in Studio) would not be announced, but might be useful for some broadcasters with mixers.
			if splconfig.SPLConfig["SayStatus"]["SayStudioPlayerPosition"]:
				player = self.status(self.SPLNextPlayer).name
				ui.message(", ".join([player, nextTrack]))
			else:
				ui.message(nextTrack)
		except RuntimeError:
			# Translators: Presented when next track information is unavailable.
			ui.message(_("Cannot find next track information"))
		finally:
			self.finish()

	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Announces title of the currently playing track"))
	def script_sayCurrentTrackTitle(self, gesture):
		if not splbase.studioIsRunning():
			self.finish()
			return
		try:
			if not splbase.studioAPI(0, 39):
				# Message comes from Foobar 2000 app module, part of NVDA Core.
				currentTrack = translate("No track playing")
			else:
				obj = self.status(self.SPLCurrentTrackTitle)
				# Translators: Presented when there is no information for the current track.
				currentTrack = _("Cannot locate current track information") if obj.name is None else obj.name
			# #34 (17.08): see the note on next track script above.
			if splconfig.SPLConfig["SayStatus"]["SayStudioPlayerPosition"]:
				player = self.status(self.SPLCurrentPlayer).name
				ui.message(", ".join([player, currentTrack]))
			else:
				ui.message(currentTrack)
		except RuntimeError:
			# Translators: Presented when current track information is unavailable.
			ui.message(_("Cannot find current track information"))
		finally:
			self.finish()

	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Announces temperature and weather information"))
	def script_sayTemperature(self, gesture):
		if not splbase.studioIsRunning():
			self.finish()
			return
		try:
			obj = self.status(self.SPLTemperature)
			# Translators: Presented when there is no weather or temperature information.
			ui.message(obj.name if obj.name else _("Weather and temperature not configured"))
		except RuntimeError:
			# Translators: Presented when temperature information cannot be found.
			ui.message(_("Weather information not found"))
		finally:
			self.finish()

	def script_sayUpTime(self, gesture):
		obj = self.status(self.SPLSystemStatus).firstChild
		ui.message(obj.name)

	def script_sayScheduledTime(self, gesture):
		# 7.0: Scheduled is the time originally specified in Studio, scheduled to play is broadcast time based on current time.
		# Sometimes, hour markers return seconds.999 due to rounding error, hence this must be taken care of here.
		trackStarts = divmod(splbase.studioAPI(3, 27), 1000)
		# For this method, all three components of time display (hour, minute, second) must be present.
		# In case it is midnight (0.0 but sometimes shown as 86399.999 due to rounding error), just say "midnight".
		if trackStarts in ((86399, 999), (0, 0)):
			ui.message("00:00:00")
		else:
			self.announceTime(trackStarts[0] + 1 if trackStarts[1] == 999 else trackStarts[0], ms=False)

	def script_sayScheduledToPlay(self, gesture):
		# 7.0: This script announces length of time remaining until the selected track will play.
		# This is the only time hour announcement should not be used in order to conform to what's displayed on screen.
		self.announceTime(splbase.studioAPI(4, 27), includeHours=False)

	def script_sayListenerCount(self, gesture):
		obj = self.status(self.SPLSystemStatus).getChild(3)
		# Translators: Presented when there is no listener count information.
		ui.message(obj.name if obj.name else _("Listener count not found"))

	def script_sayTrackPitch(self, gesture):
		obj = self.status(self.SPLSystemStatus).getChild(4)
		ui.message(obj.name)

	# Few toggle/misc scripts that may be excluded from the layer later.

	def script_libraryScanMonitor(self, gesture):
		if not self.libraryScanning:
			if splbase.studioAPI(1, 32) < 0:
				ui.message(_("{itemCount} items in the library").format(itemCount=splbase.studioAPI(0, 32)))
				return
			self.libraryScanning = True
			# Translators: Presented when attempting to start library scan.
			ui.message(_("Monitoring library scan")) if not splconfig.SPLConfig["General"]["BeepAnnounce"] else tones.beep(740, 100)
			self.monitorLibraryScan()
		else:
			# Translators: Presented when library scan is already in progress.
			ui.message(_("Scanning is in progress"))

	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Marks focused track as start marker for various playlist analysis commands"))
	def script_markTrackForAnalysis(self, gesture):
		self.finish()
		if self._trackAnalysisAllowed():
			focus = api.getFocusObject()
			if scriptHandler.getLastScriptRepeatCount() == 0:
				self._analysisMarker = focus.IAccessibleChildID - 1
				# Translators: Presented when track time analysis is turned on.
				ui.message(_("Playlist analysis activated"))
			else:
				self._analysisMarker = None
				# Translators: Presented when track time analysis is turned off.
				ui.message(_("Playlist analysis deactivated"))

	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Announces total length of tracks between analysis start marker and the current track"))
	def script_trackTimeAnalysis(self, gesture):
		self.finish()
		if self._trackAnalysisAllowed():
			if self._analysisMarker is None:
				# Translators: Presented when track time analysis cannot be used because start marker is not set.
				ui.message(_("No track selected as start of analysis marker, cannot perform time analysis"))
				return
			focus = api.getFocusObject()
			trackPos = focus.IAccessibleChildID - 1
			analysisBegin = min(self._analysisMarker, trackPos)
			analysisEnd = max(self._analysisMarker, trackPos)
			analysisRange = analysisEnd - analysisBegin + 1
			# #75 (18.08): use segue instead as it gives more accurate information as to the actual total duration.
			# Add a 1 because track position subtracts it for comparison purposes.
			# 18.10: rework this so this feature can work on track objects directly.
			totalLength = self.playlistDuration(start=focus.parent.getChild(analysisBegin), end=focus.parent.getChild(analysisEnd + 1))
			# Playlist duration method returns raw seconds, so do not force milliseconds, and in case of multiple tracks, multiply this by 1000.
			if analysisRange == 1:
				self.announceTime(totalLength, ms=False)
			else:
				# Translators: Presented when time analysis is done for a number of tracks (example output: Tracks: 3, totaling 5:00).
				ui.message(_("Tracks: {numberOfSelectedTracks}, totaling {totalTime}").format(numberOfSelectedTracks=analysisRange, totalTime=self._ms2time(totalLength * 1000)))

	@scriptHandler.script(
		# Translators: Input help mode message for a command in StationPlaylist add-on.
		description=_("Presents playlist snapshot information such as number of tracks and top artists"))
	def script_takePlaylistSnapshots(self, gesture):
		if not splbase.studioIsRunning():
			self.finish()
			return
		if not self._trackAnalysisAllowed(mustSelectTrack=False):
			self.finish()
			return
		obj = api.getFocusObject()
		if obj.role == controlTypes.ROLE_LIST:
			obj = obj.firstChild
		scriptCount = scriptHandler.getLastScriptRepeatCount()
		# Display the decorated HTML window on the first press if told to do so.
		if splconfig.SPLConfig["PlaylistSnapshots"]["ShowResultsWindowOnFirstPress"]:
			scriptCount += 1
		# Never allow this to be invoked more than twice, as it causes performance degredation and multiple HTML windows are opened.
		if scriptCount >= 2:
			self.finish()
			return
		# #55 (18.04): partial playlist snapshots require start and end range.
		# Analysis marker is an integer, so locate the correct track.
		start = obj.parent.firstChild if self._analysisMarker is None else None
		end = None
		if self._analysisMarker is not None:
			trackPos = obj.IAccessibleChildID - 1
			analysisBegin = min(self._analysisMarker, trackPos)
			analysisEnd = max(self._analysisMarker, trackPos)
			start = obj.parent.getChild(analysisBegin)
			end = obj.parent.getChild(analysisEnd).next
		# Speak and braille on the first press, display a decorated HTML message for subsequent presses.
		self.playlistSnapshotOutput(self.playlistSnapshots(start, end), scriptCount)
		self.finish()

	def script_playlistTranscripts(self, gesture):
		if not splbase.studioIsRunning():
			self.finish()
			return
		if not self._trackAnalysisAllowed(mustSelectTrack=False):
			self.finish()
			return
		obj = api.getFocusObject()
		if obj.role == controlTypes.ROLE_LIST:
			obj = obj.firstChild
		try:
			d = splmisc.SPLPlaylistTranscriptsDialog(gui.mainFrame, obj)
			gui.mainFrame.prePopup()
			d.Raise()
			d.Show()
			gui.mainFrame.postPopup()
			splmisc._plTranscriptsDialogOpened = True
		except RuntimeError:
			wx.CallAfter(splmisc.plTranscriptsDialogError)
		self.finish()

	def script_switchProfiles(self, gesture):
		# #118 (20.02): do not allow profile switching while add-on settings screen is shown.
		if splconfui._configDialogOpened:
			# Translators: Presented when trying to switch to an instant switch profile when add-on settings dialog is active.
			ui.message(_("Add-on settings dialog is open, cannot switch profiles"))
			return
		splconfig.instantProfileSwitch()

	def script_setPlaceMarker(self, gesture):
		obj = api.getFocusObject()
		try:
			index = obj.indexOf("Filename")
		except AttributeError:
			# Translators: Presented when place marker cannot be set.
			ui.message(_("No tracks found, cannot set place marker"))
			return
		filename = obj._getColumnContentRaw(index)
		if filename:
			self.placeMarker = (index, filename)
			# Translators: Presented when place marker track is set.
			ui.message(_("place marker set"))
		else:
			# Translators: Presented when attempting to place a place marker on an unsupported track.
			ui.message(_("This track cannot be used as a place marker track"))

	def script_findPlaceMarker(self, gesture):
		# 7.0: Place marker command will still be restricted to playlist viewer in order to prevent focus bouncing.
		# #81: no more custom message for place marker track, as the generic one will be enough for now.
		if self.canPerformPlaylistCommands() == self.SPLPlaylistNoErrors:
			if self.placeMarker is None:
				# Translators: Presented when no place marker is found.
				ui.message(_("No place marker found"))
			else:
				track = self._trackLocator(self.placeMarker[1], obj=api.getFocusObject().parent.firstChild, columns=[self.placeMarker[0]])
				# 16.11: Just like Track Finder, use select track function to select the place marker track.
				# 20.09: perform doAction instead.
				track.doAction()

	def script_metadataStreamingAnnouncer(self, gesture):
		# 8.0: Call the module-level function directly.
		# 18.04: obtain results via the misc module.
		# 18.08.1: metadata status function takes no arguments.
		ui.message(splmisc.metadataStatus())

	# Gesture(s) for the following script cannot be changed by users.
	def script_metadataEnabled(self, gesture):
		url = int(gesture.displayName[-1])
		if splbase.studioAPI(url, 36):
			# 0 is DSP encoder status, others are servers.
			if url:
				# Translators: Status message for metadata streaming.
				status = _("Metadata streaming on URL {URLPosition} enabled").format(URLPosition=url)
			else:
				# Translators: Status message for metadata streaming.
				status = _("Metadata streaming on DSP encoder enabled")
		else:
			if url:
				# Translators: Status message for metadata streaming.
				status = _("Metadata streaming on URL {URLPosition} disabled").format(URLPosition=url)
			else:
				# Translators: Status message for metadata streaming.
				status = _("Metadata streaming on DSP encoder disabled")
		ui.message(status)

	def script_layerHelp(self, gesture):
		compatibility = splconfig.SPLConfig["Advanced"]["CompatibilityLayer"]
		if compatibility == "off":
			# Translators: The title for SPL Assistant help dialog.
			title = _("SPL Assistant help")
		elif compatibility == "jfw":
			# Translators: The title for SPL Assistant help dialog.
			title = _("SPL Assistant help for JAWS layout")
		wx.CallAfter(gui.messageBox, SPLAssistantHelp[compatibility], title)

	def script_openOnlineDoc(self, gesture):
		# 18.09: show appropriate user guide version based on currently installed channel.
		SPLAddonManifest = addonHandler.Addon(os.path.join(os.path.dirname(__file__), "..", "..")).manifest
		updateChannel = SPLAddonManifest.get("updateChannel")
		if "-dev" in SPLAddonManifest['version'] or updateChannel == "dev":
			os.startfile("https://github.com/josephsl/stationplaylist/wiki/SPLDevAddonGuide")
		else:
			os.startfile("https://github.com/josephsl/stationplaylist/wiki/SPLAddonGuide")

	__SPLAssistantGestures = {
		"kb:p": "sayPlayStatus",
		"kb:a": "sayAutomationStatus",
		"kb:m": "sayMicStatus",
		"kb:l": "sayLineInStatus",
		"kb:r": "sayRecToFileStatus",
		"kb:t": "sayCartEditStatus",
		"kb:h": "sayHourTrackDuration",
		"kb:shift+h": "sayHourRemaining",
		"kb:d": "sayPlaylistRemainingDuration",
		"kb:y": "sayPlaylistModified",
		"kb:u": "sayUpTime",
		"kb:n": "sayNextTrackTitle",
		"kb:c": "sayCurrentTrackTitle",
		"kb:w": "sayTemperature",
		"kb:i": "sayListenerCount",
		"kb:s": "sayScheduledTime",
		"kb:shift+s": "sayScheduledToPlay",
		"kb:shift+p": "sayTrackPitch",
		"kb:shift+r": "libraryScanMonitor",
		"kb:f8": "takePlaylistSnapshots",
		"kb:shift+f8": "playlistTranscripts",
		"kb:f9": "markTrackForAnalysis",
		"kb:f10": "trackTimeAnalysis",
		"kb:f12": "switchProfiles",
		"kb:f": "findTrack",
		"kb:Control+k": "setPlaceMarker",
		"kb:k": "findPlaceMarker",
		"kb:e": "metadataStreamingAnnouncer",
		"kb:f1": "layerHelp",
		"kb:shift+f1": "openOnlineDoc",
	}

	__SPLAssistantJFWGestures = {
		"kb:p": "sayPlayStatus",
		"kb:a": "sayAutomationStatus",
		"kb:m": "sayMicStatus",
		"kb:shift+l": "sayLineInStatus",
		"kb:shift+e": "sayRecToFileStatus",
		"kb:t": "sayCartEditStatus",
		"kb:h": "sayHourTrackDuration",
		"kb:shift+h": "sayHourRemaining",
		"kb:r": "sayPlaylistRemainingDuration",
		"kb:y": "sayPlaylistModified",
		"kb:u": "sayUpTime",
		"kb:n": "sayNextTrackTitle",
		"kb:shift+c": "sayCurrentTrackTitle",
		"kb:c": "toggleCartExplorer",
		"kb:w": "sayTemperature",
		"kb:l": "sayListenerCount",
		"kb:s": "sayScheduledTime",
		"kb:shift+s": "sayScheduledToPlay",
		"kb:shift+p": "sayTrackPitch",
		"kb:shift+r": "libraryScanMonitor",
		"kb:f8": "takePlaylistSnapshots",
		"kb:shift+f8": "playlistTranscripts",
		"kb:f9": "markTrackForAnalysis",
		"kb:f10": "trackTimeAnalysis",
		"kb:f12": "switchProfiles",
		"kb:f": "findTrack",
		"kb:Control+k": "setPlaceMarker",
		"kb:k": "findPlaceMarker",
		"kb:e": "metadataStreamingAnnouncer",
		"kb:f1": "layerHelp",
		"kb:shift+f1": "openOnlineDoc",
	}
