# -*- coding: utf-8 -*- 
# 
# Copyright (C) 2007 Gordon Bergling
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

import pygtk
pygtk.require("2.0")

import gtk, gtk.gdk, pango
from gtksourceview	import SourceBuffer
from gtksourceview	import SourceLanguagesManager
from gtksourceview	import SourceView

from librgnome		import config

class editor(gtk.ScrolledWindow):
	"""
		Implements a GtkScrolledWindow, which inherits
		a gtksourceview class for syntax highlighting
		and other usefull stuff, which is found in
		coding environments.
	"""
	def __init__(self, widget):
		"""
			initiat the widget
		"""

		self.c = config.config()
		gtk.ScrolledWindow.__init__(self)
		self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.show()
		self.editor = editorView(self)
		self.editor.show()
		self.add(self.editor)

	def get_buffer(self):
		"""
		returns the source buffer object

		@return - gtkSourceBuffer 
		"""
		buffer = self.editor.get_buffer()
		return buffer

	def get_view(self):
		""" 
		returns the SourceView object 
		
		@return - gtkSourceView object
		"""
		view = self.editor
		return view

	def get_cursor_position(self):
		""" 
		returns the current cursor position 
		
		@return line - string - current cursor position (line)
		@return col - string - current cursor position (column)
		"""
		view = self.editor
		buffer = self.editor.get_buffer()
		iter = buffer.get_iter_at_mark(buffer.get_insert())
		line = iter.get_line()
		start_iter = buffer.get_iter_at_line(line)
		line_text = buffer.get_text(start_iter, iter)
		tabs_width = view.get_tabs_width()

		col = 0
		from operator import eq
		for ch in line_text:
			if eq(ch, "\t"):
				col += (tabs_width - (col % tabs_width))
			else:
				col +=1
		
		return line + 1 , col + 1

class editorBuffer(SourceBuffer):
	""" implements and initiats a wrapper for gtksourceview.SourceBuffer """
		
	def __init__(self):
		""" initiats the editorBuffer and sets initial values """

		self.matches = []
		self.current_match = {'start' : None, 'end' : None}

		self.c = config.config()

		SourceBuffer.__init__(self)
		lm = SourceLanguagesManager()
		self.languages_manager = lm
		lang = lm.get_language_from_mime_type("text/x-R")
		self.set_language(lang)

		self.tag = self.create_tag(background="#FFFF78") # value from gedit
		self.match_tag = self.create_tag(background="#808080") # value from gedit

		# Honor the users configuration
		value = self.c.get_bool("/editor/syntax_highlighting")
		if value == None: value = True
		self.set_highlight(value)

	def get_cursor(self):
		""" 
		returns the active cursor position

		@return cursor_mark - gtkIter - current cursor iterator
		"""
		return self.get_iter_at_mark(self.get_insert())

	def tag_text(self, start, end):
		""" highlight a given string in the TextBuffer """
		self.apply_tag(self.tag, start, end)

	def untag_text(self, start, end):
		""" remove highlighting of a given string in the TextBuffer """
		self.remove_tag(self.tag, start, end)

	def tag_match(self):
		""" highlight current search match """
		start = self.get_iter_at_mark(self.current_match['start'])
		end = self.get_iter_at_mark(self.current_match['end'])
		self.apply_tag(self.match_tag, start, end)

	def untag_match(self):
		""" remove highlighting of the current search match """
		start = self.get_iter_at_mark(self.current_match['start'])
		end = self.get_iter_at_mark(self.current_match['end'])
		self.remove_tag(self.match_tag, start, end)

	def highlight_string(self, string):
		""" highlight all occurences of string """

		# clear matches list
		self.matches = []
		# get start iterator
		start = self.get_start_iter()

		finished = False
		while not finished:
			res = start.forward_search(string, gtk.TEXT_SEARCH_TEXT_ONLY)
			if not res:
				finished = True
			else:
				m_start, m_end = res
				mark_start = self.create_mark(None, m_start)
				mark_end = self.create_mark(None, m_end)
				self.matches.append((mark_start, mark_end))
				self.tag_text(m_start, m_end)
				start = m_end

	def clear_highlight_string(self):
		""" remove the highlighting of a string """
		start, end = self.get_bounds()
		self.untag_text(start, end)

	def search(self, string, forward=True):
		"""
		Search in the buffer. Default forward.

		@param string - string - search string
		@param forward - boolean - search direction, defaults to forward

		@return from_pos - gtk.Iter - from cursor position
		@return to_pos - gtk.Iter - to cursor position
		"""

		cursor = self.get_cursor()
		try:
			if forward:
				[start, end] = cursor.forward_search(string, gtk.TEXT_SEARCH_TEXT_ONLY)
			else:
				[start, end] = cursor.backward_search(string, gtk.TEXT_SEARCH_TEXT_ONLY)
		except TypeError:
			return

		# check if we have allready a current match
		# and untag it to tag the next one.
		if self.current_match['start']:
			self.untag_match()

		# Update the current match position
		mark_start = self.create_mark(None, start)
		mark_end = self.create_mark(None, end)
		self.current_match['start'] = mark_start
		self.current_match['end'] = mark_end
		
		# get the current cursor position
		now_pos = cursor.get_offset()
		start_pos = start.get_offset()
		end_pos = end.get_offset()

		# calculate the new movement coordinates
		if forward:
			from_pos = start_pos - now_pos
			to_pos   = end_pos - start_pos
		else:
			from_pos = end_pos - now_pos
			to_pos   = start_pos - end_pos
		
		self.tag_match()

		return from_pos, to_pos

	def replace(self, string):
		"""
		replace a string at the current cursor position

		@param string - string - replace string
		"""
		if self.current_match['start']:
			start = self.get_iter_at_mark(self.current_match['start'])
			end = self.get_iter_at_mark(self.current_match['end'])
			self.delete(start, end)
			start = self.get_iter_at_mark(self.current_match['start'])
			self.insert(start, string)

	def replace_all(self, string):
		""" 
		replaces all occurences of a string in the textbuffer
		
		@param string - string - replace string
		"""
		for marks in self.matches:
			begin = self.get_iter_at_mark(marks[0])
			end = self.get_iter_at_mark(marks[1])
			self.delete(begin, end)
			begin = self.get_iter_at_mark(marks[0])
			self.insert(begin, string)

class editorView(SourceView):
	"""
		Implements a wrapper for gtksourceview.SourceView
	"""
	def __init__(self, widget):
		""" initiats the EditorView and sets initial values """
		self.buf = editorBuffer()
		SourceView.__init__(self, self.buf)

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
