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
# - Handle file open/save exceptions with error dialogs
# - make tab_label tooltip show filename (buggy)

import os
import shutil

from gettext import gettext as _

import pygtk
pygtk.require('2.0')
import gtk

class Script:
	""" Implements a generical script """
	def __init__(self, name, textbuf):
		""" 
		Script initialization

		@param name - string - Name of the new script
		"""
		self.filename = None
		self.shortname = name
		self.changed = False
		self.textbuf = textbuf
		self.history = []

		# Create an icon for the notebook tab
		self.tab_icon = gtk.image_new_from_stock(gtk.STOCK_FILE, gtk.ICON_SIZE_MENU)

		# Create a label with short name of the script for the notebook tab
		self.tab_label = gtk.Label()
		self.tab_label.set_label(self.shortname)
		self.tab_label_tip = gtk.Tooltips()
		self.tab_label_tip.set_tip(self.tab_label, _("Filename: undefined"), "")

		# Create a small close button for the notebook tab
		self.tab_close_btn = gtk.Button()
		self.tab_close_btn.set_relief(gtk.RELIEF_NONE)
		self.tab_close_btn.set_focus_on_click(False)
		btnCloseTip = gtk.Tooltips()
		btnCloseTip.set_tip(self.tab_close_btn, _("Close script"), "")
		btnCloseImage = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
		self.tab_close_btn.set_image(btnCloseImage)

		# create a box to hold the label and the close button
		self.tab_hbox = gtk.HBox(False, 4)
		self.tab_hbox.set_border_width(0)
		self.tab_hbox.pack_start(self.tab_icon, False, False, 0)
		self.tab_hbox.pack_start(self.tab_label, False, False, 0)
		self.tab_hbox.pack_start(self.tab_close_btn, False, False, 0)

	def get_buffer(self):
		"""@return - SourceBuffer - Text buffer of the script"""
		return self.textbuf

	def get_short_name(self):
		"""@return - string - Short name of the script"""
		return self.shortname

	def get_filename(self):
		"""@return - string - Full path+filename of the script"""
		return self.filename

	def get_tab_label(self):
		"""@return - gtk.Label - Label with short name of the script"""
		return self.tab_label

	def get_tab_close_button(self):
		"""@return - gtk.Button - A little close button"""
		return self.tab_close_btn

	def get_tab_icon(self):
		"""@return - gtk.Image - Current icon for the script"""
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

	def load(self, textbuf, filename=None):
		""" 
		Choose and load an existing script from disk

		@param textbuf - buffer - The page buffer where script is loaded
		@param filename - string - filename to load
		@return - string - Filename of selected script, None otherwise
		"""
		if filename:
			self.filename = filename
		else:
			# Show file chooser dialog
			chooser = gtk.FileChooserDialog(title   = _("Open"),\
							action  = gtk.FILE_CHOOSER_ACTION_OPEN,\
							buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
										gtk.STOCK_OK, gtk.RESPONSE_OK))
			if self.filename:
				chooser.set_current_folder(os.path.abspath(os.path.dirname(self.filename)))
				chooser.set_current_name(os.path.basename(self.filename))
			else:
				chooser.set_current_folder(os.path.abspath(os.path.curdir))

			for filter in self.__get_file_filters():
				chooser.add_filter(filter)

			result = chooser.run()
			if result != gtk.RESPONSE_OK:
				chooser.destroy()
				return None
			else:
				self.filename = chooser.get_filename()
				chooser.destroy()

		# Open and read selected file
		try:
			fd = open(filename, "rbU")
			s = unicode(fd.read(), "utf-8")
			file_content = s.encode("utf-8")
		finally:
			fd.close()

		# Place file content of it into the buffer
		textbuf.begin_not_undoable_action()
		textbuf.set_text(file_content)
		textbuf.end_not_undoable_action()
		textbuf.set_modified(False)
		textbuf.place_cursor(textbuf.get_start_iter())

		self.__update_filename()

		return self.get_filename()

	def load_dialog(self):
		""" 
		Choose an existing script from disk

		@return - string - Filename of selected script, None otherwise
		"""
		# Show file chooser dialog
		chooser = gtk.FileChooserDialog(title   = _("Open"),\
						action  = gtk.FILE_CHOOSER_ACTION_OPEN,\
						buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
									gtk.STOCK_OK, gtk.RESPONSE_OK))
		if self.filename:
			chooser.set_current_folder(os.path.abspath(os.path.dirname(self.filename)))
			chooser.set_current_name(os.path.basename(self.filename))
		else:
			chooser.set_current_folder(os.path.abspath(os.path.curdir))

		for filter in self.__get_file_filters():
			chooser.add_filter(filter)

		result = chooser.run()
		if result != gtk.RESPONSE_OK:
			chooser.destroy()
			return None
		else:
			filename = chooser.get_filename()
			chooser.destroy()
			return filename

	def save(self, textbuf, filename=None):
		""" 
		Save current script into filename, prompting file chooser if needed

		@param textbuf - buffer - Script text buffer
		@param filename - string - if None prompt file chooser dialog
		@return - string - filename where script is saved, None otherwise
		"""
		# Check if a filename is provided otherwise let the user choose it
		if not filename:
			chooser = gtk.FileChooserDialog(title = _("Save as"),\
						action  = gtk.FILE_CHOOSER_ACTION_SAVE,\
						buttons = (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,\
									gtk.STOCK_OK, gtk.RESPONSE_OK))
			if self.filename:
				chooser.set_current_folder(os.path.abspath(os.path.dirname(self.filename)))
				chooser.set_current_name(os.path.basename(self.filename))
			else:
				chooser.set_current_folder(os.path.abspath(os.path.curdir))

			for filter in self.__get_file_filters():
				chooser.add_filter(filter)

			result = chooser.run()
			if result != gtk.RESPONSE_OK:
				chooser.destroy()
				return None
			else:
				# set the label on the editor notebook with the choosen filename
				self.filename = chooser.get_filename()
				chooser.destroy()
		else:
			# make a backup copy of the file
			try: 
				shutil.copy(self.filename, self.filename + "~")
			except:
				# TODO handle if self.filename does not exists before trying 
				#	to backup it into self.filename~
				pass


		# get buffer's contents
		text = textbuf.get_text(textbuf.get_start_iter(), 
								textbuf.get_end_iter()) + "\n"

		# save it into filename
		try:
			fd = open(self.filename, "w")
			fd.write(text)
		finally:
			fd.close()

		self.set_changed(False)
		self.__update_filename()

	def is_changed(self):
		""" Check if changed status is true"""
		return self.changed

	def set_changed(self, value):
		"""
		Set script's changed stats

		@param value - boolean - New changed status
		"""
		self.changed = value

		if self.changed:
			self.tab_label.set_label("*" + self.shortname)
			self.set_tab_icon(gtk.STOCK_EDIT)
		else:
			self.tab_label.set_label(self.shortname)
			self.set_tab_icon(gtk.STOCK_FILE)

	def show_controls(self):
		"""Show all tab controls for this script"""
		self.tab_icon.show()
		self.tab_label.show()
		self.tab_close_btn.show()

	def __get_file_filters(self):
		"""
		Provide filters for selecting script files

		@return - gtk.FileFilter[] - File filters for use in gtk.FileChooser
		"""
		result = []

		filter = gtk.FileFilter()
		filter.set_name(_("R Files"))
		filter.add_pattern("*.[rR]")
		result.append(filter)

		filter = gtk.FileFilter()
		filter.set_name(_("All Files"))
		filter.add_pattern("*")
		result.append(filter)

		return result

	def __update_short_name(self):
		"""Update shortname according to current filename"""
		self.shortname = os.path.basename(self.filename)
		self.tab_label.set_label(self.shortname)

	def __update_filename(self):
		"""Update tooltip & shortname according to current filename"""
		self.tab_label_tip.set_tip(self.tab_label, _("Filename: ") + 
													self.filename, "")
		self.__update_short_name()

