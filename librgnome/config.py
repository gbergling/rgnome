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

import gconf 
import gtk.gdk

# XXX Make config a gconf object?
class config:
	def __init__(self):
		self.client = gconf.client_get_default()
		self.base = "/apps/rgnome"
		self.version = "0.1.9-alpha"
	
		self.client.add_dir(self.base + "/editor", gconf.CLIENT_PRELOAD_NONE)
		self.client.add_dir(self.base + "/colors", gconf.CLIENT_PRELOAD_NONE)
		self.client.add_dir(self.base + "/general", gconf.CLIENT_PRELOAD_NONE)

		# for future use	
		#self.client.add_notify(self.base + "/editor/display_line_numbers", self.display_line_numbers)
		#self.client.add_notify(self.base + "/editor/highlight_current_line", self.highlight_current_line)
		#self.client.add_notify(self.base + "/editor/display_right_margin", self.display_right_margin)
		#self.client.add_notify(self.base + "/editor/syntax_highlighting", self.syntax_highlighting)
		#self.client.add_notify(self.base + "/editor/highlight_matching_bracket", self.highlight_matching_bracket)
		#self.client.add_notify(self.base + "/editor/automatic_identation", self.automatic_identation)
		#self.client.add_notify(self.base + "/editor/tabs_width", self.tabs_width)
		#self.client.add_notify(self.base + "/editor/spaces_instead_of_tabs", self.spaces_instead_of_tabs)
		#self.client.add_notify(self.base + "/colors/foreground", self.foreground)
		#self.client.add_notify(self.base + "/colors/background", self.background)
		#self.client.add_notify(self.base + "/colors/use_system_colors", self.use_system_colors)
		#self.client.add_notify(self.base + "/colors/buildin_scheme", self.buildin_scheme)
		#self.client.add_notify(self.base + "/general/respawn_r", self.respawn_r)
		#self.client.add_notify(self.base + "/general/use_system_font", self.use_system_font)
		#self.client.add_notify(self.base + "/general/font", self.font)
		#self.client.add_notify(self.base + "/general/cursor_blinks", self.cursor_blinks)

	def get_str(self, data):
		""" gets a string value """
		return self.client.get_string(self.base + data)

	def set_str(self, data, value):
		""" sets a string value """
		self.client.set_string(self.base + data, str(value))

	def get_string(self, data):
		""" returns a string value without self.base added """
		return self.client.get_string(data)

	def get_bool(self, data):
		""" gets a bool value """
		return self.client.get_bool(self.base + data)

	def set_bool(self, data, value):
		""" sets a bool value """
		self.client.set_bool(self.base + data, value)

	def set_color(self, data, color):
		""" sets a color value """
		color = "#%.2X%.2X%.2X" % \
                   (color.red/256,color.green/256,color.blue/256)
		color = self.client.set_string(self.base + data, color)

	def get_color(self, data):
		""" gets a color value """
		color_string = self.client.get_string(self.base + data)
		try:
			value = gtk.gdk.color_parse(color_string)
		except (TypeError, ValueError):
			return None
		return value

	def get_version(self):
		""" return the version of rgnome """
		return self.version
