# -*- coding: utf-8 -*- 
# 
# Copyright (C) 2007 Luca Della Santina
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 1, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# TODO
# - implement clean(robjects=True) for cleaning R objects
# - Propagate rpy exceptions in addition of showing them on text buffer
# - Fix missing refresh of graphs during visualization (using rpy_events() )

import string
import pygtk
pygtk.require("2.0")

import gtk, gtk.gdk, pango
from rpy import *

from gtksourceview	import SourceBuffer
from gtksourceview	import SourceLanguagesManager
from gtksourceview	import SourceView

from librgnome		import config

class editorBuffer(SourceBuffer):
	""" implements and initiats a wrapper for gtksourceview.SourceBuffer """
		
	def __init__(self):
		""" initiats the editorBuffer and sets initial values """

		self.c = config.config()

		SourceBuffer.__init__(self)
		lm = SourceLanguagesManager()
		self.languages_manager = lm
		lang = lm.get_language_from_mime_type("text/x-R")
		self.set_language(lang)

		self.tag = self.create_tag(background="#FFFF78") # value from gedit

		# Honor the users configuration
		value = self.c.get_bool("/editor/syntax_highlighting")
		if value == None: value = True
		self.set_highlight(value)

	def get_cursor(self):
		""" returns the active cursor position """
		return self.get_iter_at_mark(self.get_insert())

	def tag_text(self, start, end):
		""" highlight a given string in the TextBuffer """
		self.apply_tag(self.tag, start, end)

	def untag_text(self, start, end):
		""" remove highlighting of a given string in the TextBuffer """
		self.remove_tag(self.tag, start, end)

#-------------------------------------------------------------------------------

class Rpyconsole(SourceView):
	"""
		Uses rpy and gtksourceview to create a virtual R console that evaluates
		string commands and outputs R messages into the sourceview widget
	"""
	def __init__(self):
		""" 
		Create sourceview widget and redirect rpy output into it
		"""
		self.history = []
		self.history_placeholder = -1

		self.buf = editorBuffer()
		SourceView.__init__(self, self.buf)

		#Tell rpy to not try converting R objects to python
		#In this way original R output style is preserved
		set_default_mode(NO_CONVERSION)

		#Redirect rpy output into sourceview instead of std.out 
		set_rpy_output(self.append)

		self.show_version()
		self.load_config()

	def append(self, text):
		"""
		Print passed text into the console

		@param text - string - text to print into sourceview
		"""
		self.buf.insert(self.buf.get_end_iter(), text)

	def eval(self, text, store_history=True):
		"""
		Pass commands to R

		@param text - string - textual R expression to evaluate
		"""
		for line in text.splitlines():
			# Write the passed command
			self.append(">> " + line + "\n")
			if store_history: 
				self.history.insert(0, line)
				self.history_placeholder = -1

			try:
				# Process R expression
				result = r(line)
				if result:
					# Print R output into console
					r.print_(result)
			except RException, ex:
				# Print exception text into console
				self.append(str(ex))

	def clear(self, robjects=False):
		"""
		Clear console output

		@param robjects - boolean - if True also remove all R objects
		"""

		self.buf.set_text("")
		self.show_version()

	def show_version(self):
		"""
		Print into console informations on current R version
		"""

		self.append("R version: " + RVERSION + "\n")
		self.append("R HOME: " + RHOME + "\n")
		self.append("R user: "+ RUSER + "\n\n")

	def load_config(self):
		"""
		Load user preferences
		"""

		self.c = config.config()

		# Honor the users configuration
		value = self.c.get_bool("/editor/automatic_indentation")
		if value == None: value = True
		self.set_auto_indent(value)

		value = self.c.get_bool("/editor/display_line_numbers")
		if value == None: value = True
		self.set_show_line_numbers(value)

		try:
			value = int(self.c.get_str("/editor/tabs_width"))
		except (TypeError, ValueError):
			value = 8
		self.set_tabs_width(value)

		value = self.c.get_bool("/editor/highlight_current_line")
		if value == None: value = True
		self.set_highlight_current_line(value)

		value = self.c.get_bool("/editor/spaces_instead_of_tabs")
		if value == None: value = False
		self.set_insert_spaces_instead_of_tabs(value)

		if(self.c.get_bool("/general/use_system_font")):
			value = self.c.get_string("/desktop/gnome/interface/monospace_font_name")
			self.modify_font(pango.FontDescription(value))
		else:
			value = self.c.get_str("/general/font")
			if value == None: value = "Monospace 10"
			self.modify_font(pango.FontDescription(value))

		if(self.c.get_bool("/colors/use_system_colors")):
			value_fg = gtk.gdk.color_parse("#000000")
			value_bg = gtk.gdk.color_parse("#FFFFFF")
		else:
			value_fg = self.c.get_color("/colors/foreground")
			value_bg = self.c.get_color("/colors/background")

		self.modify_text(gtk.STATE_NORMAL, value_fg)
		self.modify_base(gtk.STATE_NORMAL, value_bg)

		self.set_wrap_mode(gtk.WRAP_WORD)

	def set_foreground_color(self, color):
		""" 
		sets the foreground color for the rconsole 
		
		@param color - gtkColor - gdk parseable color definition
		"""
		try:
			self.color = gtk.gdk.color_parse(color)
		except (TypeError, ValueError):
			return
		self.modify_text(gtk.STATE_NORMAL, self.color)

	def set_background_color(self, color):
		""" 
		sets the background color for the rconsole 
		
		@param color - gtkColor - gdk parseable color definition
		"""
		try:
			self.color = gtk.gdk.color_parse(color)
		except (TypeError, ValueError):
			return
		self.modify_base(gtk.STATE_NORMAL, self.color)

	def set_font(self, font):
		""" 
		sets the font for the rconsole 
		
		@param font - string - pango parseable font description
		"""
		if not font:
			return
		self.set_font_from_string(font)

	def set_font_from_string(self, font):
		""" 
		sets the font for the rconsole by string 
		
		@param font - string - pango parseable font description 
		"""
		if not font: 
			return
		self.modify_font(pango.FontDescription(font))

	def get_buffer(self):
		""" 
		@return - SourceBuffer - text buffer of the console
		"""
		return self.buf

	def history_forward(self):
		"""
		@return - string - element earlier in history
		@return - None - if no element is available earlier in history
		"""
		if self.history_placeholder < 0:
			return None
		elif self.history_placeholder == 0:
			self.history_placeholder -= 1
			return None
		else:
			self.history_placeholder -= 1
			return self.history[self.history_placeholder]

	def history_back(self):
		"""
		@return - string - element older in history
		@return - None - if no element is available older in history
		"""
		if self.history_placeholder >= len(self.history):
			return None
		elif self.history_placeholder == len(self.history)-1:
			self.history_placeholder += 1
			return None
		else:
			self.history_placeholder +=1
			return self.history[self.history_placeholder]

	def history_clear(self):
		"""
		Clear command history and reset history placeholder
		"""
		self.history = []
		self.history_placeholder = -1

	def history_load(self, filename):
		"""
		Load command history from file

		@param filename - string - Filename to save history into
		"""
		try:
			rhist = open(filename, "r")
			self.history_clear()
			for line in rhist:
				self.history.insert(0, line.replace("\n", ""))
		finally:
			rhist.close()

	def history_save(self, filename):
		"""
		Save command history

		@param filename - string - Filename to save history into
		"""
		try:
			rhist = open(filename, "w")
			for item in reversed(self.history):
				rhist.write(item + "\n")
		finally:
			rhist.close()
