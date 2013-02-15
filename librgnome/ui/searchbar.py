# -*- coding: utf-8 -*- 
#
# Copyright (C) 2007 Gordon Bergling
#
# This file is part of RGnome.
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
pygtk.require('2.0')
import gtk, gtk.gdk, gtk.glade

from gettext import gettext as _

from librgnome import config

class searchbar:
	""" represents the searchbar """
	def __init__(self, editor_nb, wTree):
		""" initiats the searchbar """

		# Create the main widgets
		self.wTree = wTree
		self.nb = editor_nb
		self.search_bar = self.wTree.get_widget('search_bar')

		# Create the buttons
		self.close_btn = self.wTree.get_widget('search_close_btn')
		self.next_btn = self.wTree.get_widget('find_next_btn')
		self.previous_btn = self.wTree.get_widget('find_previous_btn')

		# Create Toogle Buttons
		self.match_case_btn = self.wTree.get_widget('match_case_btn')
		self.match_word_btn = self.wTree.get_widget('match_word_btn')

		# Create the search field & connect signals
		self.search_field = self.wTree.get_widget('search_field')

		dic_signals = {
			'on_search_close_btn_clicked': self.close,
			'on_find_next_btn_clicked': self.find_next,
			'on_find_previous_btn_clicked': self.find_previous,
			'on_match_case_btn_toggled': self.match_case_cb,
			'on_match_word_btn_toggled': self.match_word_cb,
			'on_search_field_activate': self.search_field_activated_cb,
			'on_search_field_backspace': self.search_field_backspace_cb}
		dic_search_menu = {
			'on_find_activate': self.show,
			'on_find_next_activate': self.find_next,
			'on_find_previous_activate': self.find_previous}

		self.wTree.signal_autoconnect(dic_signals)
		self.wTree.signal_autoconnect(dic_search_menu)

		# Search mode flags
		self.match_case = False
		self.match_word = False

	def find_cb(self, widget=None, forward=True):
		""" 
		Search in the currently active editor tab

		@param widget - gtk.Widget - Caller widget, if any
		@param forward - boolean - Search direction, True if forward (default)
		"""
		tab = self.nb.get_current_page()
		buf = self.nb.get_nth_page(tab).get_buffer()
		view = self.nb.get_nth_page(tab).get_view()

		string = self.search_field.get_text()

		# highlight the search string
		buf.highlight_string(string)
		
		# get next cursor position and move the cursor to it
		try:
			from_pos, to_pos = buf.search(string, forward)
			view.emit('move-cursor', gtk.MOVEMENT_LOGICAL_POSITIONS, from_pos, False)
			view.emit('move-cursor', gtk.MOVEMENT_LOGICAL_POSITIONS, to_pos, False)
		except (TypeError, UnboundLocalError):
			# we are already at the beginning or the bottom of the buffer
			pass

	def match_case_cb(self, widget):
		""" Match Case Search Option """
		self.match_case = self.match_case_btn.get_active()
	
	def match_word_cb(self, widget):
		""" Match Word Search Option """
		self.match_word = self.match_word_btn.get_active()

	def search_field_activated_cb(self, widget):
		""" callback if enter is pressed in the search field """
		self.find_cb(forward=True)

	def search_field_backspace_cb(self, widget):
		""" callback when a backspace is used on the search_field """
		tab = self.nb.get_current_page()
		buf = self.nb.get_nth_page(tab).get_buffer()
		buf.clear_highlight_string()

	def find_next(self, widget=None):
		""" Search the next occurrence """
		self.find_cb(forward=True)

	def find_previous(self, widget=None):
		""" Search the previous occurrence """
		self.find_cb(forward=False)

	def is_visible(self, widget=None):
		"""
		Check if the searchbar is visible

		@return - boolean - True if visible
		"""
		return self.search_bar.flags() & gtk.VISIBLE

	def show(self, widget=None):
		""" show the search_bar """
		self.search_bar.show_all()
		self.search_field.grab_focus()
		
	def close(self, widget=None):
		""" closes the find dialog and untag the TextBuffer"""
		tab = self.nb.get_current_page()
		buf = self.nb.get_nth_page(tab).get_buffer()
		buf.clear_highlight_string()
		self.search_bar.hide()
