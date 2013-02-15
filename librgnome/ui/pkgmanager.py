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


import os, sys
from gettext import gettext as _

import pygtk
pygtk.require('2.0')
import gtk, gtk.glade, gtk.gdk
import gobject

from rpy import *

class PkgManager:
	""" implements the MainWindow and all its GUI compoments """
	def __init__(self):
		""" 
			Create and show the package manager dialog
		"""
		self.wTree = gtk.glade.XML('resource%spkgbrowser.glade' % os.sep, "pkgbrowser")
		self.window = self.wTree.get_widget('pkgbrowser')
		self.pkgtree = self.wTree.get_widget('pkgtree')
		self.live_text = self.wTree.get_widget('live_text')
		self.info = self.wTree.get_widget('info_label')
		self.CRAN_combo = self.wTree.get_widget('CRAN_combo')

		dic_dialog = {
			'on_pkgbrowser_delete_event': lambda x,y : self.window.destroy(),
			'on_close_btn_clicked': lambda x: self.window.destroy(),
			'on_refresh_btn_clicked': self.refresh,
			'on_update_btn_clicked': self.update_packages,
			'on_pkgtree_button_release_event': self.pkgtree_row_selected,
			'on_live_text_changed': self.live_search}
		self.wTree.signal_autoconnect(dic_dialog)

		self.packages = {}
		self.model = gtk.ListStore(	gobject.TYPE_STRING, 
									gobject.TYPE_BOOLEAN,
									gobject.TYPE_BOOLEAN)

		# init tree view
		self.pkgtree.set_model(self.model)	

		# package name
		cell = gtk.CellRendererText()

		column = gtk.TreeViewColumn(_("Installed packages"))
		self.pkgtree.append_column(column)
		column.pack_start(cell, True)
		column.add_attribute(cell, 'text', 0)
		column.set_sort_column_id(0)

		# package_loaded status
		cell = gtk.CellRendererToggle()
		cell.set_property('activatable', True)
		cell.connect('toggled', self.pkgloaded_toggled, self.model)

		column = gtk.TreeViewColumn(_("loaded"))
		self.pkgtree.append_column(column)
		column.pack_start(cell, True)
		column.add_attribute(cell, 'active', 1)
		column.set_sort_column_id(1)

		self.load_pkglist()
		self.synch_model()
		self.populate_CRAN_combo()

		self.window.show()
		self.live_text.grab_focus()

	def load_pkglist(self):
		"""
			Walk through all the packages dir and import every subdir
		"""

		self.packages = {}
		libpaths = with_mode(BASIC_CONVERSION, lambda: r(".libPaths()"))()
		for libpath in libpaths:
			for pkg in os.listdir(libpath):
				if os.path.isdir(libpath + os.sep + pkg):
					self.packages[pkg] = libpath + os.sep + pkg
				# don't block the gui when loading many packages
				while gtk.events_pending():
					gtk.main_iteration()

	def synch_model(self, filter_text=None):
		""" 
		Synchronize treeview model over current self.packages
		rebuilding the model from scratch
		"""

		self.model.clear()
		loaded_pkg_list = self.get_loaded_packages()

		for name in self.packages.keys():
			if filter_text and (name.find(filter_text) < 0):
				continue
			rowiter = self.model.append()
			self.model.set_value(rowiter, 0, name)
			self.model.set_value(rowiter, 1, name in loaded_pkg_list)

	def synch_loaded(self):
		""" 
		Synchronize treeview model package_loaded status field only
		without rebouilding the model from scratch
		"""

		loaded_pkg_list = self.get_loaded_packages()

		for row in self.model:
			row[1] = row[0] in loaded_pkg_list

	def refresh(self, *args, **kargs):
		""" 
		Reloads package list and rebuild treeview model
		"""

		self.load_pkglist()
		self.synch_model()
		self.live_text.set_text("")

	def get_loaded_packages(self):
		""" 
		Get the list of loaded packages

		@return - list - loaded packages' names
		"""

		loaded = []
		full_list = with_mode(BASIC_CONVERSION, lambda: r.search())()
		for item in full_list:
			if item.startswith("package:"):
				loaded.append(item.split(":")[1])

		return loaded

	def pkgloaded_toggled(self, cell, path, model):
		""" 
		Toggle loaded status for selected package
		"""
		model[path][1] = not model[path][1]

		if model[path][1]:
			r.library(model[path][0])
		else:
			r.detach("package:" + model[path][0])

		self.synch_loaded()

	def populate_CRAN_combo(self):
		"""
		Fill CRAN combobox with mirror list retrieved from:
			/usr/share/R/doc/CRAN_mirrors.csv
		"""

		self.CRAN_model = gtk.ListStore(gobject.TYPE_STRING, 
										gobject.TYPE_STRING,
										gobject.TYPE_STRING)

		self.CRAN_combo.set_model(self.CRAN_model)

		# CRAN name
		cell = gtk.CellRendererText()
		self.CRAN_combo.pack_start(cell, True)
		self.CRAN_combo.add_attribute(cell, 'text', 2)

		# CRAN location
		cell = gtk.CellRendererText()
		self.CRAN_combo.pack_end(cell, False)
		self.CRAN_combo.add_attribute(cell, 'text', 0)

		# Open CRAN_mirrors.csv
		filename = RHOME + os.sep + "doc" + os.sep + "CRAN_mirrors.csv"
		if os.path.isfile(filename):
			CRAN_mirrors = open(filename)
		elif os.path.isfile("/usr/share/R/doc/CRAN_mirrors.csv"):
			CRAN_mirrors = open("/usr/share/R/doc/CRAN_mirrors.csv", "r")
		else:
			print _("Cannot retrieve CRAN mirrors")

		# Populate combobox with mirrors
		for line in CRAN_mirrors:
			fields = line.split(",")
			if fields[0] == "Name":
				continue
			item = (fields[0].replace("\"", ""), 
					fields[3], 
					fields[4].replace("\"", ""))

			self.CRAN_model.append(item)

	def update_packages(self, widget):
		"""
		Update installed packages agains latest version present on CRAN
		"""

		# assert the user selected a CRAN mirror, otherwise advise it.
		if self.CRAN_combo.get_active() < 0 :
			dialog = gtk.MessageDialog(	
								parent = self.window, 
								flags = gtk.DIALOG_MODAL,
								type = gtk.MESSAGE_INFO, 
								buttons = gtk.BUTTONS_NONE,
								message_format = _("CRAN mirror not specified"))

			dialog.format_secondary_text(
				_("Select a CRAN mirror from the list, then click update."))

			dialog.set_title(_("Information"))
			dialog.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
			dialog.run()
			dialog.destroy()
			return
		else:
			item = self.CRAN_model[self.CRAN_combo.get_active()]

		# perform packages update, report the error if unable to connect CRAN
		try:
			r.update_packages(mirror=item[1])
		except RException, e:
			error = _("Cannot update packages")
			#error += ()

			dialog = gtk.MessageDialog(	parent = self.window, 
										flags = gtk.DIALOG_MODAL,
										type = gtk.MESSAGE_ERROR, 
										buttons = gtk.BUTTONS_NONE,
										message_format = error)

			dialog.format_secondary_text("CRAN:\t%s\nurl:\t\t%s\n\n%s" 
										%(item[2],item[1],str(e)))
			dialog.set_title(_("Error"))
			dialog.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
			dialog.run()
			dialog.destroy()
		
	def pkgtree_row_selected(self, widget, event):
		"""
		Show description of the selected package

		@param widget - gtk.TreeView - TreeView that triggered the event
		@param event - ? - button release event 
		"""

		selection = self.pkgtree.get_selection()
		if not selection:
			return

		(model, pathlist) = selection.get_selected_rows()

		# push into dictionary package description fields
		for path in pathlist:
			self.info.set_text("")
			row = model.get_iter(path)
			name = model[row][0]
			fields = {}
			try:
				info = open(self.packages[name] + os.sep + "DESCRIPTION", "r")
				for line in info:
					tokens = line.split(":")
					if len(tokens) == 2:						
						fields[tokens[0]] = tokens[1].replace("\n","")
			finally:
				info.close()

		# pretty-print package description on screen
		try:
			text = "%s %s\n" %(fields["Package"], fields["Version"])
			text +="%s\n\n" %(fields["Title"])
			text += "Author: %s\n" %(fields["Author"])
			text += "Mantainer: %s\n" %(fields["Maintainer"])
			text += "License: %s\n\n" %(fields["License"])
			text += fields["Description"]
		except:
			text = _("Cannot retrieve package description for ") + name

		self.info.set_use_markup(True)
		self.info.set_text(text)

	def live_search(self, widget):

		self.synch_model(self.live_text.get_text())
		if self.live_text.get_text():
			self.live_text.modify_base(gtk.STATE_NORMAL, 
										gtk.gdk.color_parse("#FBFAD6"))
		else:
			self.live_text.modify_base(gtk.STATE_NORMAL, None)


if __name__ == "__main__":
    PkgManager()
    gtk.main()
