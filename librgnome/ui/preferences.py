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
import pygtk
pygtk.require('2.0')
import gtk, gtk.gdk, gtk.glade, pango

from gettext import gettext as _

from librgnome import config

class PreferencesWindow:
	def __init__(self, widget, parent, rconvt):
		"""
			Initiats the Preferences Window 
		"""

		self.editor_nb 	= parent
		self.rconvt 	= rconvt
		
		self.c	= config.config()

		# Read in the Glade File
		self.wTree = gtk.glade.XML('resource%spreferences.glade' % os.sep, "PreferencesDialog")
		# Create the Main Window
		self.prefdlg = self.wTree.get_widget('PreferencesDialog')
		# set the window icon
		img = os.path.abspath(os.getcwd()) + "%sresource%srgnome.png" % (os.sep, os.sep)
		icon = gtk.gdk.pixbuf_new_from_file(img)
		self.prefdlg.set_icon(icon)
		# Create Preferences Notebook 
		self.pref_nb = self.wTree.get_widget('preferences_nb')
		self.pref_nb.show()
		self.prefdlg.show()
		# Create Toggle Buttons Widgets
		self.use_system_terminal_font 	 = self.wTree.get_widget('system_terminal_font')
		self.use_system_colors		 = self.wTree.get_widget('system_colors')
		self.line_numbers		 = self.wTree.get_widget('line_numbers')
		self.highlight_current_line	 = self.wTree.get_widget('highlight_current_line')
		self.right_margin		 = self.wTree.get_widget('right_margin')
		self.syntax_highlighting	 = self.wTree.get_widget('syntax_highlighting')
		self.matching_bracket		 = self.wTree.get_widget('matching_bracket')
		self.indentation		 = self.wTree.get_widget('indentation')
		self.spaces_instead_of_tabs	 = self.wTree.get_widget('spaces_instead_of_tabs')
		self.respawn_r 			 = self.wTree.get_widget('respawn_r')
		self.save_r_history	= self.wTree.get_widget('save_r_history')
		# Create Color Buttons
		self.foreground_color_btn	= self.wTree.get_widget('foreground_color')
		self.background_color_btn	= self.wTree.get_widget('background_color')
		self.color_cmb			= self.wTree.get_widget('color_scheme_cmb')
		# Create the Font Button
		self.font_btn			= self.wTree.get_widget('terminal_font_button')
		# Create the Tab Width Spin Button
		self.tab_spin_btn		= self.wTree.get_widget('tab_width_btn')
		# Labels
		self.label_001			= self.wTree.get_widget('label_001')
		self.label_002			= self.wTree.get_widget('label_002')
		self.label_003			= self.wTree.get_widget('label_003')
		self.label_004			= self.wTree.get_widget('label_004')

		# Finally show the widgets
		self.pref_nb.show()
		self.prefdlg.show()

		dic_signal = {'on_prefhelp_clicked'  : self.help_activate,
			      'on_prefclose_clicked' : self.close}
		dig_tgl_buttons = { 'on_use_system_terminal_font_toggled' : self.system_font_cb,
			'on_use_system_colors_toggled' : self.system_colors_cb,
			'on_line_numbers_toggled' : self.line_numbers_cb,
			'on_highlight_current_line_toggled' : self.highlight_current_line_cb,
			'on_right_margin_toggled' : self.right_margin_cb,
			'on_syntax_highlighting_toggled' : self.syntax_highlighting_cb,
			'on_matching_bracket_toggled' : self.matching_bracket_cb,
			'on_indentation_toggled' : self.indentation_cb,
			'on_spaces_instead_of_tabs_toggled' : self.spaces_instead_of_tabs_cb,
			'on_respawn_r_toggled' : self.respawn_r_cb,
			'on_save_r_history_toggled': self.save_r_history_cb}
		dic_other_buttons = { 'on_terminal_font_button_font_set' : self.set_font,
			'on_foreground_color_color_set' : self.set_foreground_color,
			'on_background_color_color_set' : self.set_background_color,
			'on_tab_width_change'  : self.tab_width_change,
			'on_color_scheme_cmb_changed' : self.color_cmb_changed}

		# connect the signals
		self.wTree.signal_autoconnect(dic_signal)
		self.wTree.signal_autoconnect(dig_tgl_buttons)
		self.wTree.signal_autoconnect(dic_other_buttons)
		self.prefdlg.connect("destroy", self.close)

		# set the Toggle Button states from gconf settings
		value = self.c.get_bool("/editor/automatic_indentation")
		if value == None: value = False
		self.indentation.set_active(value)

		value = self.c.get_bool("/editor/display_line_numbers")
		if value == None: value = False
		self.line_numbers.set_active(value)

		value = self.c.get_bool("/editor/highlight_current_line")
		if value == None: value = False
		self.highlight_current_line.set_active(value)

		value = self.c.get_bool("/editor/spaces_instead_of_tabs")
		if value == None: value = False
		self.spaces_instead_of_tabs.set_active(value)

		value = self.c.get_bool("/editor/highlight_matching_bracket")
		if value == None: value = False
		self.matching_bracket.set_active(value)

		value = self.c.get_bool("/editor/display_right_margin")
		if value == None: value = False
		self.right_margin.set_active(value)

		value = self.c.get_bool("/editor/syntax_highlighting")
		if value == None: value = False
		self.syntax_highlighting.set_active(value)

		value = self.c.get_bool("/general/use_system_font")
		if value == None: value = False
		self.use_system_terminal_font.set_active(value)

		value = self.c.get_bool("/general/respawn_r")
		if value == None: value = False
		self.respawn_r.set_active(value)

		value = self.c.get_bool("/general/save_r_history")
		if value == None: value = False
		self.save_r_history.set_active(value)

		value = self.c.get_bool("/colors/use_system_colors")
		if value == None: value = False
		self.use_system_colors.set_active(value)

		# Set the font button state from gconf settings
		value = self.c.get_str("/general/font")
		if value == None: value = "Monospace 10"
		self.font_btn.set_font_name(value)

		# Set the color buttons states from gconf settings
		value_fg = self.c.get_color("/colors/foreground")
		value_bg = self.c.get_color("/colors/background")
		if value_fg == None: value_fg = gtk.gdk.color_parse("#000000")
		if value_bg == None: value_bg = gtk.gdk.color_parse("#FFFFFF")
		self.foreground_color_btn.set_color(value_fg)
		self.background_color_btn.set_color(value_bg)

		# Set the value of the tab width spin button from the gconf setting
		try:
			value = int(self.c.get_str("/editor/tabs_width"))
		except (ValueError, TypeError):
			value = 8
		self.tab_spin_btn.set_value(value)

		# XXX Set the value for the color scheme combobox
	
	# Toggle Buttons Callbacks
    # XXX The callback methods share a lot of code.
    #     Write a function to update the editor_nb at once
    #     and not every time a callback is called.
	def system_font_cb(self, widget, *args):
		""" enable use of the system font """
		if self.use_system_terminal_font.get_active():
			self.c.set_bool("/general/use_system_font", True)
			self.font_btn.set_sensitive(False)
			self.label_004.set_sensitive(False)
			font = self.c.get_string("/desktop/gnome/interface/monospace_font_name")
			for page in self.editor_nb:
				view = page.get_view()
				view.modify_font(pango.FontDescription(font))
			self.rconvt.set_font_from_string(font)
		else:
			self.c.set_bool("/general/use_system_font", False)
			self.font_btn.set_sensitive(True)
			self.label_004.set_sensitive(True)
			font = self.c.get_str("/general/font")
			for page in self.editor_nb:
				view = page.get_view()
				view.modify_font(pango.FontDescription(font))
			self.rconvt.set_font_from_string(font)

	def system_colors_cb(self, widget, *args):
		""" enable use of system colors """
		if self.use_system_colors.get_active():
			color_fg = gtk.gdk.color_parse("#000000")
			color_bg = gtk.gdk.color_parse("#FFFFFF")
			for page in self.editor_nb:
				view = page.get_view()
				view.modify_text(gtk.STATE_NORMAL, color_fg)
				view.modify_base(gtk.STATE_NORMAL, color_bg)
			# XXX: the foreground color is only shown if the widget refreshes
			#      is there a method to do it automatically?
			self.rconvt.set_foreground_color(color_fg)
			self.rconvt.set_background_color(color_bg)

			self.c.set_bool("/colors/use_system_colors", True)
			self.foreground_color_btn.set_sensitive(False)
			self.background_color_btn.set_sensitive(False)
			self.color_cmb.set_sensitive(False)
			self.label_001.set_sensitive(False)
			self.label_002.set_sensitive(False)
			self.label_003.set_sensitive(False)
		else:
			color_fg = self.c.get_color("/colors/foreground")
			color_bg = self.c.get_color("/colors/background")
			for page in self.editor_nb:
				view = page.get_view()
				view.modify_text(gtk.STATE_NORMAL, color_fg)
				view.modify_base(gtk.STATE_NORMAL, color_bg)
			# XXX: the foreground color is only shown if the widget refreshes
			#      is there a method to do it automatically?
			self.rconvt.set_foreground_color(color_fg)
			self.rconvt.set_background_color(color_bg)
			self.c.set_bool("/colors/use_system_colors", False)
			self.foreground_color_btn.set_sensitive(True)
			self.background_color_btn.set_sensitive(True)
			self.color_cmb.set_sensitive(True)
			self.label_001.set_sensitive(True)
			self.label_002.set_sensitive(True)
			self.label_003.set_sensitive(True)

	def line_numbers_cb(self, widget, *args):
		""" shows the line numbers in the script editor """
		if self.line_numbers.get_active():
			for page in self.editor_nb:
				view = page.get_view()
				view.set_show_line_numbers(True)
			self.c.set_bool("/editor/display_line_numbers", True)
		else:
			for page in self.editor_nb:
				view = page.get_view()
				view.set_show_line_numbers(False)
			self.c.set_bool("/editor/display_line_numbers", False)

	def highlight_current_line_cb(self, widget, *args):
		""" highlight the current line in the script editor """
		if self.highlight_current_line.get_active():
			for page in self.editor_nb:
				view = page.get_view()
				view.set_highlight_current_line(True)
			self.c.set_bool("/editor/highlight_current_line", True)
		else:
			for page in self.editor_nb:
				view = page.get_view()
				view.set_highlight_current_line(False)
			self.c.set_bool("/editor/highlight_current_line", False)

	def right_margin_cb(self, widget, *args):
		""" shows a line on the margin, defaults to 80 characters """
		if self.right_margin.get_active():
			for page in self.editor_nb:
				view = page.get_view()
				view.set_show_margin(True)
			self.c.set_bool("/editor/display_right_margin", True)
		else:
			for page in self.editor_nb:
				view = page.get_view()
				view.set_show_margin(False)
			self.c.set_bool("/editor/display_right_margin", False)

	def syntax_highlighting_cb(self, widget, *args):
		""" enable syntax highlighting on the console """
		if self.syntax_highlighting.get_active():
			for page in self.editor_nb:
				buffer = page.get_buffer()
				buffer.set_highlight(True)
			self.c.set_bool("/editor/syntax_highlighting", True)
		else:
			for page in self.editor_nb:
				buffer = page.get_buffer()
				buffer.set_highlight(False)
			self.c.set_bool("/editor/syntax_highlighting", False)

	def matching_bracket_cb(self, widget, *args):
		""" show matching brackets in the script editor """
		if self.matching_bracket.get_active():
			for page in self.editor_nb:
				buffer = page.get_buffer()
				buffer.set_check_brackets(True)
			self.c.set_bool("/editor/highlight_matching_bracket", True)
		else:
			for page in self.editor_nb:
				buffer = page.get_buffer()
				buffer.set_check_brackets(False)
			self.c.set_bool("/editor/highlight_matching_bracket", False)

	def spaces_instead_of_tabs_cb(self, widget, *args):
		""" use spaces instead of tabs in the script editor """
		if self.spaces_instead_of_tabs.get_active():
			for page in self.editor_nb:
				view = page.get_view()
				view.set_insert_spaces_instead_of_tabs(True)
			self.c.set_bool("/editor/spaces_instead_of_tabs", True)
		else:
			for page in self.editor_nb:
				view = page.get_view()
				view.set_insert_spaces_instead_of_tabs(False)
			self.c.set_bool("/editor/spaces_instead_of_tabs", False)

	def indentation_cb(self, widget, *args):
		""" enables automatic indentation in the script editor """
		if self.indentation.get_active():
			for page in self.editor_nb:
				view = page.get_view()
				view.set_auto_indent(True)
			self.c.set_bool("/editor/automatic_indentation", True)
		else:
			for page in self.editor_nb:
				view = page.get_view()
				view.set_auto_indent(False)
			self.c.set_bool("/editor/automatic_indentation", False)

	def respawn_r_cb(self, widget, *args):
		""" if the R process terminates respawn it """
		if self.respawn_r.get_active():
			self.c.set_bool("/general/respawn_r", True)
		else:
			self.c.set_bool("/general/respawn_r", False)

	def save_r_history_cb(self, widget, *args):
		""" save the r history """
		if self.save_r_history.get_active():
			self.c.set_bool("/general/save_r_history", True)
		else:
			self.c.set_bool("/general/save_r_history", False)

	# Font and Color Buttons
	def set_font(self, widget, *args):
		""" sets the console and editor font """
		font = widget.get_font_name()
		for page in self.editor_nb:
			view = page.get_view()
			view.modify_font(pango.FontDescription(font))
		self.rconvt.set_font_from_string(font)
		self.c.set_str("/general/font", font)

	def set_foreground_color(self, widget, *args):
		""" sets the foreground color for the console and editor """
		color = widget.get_color()
		for page in self.editor_nb:
			view = page.get_view()
			view.modify_text(gtk.STATE_NORMAL, color)
		# XXX: the foreground color is only shown if the widget refreshes
		#      is there a method to do it automatically?
		self.rconvt.set_foreground_color(color)
		self.c.set_color("/colors/foreground", color)

	def set_background_color(self, widget, *args):
		""" sets the background color for the console and editor """
		color = widget.get_color()
		for page in self.editor_nb:
			view = page.get_view()
			view.modify_base(gtk.STATE_NORMAL, color)
		self.rconvt.set_background_color(color)
		self.c.set_color("/colors/background", color)

	# Tab Width Spin Button
	def tab_width_change(self, widget, *args):
		""" sets the tab width """
		value = self.tab_spin_btn.get_value_as_int()
		self.c.set_str("/editor/tabs_width", value)

	# Builtin Color Schemes Combobox
	def color_cmb_changed(self, widget, *args):
		""" sets values for the color schemes combobox """
		active = self.color_cmb.get_active()
		model  = self.color_cmb.get_model()
		sel = model[active][0]

		white = gtk.gdk.color_parse("white")
		black = gtk.gdk.color_parse("black")
		green = gtk.gdk.color_parse("green")

		# Black on White
		if active == 0:
			color_bg = white
			color_fg = black
		# White on Black	
		elif active == 1: 
			color_bg = black
			color_fg = white
		# Green on Black
		elif active == 2: 
			color_bg = black
			color_fg = green

		for page in self.editor_nb:
			view = page.get_view()
			view.modify_base(gtk.STATE_NORMAL, color_bg)
			view.modify_text(gtk.STATE_NORMAL, color_fg)
		self.rconvt.set_background_color(color_bg)
		self.rconvt.set_foreground_color(color_fg)

		self.c.set_color("/colors/background", color_bg)
		self.c.set_color("/colors/foreground", color_fg)
		self.c.set_str("/colors/buildin_scheme", active)

	# Dialog Buttons
	def help_activate(self, widget, *args):
		""" displays the help window """
		print "Help Button Pressed"

	def close(self, widget, *args):
		"""
			closes the Preferences Window
		"""
		self.prefdlg.hide()
