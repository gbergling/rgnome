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

from gettext import gettext as _

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import pango
import gtksourceview

class PrintData:
	""" Helper class storing print job data """
	text = None
	layout = None
	page_breaks = None

class PrintFactory:
	""" Printing facilities """
	def __init__(self):
		""" 
		Print/preview initialization
		"""
		self.print_settings = gtk.PrintSettings()
		self.page_setup = gtk.PageSetup()

	def show_page_setup(self, parent):
		"""
		Show page setup dialog

		@parent - gtk.Widget - Parent widget
		"""
		self.page_setup = gtk.print_run_page_setup_dialog(parent, 
														self.page_setup, 
														self.print_settings)

	def script_print_preview(self, textbuf):
		"""
		Show print preview

		@param textbuf - gtk.TextBuffer - Text to print
		"""
		print_data = PrintData()
		print_data.text = textbuf.get_text(textbuf.get_start_iter(), 
											textbuf.get_end_iter())

		self.job = gtk.PrintOperation()
		self.job.set_default_page_setup(self.page_setup)
		self.job.set_print_settings(self.print_settings)

		self.job.connect("begin_print", self.__begin_print, print_data)
		self.job.connect("draw_page", self.__draw_page, print_data)

		res = self.job.run(gtk.PRINT_OPERATION_ACTION_PREVIEW)

	def script_print(self, textbuf):
		"""
		Print passed text according to page settings

		@param textbuf - gtk.TextBuffer - Text to print
		"""
		print_data = PrintData()
		print_data.text = textbuf.get_text(textbuf.get_start_iter(), 
											textbuf.get_end_iter())

		self.job = gtk.PrintOperation()
		self.job.set_default_page_setup(self.page_setup)
		self.job.set_print_settings(self.print_settings)

		self.job.connect("begin_print", self.__begin_print, print_data)
		self.job.connect("draw_page", self.__draw_page, print_data)

		try:
			res = self.job.run(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG)
		except gobject.GError, ex:
			error_dialog = gtk.MessageDialog(main_window,
										gtk.DIALOG_DESTROY_WITH_PARENT,
										gtk._MESSAGE_ERROR,
										gtk.BUTTONS_CLOSE,
										("Error printing file:\n%s" % str(ex)))
			error_dialog.connect("response", gtk.Widget.destroy)
			error_dialog.show()
		else:
			if res == gtk.PRINT_OPERATION_RESULT_APPLY:
				self.print_settings = self.job.get_print_settings()

	def __begin_print(self, operation, context, print_data):
		"""
		Callback method for setting initial print status

		@param operation - gtk.PrintOperation - Caller object
		@param context - gtk.PrintContext - Device where pages are printed
		@param print_data - PrintData - Helper object holding data to be printed
		"""
		width = context.get_width()
		height = context.get_height()
		print_data.layout = context.create_pango_layout()
		print_data.layout.set_font_description(pango.FontDescription("Sans 12"))
		print_data.layout.set_width(int(width*pango.SCALE))
		print_data.layout.set_text(print_data.text)

		num_lines = print_data.layout.get_line_count()

		page_breaks = []
		page_height = 0

		for line in xrange(num_lines):
			layout_line = print_data.layout.get_line(line)
			ink_rect, logical_rect = layout_line.get_extents()
			lx, ly, lwidth, lheight = logical_rect
			line_height = lheight / 1024.0
			if page_height + line_height > height:
				page_breaks.append(line)
				page_height = 0
			page_height += line_height

		operation.set_n_pages(len(page_breaks) + 1)
		print_data.page_breaks = page_breaks

	def __draw_page(self, operation, context, page_nr, print_data):
		"""
		Callback method	for printing specified page

		@param operation - gtk.PrintOperation - Caller object
		@param context - gtk.PrintContext - Device where the page is printed
		@param page_nr - integer - Number of the page to print
		@param print_data - PrintData - Helper object holding data to be printed
		"""
		assert isinstance(print_data.page_breaks, list)
		if page_nr == 0:
			start = 0
		else:
			start = print_data.page_breaks[page_nr - 1]

		try:
			end = print_data.page_breaks[page_nr]
		except IndexError:
			end = print_data.layout.get_line_count()

		cr = context.get_cairo_context()

		cr.set_source_rgb(0, 0, 0)

		i = 0
		start_pos = 0
		iter = print_data.layout.get_iter()
		while 1:
			if i >= start:
				line = iter.get_line()
				none, logical_rect = iter.get_line_extents()
				lx, ly, lwidth, lheight = logical_rect
				baseline = iter.get_baseline()
				if i == start:
					start_pos = ly / 1024.0;
				cr.move_to(lx / 1024.0, baseline / 1024.0 - start_pos)
				cr.show_layout_line(line)
			i += 1
			if not (i < end and iter.next_line()):
				break

