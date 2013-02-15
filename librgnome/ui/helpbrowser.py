# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Luca Della Santina
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

# TODO
# - Correctly handle those strange characters that appear in man pages
#	(probably related to en_US charset or some escape character man-specific)

import os

import pygtk
pygtk.require("2.0")

import gtk, gtk.gdk, pango

from gtksourceview import SourceView
from gtksourceview import SourceBuffer
from rpy import *

class HelpItem:
	""" 
	Helper class storing help data
	"""

	def __init__(self, filename, title, textbuf):
		self.filename = filename
		self.title = title
		self.textbuf = textbuf

class HelpBrowser:
	""" Implements an help browser """
	def __init__(self):
		""" 
		Initialization
		"""
		self.filename = None
		self.shortname = "Help"
		self.history = []

		# Create an icon for the notebook tab
		self.tab_icon = gtk.image_new_from_stock(gtk.STOCK_FILE, gtk.ICON_SIZE_MENU)

		# Create a label with short name for the notebook tab
		self.tab_label = gtk.Label()
		self.tab_label.set_label(self.shortname)
		self.tab_label_tip = gtk.Tooltips()
		self.tab_label_tip.set_tip(self.tab_label, _("Filename: undefined"), "")

		# Create a small close button for the notebook tab
		self.tab_close_btn = gtk.Button()
		self.tab_close_btn.set_relief(gtk.RELIEF_NONE)
		self.tab_close_btn.set_focus_on_click(False)
		btnCloseTip = gtk.Tooltips()
		btnCloseTip.set_tip(self.tab_close_btn, _("Close item"), "")
		btnCloseImage = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
		self.tab_close_btn.set_image(btnCloseImage)

		# create a box to hold the label and the close button
		self.tab_hbox = gtk.HBox(False, 4)
		self.tab_hbox.set_border_width(0)
		self.tab_hbox.pack_start(self.tab_icon, False, False, 0)
		self.tab_hbox.pack_start(self.tab_label, False, False, 0)
		self.tab_hbox.pack_start(self.tab_close_btn, False, False, 0)

		#create a scrolledwindow and place the sourceview inside
		self.help = HelpItem(None, "Help", SourceBuffer())
		self.helpview = SourceView(self.help.textbuf)
		self.helpview.set_wrap_mode(gtk.WRAP_WORD)

		self.scrolledwin = gtk.ScrolledWindow()
		self.scrolledwin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.scrolledwin.add(self.helpview)

		self.set_active()

	def get_buffer(self):
		"""@return - SourceBuffer - Text buffer of current help"""
		return self.help.textbuf

	def get_short_name(self):
		"""@return - string - Short name of the help item"""
		return self.shortname

	def get_filename(self):
		"""@return - string - Full path+filename of the help item"""
		return self.filename

	def get_tab_label(self):
		"""@return - gtk.Label - Label with short name of the help item"""
		return self.tab_label

	def get_tab_close_button(self):
		"""@return - gtk.Button - A little close button"""
		return self.tab_close_btn

	def get_tab_icon(self):
		"""@return - gtk.Image - Current icon for the help item"""
		return self.tab_icon

	def set_tab_icon(self, stock_image):
		""" 
		Change tab icon into a new stock image

		@param stock_image - gtk.STOCK_ - new icon for the script's tab
		"""
		self.tab_icon.set_from_stock(stock_image, gtk.ICON_SIZE_MENU)

	def get_tab_hbox(self):
		"""@return - gtk.HBox - Box containing tab controls"""
		self.show_controls()
		return self.tab_hbox

	def get_view(self):
		"""@return - gtk.ScrolledWindow - widget encapsulating help viewer"""
		self.helpview.show()
		self.scrolledwin.show()
		return self.scrolledwin

	def go_backward(self):
		"""
		Visualize help document searched before the current one, if any
		"""

		index = self.history.index(self.help)

		if index > 0 :
			self.help = self.history[index-1]
			self.helpview.set_buffer(self.help.textbuf)
			self.shortname = self.help.title

		self.__update_short_name()

	def go_forward(self):
		"""
		Visualize help document searched before the current one, if any
		"""
		index = self.history.index(self.help)

		if index < (len(self.history)-1) :
			self.help = self.history[index+1]
			self.helpview.set_buffer(self.help.textbuf)
			self.shortname = self.help.title

		self.__update_short_name()

	def help_call(self, name):
		r.help(name)

	def set_active(self):
		"""
		Make this help item active by redirecting rpy help output into it
		"""
		set_rpy_showfiles(self.__rpy_showfiles_callback)

	def show_controls(self):
		"""Show all tab controls for this item"""
		self.tab_icon.show()
		self.tab_label.show()
		self.tab_close_btn.show()

	def __rpy_showfiles_callback(self, files, headers, title, delete):
		"""
		Callback when rpy need to display an external file (usually help items)

		@param files - list - List of files to display
		@param headers - list - List of files' header
		@param title - string - Title of the request
		@param delete - boolean - True if files must deleted at the end
		"""

		if len(files) == 1 :
			# Open and read selected file
			try:
				print files[0]
				fd = open(files[0], "rbU")
				s = unicode(fd.read(), "utf-8")
				file_content = s.encode("utf-8")
				# Workaround for removing strange char, find a better way
				file_content = file_content.replace("_", "")
			finally:
				fd.close()

			# Place file content of it into a new history
			self.help = HelpItem(files[0], title, SourceBuffer())			
			self.help.textbuf.set_text(file_content)
			self.help.textbuf.place_cursor(self.help.textbuf.get_start_iter())
			self.helpview.set_buffer(self.help.textbuf)
			self.history.append(self.help)

			self.shortname = self.help.title
			self.__update_short_name()

		if delete:
			for item in files:
				os.remove(item)
				print "file removed"

	def __update_short_name(self):
		"""Update shortname according to current filename"""
		self.tab_label.set_label(self.shortname)

