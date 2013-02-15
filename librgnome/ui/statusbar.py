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

import os

from gettext import gettext as _

import pygtk
pygtk.require('2.0')
import gtk
from gtk import glade

class statusbar:
	def __init__(self, wTree):
		""" initiates the statusbar class """
		self.wTree = wTree
		self.sc = self.wTree.get_widget('statusbar_hbox')
		self.sc.set_resize_mode(gtk.RESIZE_PARENT)
		self.status = gtk.Statusbar()
		self.status.set_has_resize_grip(False)
		self.textfield = gtk.Statusbar()
		self.textfield.set_size_request(350, -1)
		self.textfield.set_has_resize_grip(False)
		self.cursor = gtk.Statusbar()

		self.sc.pack_start(self.status)
		self.sc.pack_start(self.textfield)
		self.sc.pack_end(self.cursor)
		self.status.show()
		self.textfield.show()
		self.cursor.show()
		self.sc.show()

		self.status_cid = self.status.get_context_id("status")
		self.textfield_cid = self.textfield.get_context_id("textfield")
		self.cursor_cid = self.cursor.get_context_id("cursor")

	def push_status(self, status = 0):
		""" sets the statusfield on the statusbar """
		if status == 0:
			msg_id = self.status.push(self.status_cid, _("Ready"))
		else:
			msg_id = self.status.push(self.status_cid, _("Busy"))
		
		return msg_id

	def push_textfield(self, text):
		msg_id = self.textfield.push(self.textfield_cid, text)
		return msg_id

	def push_cursor(self, line, col):
		cursor_pos = "Line: %d Col: %d" %(line, col)
		msg_id = self.cursor.push(self.cursor_cid, cursor_pos)
		return msg_id

