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

# TODO

import gtk, gtk.gdk
import vte

from librgnome import config

class rconvt(vte.Terminal):
	""" implements a virtual terminal for the R process """
	def __init__(self):
		""" initiats the virtual terminal """
		vte.Terminal.__init__(self)
		self.set_emulation('xterm')
		self.reset(True, True)
		self.set_scrollback_lines(0)

		# Honor the users configuration
		self.c = config.config()

		if(self.c.get_bool("/general/use_system_font")):
			value = self.c.get_string("/desktop/gnome/interface/monospace_font_name")
			self.set_font(value)
		else:
			value = self.c.get_str("/general/font")
			if value == None: value = "monospace 10"
			self.set_font(value)

		key_value = self.c.get_bool("/colors/use_system_colors")
		if key_value == True:
			value_fg = gtk.gdk.color_parse("#000000")
			value_bg = gtk.gdk.color_parse("#FFFFFF")
		else:
			black = gtk.gdk.color_parse('#000000')
			white = gtk.gdk.color_parse('#FFFFFF')
			value_fg = self.c.get_color("/colors/foreground")
			value_bg = self.c.get_color("/colors/background")
			if value_fg == None: value_fg = black
			if value_bg == None: value_bg = white

		self.set_default_colors()
		self.set_background_color(value_bg)
		self.set_foreground_color(value_fg)

		value = self.c.get_bool("/general/cursor_blinks")
		if value == None or value == False:
			self.set_cursor_blinks_off()
		else:
			self.set_cursor_blinks_on()

		self.show()

		# Finally fork R
		pid = self.fork_r()

	def fork_r(self):
		""" forks the R process """
        # XXX Here is more logic need to determine the correct path
        #     to R. Honor R_HOME and friends...
		pid = self.fork_command('R')
		return pid

	def startup(self, command):
		""" pass commands to R on startup """
		if command:
			self.feed_child(command)
		else:
			pass
		
	def shutdown(self):
		""" shut down R """
		if self.c.get_bool("/general/save_r_history"):
			shutdown_cmd = "q()\ny\n"
		else:
			shutdown_cmd = "q()\nn\n"

		self.feed_child(shutdown_cmd)
		
	def set_foreground_color(self, color):
		""" sets the forground color for the virtual terminal """
		self.set_color_foreground(color)

	def set_background_color(self, color):
		""" sets the background color for the virtual terminal """
		self.set_color_background(color)

	def set_font(self, font):
		""" sets the font for the virtual terminal """
		self.set_font_from_string(font)

	def set_cursor_blinks_on(self):
		""" enable the blinking of the cursor """
		self.set_cursor_blinks(True)

	def set_cursor_blinks_off(self):
		""" disable the blinking of the cursor """
		self.set_cursor_blinks(False)


class rconsole(gtk.ScrolledWindow):
	""" 
		Implements a gtk.ScrolledWindow, which holds a virtual terminal
	    	of the R process.
	"""
	def __init__(self, widget):
		gtk.ScrolledWindow.__init__(self)
		self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.vt = rconvt()
		self.vt.show()
		self.add_with_viewport(self.vt)
		self.show()

