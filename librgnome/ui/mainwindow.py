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


import os, sys, codecs, shutil, re
from gettext import gettext as _

import pygtk
pygtk.require('2.0')
import gtk, gtk.glade, gtk.gdk, gtksourceview

import gnome
import gnome.ui
import gnomevfs
import gnomeprint.ui

from librgnome import config
from librgnome.ui import about 
from librgnome.ui import editor, rconsole, helpbrowser
from librgnome.ui import statusbar, scriptitem, searchbar
from librgnome.ui import preferences, printing, replacebar
from librgnome.ui import rpyconsole
from librgnome.ui import objectbrowser
from librgnome.ui import pkgmanager

class MainWindow:
	""" implements the MainWindow and all its GUI compoments """
	def __init__(self):
		""" 
			Initiats the MainWindow, while loading the respective
		    	glade file, creating the main widgets and connects the
			signals.
		"""
		# read the respective glad file and create the widget tree
		self.wTree = gtk.glade.XML('resource%srgnome.glade' % os.sep, 'MainWindow')
		self.scripts = []
		self.helps = []
		self.file_wks = None
		self.print_factory = printing.PrintFactory()
		self.object_browser = objectbrowser.ObjectBrowser(
								self.wTree.get_widget('sb_treeview'))

		# Define constants to identify current running mode
		self.MODE_CONSOLE = 0
		self.MODE_EDITOR = 1
		self.MODE_HELP = 2

		self.c = config.config()
    
		gnome.init('RGnome', self.c.get_version())

		# create the main widgets
		self.window = self.wTree.get_widget('MainWindow')
		self.rconsole = self.wTree.get_widget('rconsole')
		self.rconsb	= self.wTree.get_widget('rconsb')
		self.helpbrowser_nb = self.wTree.get_widget('helpbrowser_nb')
		self.editor_nb = self.wTree.get_widget('editor_notebook')
		self.main_nb = self.wTree.get_widget('main_notebook')
		self.main_nb.set_show_tabs(False)
		self.sb = statusbar.statusbar(self.wTree)

		# Main Checkboxes
		self.console_mode_btn = self.wTree.get_widget('console_mode')
		self.editor_mode_btn = self.wTree.get_widget('editor_mode')
		self.help_mode_btn = self.wTree.get_widget('help_mode')
		
		# Initial mark the status as busy
		self.sb.push_status(1)

		self.tb_console = self.wTree.get_widget('tb_console')
		self.tb_editor = self.wTree.get_widget('tb_editor')
		self.tb_help = self.wTree.get_widget('tb_help')
		self.vbox = self.wTree.get_widget('vbox1')
		self.live_text = self.wTree.get_widget('live_text')
		self.search_bar = searchbar.searchbar(self.editor_nb, self.wTree)
		self.replace_bar = replacebar.replacebar(self.editor_nb, self.wTree)

		# create a clipboard object
		display = gtk.gdk.display_manager_get().get_default_display()
		self.cb = gtk.Clipboard(display, "CLIPBOARD")

		# set the window / application icon
		img = os.path.abspath(os.getcwd()) + "%sresource%srgnome.png" % (os.sep, os.sep)
		self.icon = gtk.gdk.pixbuf_new_from_file(img)
		self.window.set_icon(self.icon)
		self.smallicon = gtk.gdk.pixbuf_new_from_file_at_size(img, 24, 24)
		self.wTree.get_widget('console_mode_icon').set_from_pixbuf(self.smallicon)

		# create rpy console
		self.rpyconsole = rpyconsole.Rpyconsole()
		self.rpyconsole.set_editable(False)
		self.rpyconsole_input = self.wTree.get_widget('rpyconsole_input')
		self.rpyconsole_input.grab_focus()
		viewport = self.wTree.get_widget('rpyconsole')
		viewport.add(self.rpyconsole)
		self.rpyconsole.show()

		# define our menu callbacks and connect the signals
		dic_window = {'on_MainWindow_delete_event' : self.destroy}
		dic_file = {
			'on_new_activate' : self.item_new,
			'on_open_activate' : self.item_open,
			'on_save_activate' : self.item_save,
			'on_save_as_activate' : self.item_save_as,
			'on_close_activate' : self.item_close,
			'on_page_setup_activate' : self.page_setup,
			'on_script_print_preview_activate' : self.script_print_preview,
			'on_script_print_activate' : self.script_print,
			'on_quit_activate' : self.destroy}
		dic_edit = {
			'on_undo_activate' : self.edit_undo,
			'on_redo_activate' : self.edit_redo,
			'on_cut_activate' : self.edit_cut,
			'on_copy_activate': self.edit_copy,
			'on_paste_activate': self.edit_paste,
			'on_delete_activate': self.edit_delete,
			'on_select_all_activate': self.edit_select_all,
			'on_preferences_activate': self.edit_preferences}
		dic_help = {
			'on_about_activate' : self.show_aboutdlg}
		dic_tb_editor = {
			'on_tbe_new_clicked' : self.script_new,
			'on_tbe_open_clicked' : self.script_open,
			'on_tbe_close_clicked' : self.script_close, 
			'on_tbe_save_clicked' : self.script_save,
			'on_tbe_find_clicked' : self.find_cb,
			'on_tbe_find_replace_clicked': self.replace_cb,
			'on_tbe_execute_clicked' : self.execute}
		dic_find = {
			'on_find_activate' : self.find_cb,
			'on_find_next_activate' : self.find_cb,
			'on_find_previous_activate' : self.find_cb,
			'on_replace_activate' : self.replace_cb,
			'on_goto_line_activate' : self.goto_line_cb}
		dic_tb_console = {
			'on_tbc_open_clicked' : self.workspace_open,
			'on_tbc_save_clicked' : self.workspace_save,
			'on_tbc_save_as_clicked' : self.workspace_save_as,
			'on_tbc_execute_clicked' : self.execute,
			'on_tbc_clear_clicked' : self.console_clear_output,
			'on_tbc_pkgmanager_clicked': self.show_package_manager}
		dic_tb_help = {
			'on_tbh_back_clicked' : self.help_back,
			'on_tbh_forward_clicked' : self.help_forward,
			'on_tbh_new_clicked' : self.help_new,
			'on_tbh_print_clicked' : self.script_print}
		dic_helpbrowser_nb = {
			'on_helpbrowser_nb_switch_page' : self.helpbrowser_nb_switch}
		dic_editor_nb = {
			'on_editor_notebook_select_page' : self.nb_select_cb,
			'on_editor_notebook_switch_page' : self.nb_switch_cb}
		dict_main_notebook = {
			'on_main_notebook_switch_page' : self.main_nb_switch_cb}
		dict_main_button_box = {
			'on_console_mode_toggled' : self.set_mode_console,
			'on_editor_mode_toggled' : self.set_mode_editor,
			'on_help_mode_toggled' : self.set_mode_help}
		dict_rpyconsole = {
			'on_rpyconsole_input_activate' : self.console_eval_expression,
			'on_rpyconsole_button_clicked' : self.console_eval_expression,
			'on_rpyconsole_input_key_press_event' : self.console_key_pressed}
		dict_live_widgets = {
			'on_live_text_activate' : self.live_search,
			'on_live_text_changed' : self.live_search_changed}

		self.wTree.signal_autoconnect(dic_window)
		self.wTree.signal_autoconnect(dic_file)
		self.wTree.signal_autoconnect(dic_edit)
		self.wTree.signal_autoconnect(dic_find)
		self.wTree.signal_autoconnect(dic_help)
		self.wTree.signal_autoconnect(dic_tb_console)
		self.wTree.signal_autoconnect(dic_tb_editor)
		self.wTree.signal_autoconnect(dic_tb_help)
		self.wTree.signal_autoconnect(dic_helpbrowser_nb)
		self.wTree.signal_autoconnect(dic_editor_nb)
		self.wTree.signal_autoconnect(dict_main_notebook)
		self.wTree.signal_autoconnect(dict_main_button_box)
		self.wTree.signal_autoconnect(dict_rpyconsole)
		self.wTree.signal_autoconnect(dict_live_widgets)

		# finally show the widgets and the main window
		self.editor_nb.show()
		self.helpbrowser_nb.show()
		self.main_nb_switch_cb(self.main_nb, None, self.main_nb.get_current_page())
		self.window.show()

		# at startup create on empty script in the editor per default
		self.editor_nb.remove_page(0)		
		self.script_new()

		# at startup create on empty script in the editor per default
		self.help_new()
		
		# Drag and Drop Support
        # XXX - d'n'd isn't working on the rootwindow.
        #     - make a dnd event on the rconsole executeing the droped
        #       text?
		self.TARGET_TYPE_TEXT = 80
		self.TARGET_ROOTWIN   = 1
		self.targets = [("text/plain", 0, self.TARGET_TYPE_TEXT),
			("application/x-rootwin-drop", 0, self.TARGET_ROOTWIN)]
		self.editor_nb.drag_dest_set(gtk.DEST_DEFAULT_ALL, 
			self.targets,
			gtk.gdk.ACTION_MOVE)
		# Drag and Drop Callbacks for the editor notebook
		self.editor_nb.connect("drag_motion", self.drag_callback)
		self.editor_nb.connect("drag_drop", self.drop_callback)
		self.editor_nb.connect("drag_data_received", self.data_received_callback)
		# Drag and Drop Callbacks for the root window
		self.window.connect("drag_motion", self.drag_callback)
		self.window.connect("drag_drop", self.drop_callback)
		self.window.connect("drag_data_received", self.data_received_callback)
		# Drag and Drop Callbacks for the rconsole
		#self.rconsole.connect("drag_motion", self.drag_callback)
		#self.rconsole.connect("drag_drop", self.drop_callback)
		#self.rconsole.connect("drag_data_received", self.rconsole_data_received_callback)

		self.sb.cursor.set_sensitive(False)
		self.sb.push_status(0)

		self.update_window_title()

	# Drag and Drop Callbacks
	def drag_callback(self, wid, context, x, y, time):
		context.drag_status(gtk.gdk.ACTION_MOVE, time)
	def drop_callback(self, wid, context, x, y, time):
		#self.editor.set_text("")
		return
	def data_received_callback(self, widget, drag_context, x, y, selection_data, 
							   target_type, time):
		if target_type == self.TARGET_TYPE_TEXT:
			data = selection_data.get_text()
			filename = gnomevfs.get_local_path_from_uri(data)
			filename = filename[0:-1]
			self.script_open(filename = filename)
		else:
			print "could not load file"
	def rconsole_data_received_callback(self, widget, drag_context, x, y, selection_data, 
							   target_type, time):
		if target_type == self.TARGET_TYPE_TEXT:
			data = selection_data.get_text()
			filename = gnomevfs.get_local_path_from_uri(data)
			filename = filename[0:-1]
			self.script_open(filename = filename)
			self.execute()
		else:
			print "could not load file"

	# menu functions

	def live_search(self, widget):
		""" Process live search when the user presses enter or the button """

		text = self.live_text.get_text()
		current_mode = self.get_current_mode()

		if current_mode == self.MODE_CONSOLE:
			self.live_search_changed(widget)
		elif current_mode == self.MODE_HELP:
			help = self.get_current_help()
			if help:
				help.help_call(text)
				self.update_window_title()

	def live_search_changed(self, widget):
		""" Process live search when the user presses enter or the button """

		text = self.live_text.get_text()
		current_mode = self.get_current_mode()

		if current_mode == self.MODE_CONSOLE:
			self.object_browser.set_filter(self.live_text.get_text())
			if self.live_text.get_text():
				self.live_text.modify_base(gtk.STATE_NORMAL, 
											gtk.gdk.color_parse("#FBFAD6"))
			else:
				self.live_text.modify_base(gtk.STATE_NORMAL, None)

	def item_new(self, widget):
		""" Creates a new item according to current mode"""

		mode = self.get_current_mode()
		
		if mode == self.MODE_EDITOR:
			self.script_new()
		elif mode == self.MODE_HELP:
			self.help_new()

	def script_new(self, *args, **kargs):
		""" Creates a new/empty script in the script editor """

		name = _("New Script")

		# check for duplicate names
		script_names = self.get_script_short_names()
		duplicate = script_names.count(name)
		occurrences = 0
		while(duplicate):
			occurrences += 1			
			name = _("New Script") + " (%s)" % (occurrences + 1)
			duplicate = script_names.count(name)

		# create a new script & editor
		nb_tab = editor.editor(self)
		script = scriptitem.Script(name, nb_tab.get_buffer())
		self.scripts.append(script)

		# connect tab's close button and get tab controls
		script.get_tab_close_button().connect('clicked', self.script_close)
		hbox = script.get_tab_hbox()

		self.index = self.editor_nb.append_page(nb_tab, hbox)

		buffer = script.get_buffer()
		buffer.connect('mark_set', self.update_cursor_position)
		buffer.connect('changed', self.buffer_changed_cb)

		self.editor_nb.get_nth_page(self.index).set_size_request(100,50)
		self.editor_nb.get_nth_page(self.index).show()
		self.editor_nb.set_current_page(self.index)
		self.sb.push_textfield(_("New script created"))

		self.update_window_title()
		return script
		
	def help_new(self, *args, **kargs):
		""" Creates a help browser item loading passed name """

		name = _("New Script")

		# create a new help browser
		help = helpbrowser.HelpBrowser()

		# Add new script to the list and create the respective script editor
		self.helps.append(help)

		# connect tab's close button and get tab controls
		help.get_tab_close_button().connect('clicked', self.help_close)
		hbox = help.get_tab_hbox()

		index = self.helpbrowser_nb.append_page(help.get_view(), hbox)

		self.helpbrowser_nb.get_nth_page(index).set_size_request(100,50)
		self.helpbrowser_nb.get_nth_page(index).show()
		self.helpbrowser_nb.set_current_page(index)
		self.sb.push_textfield(_("New help item created"))

		return help

	def item_open(self, widget):
		""" Open an existing item according to current mode"""

		mode = self.get_current_mode()
		
		if mode == self.MODE_CONSOLE:
			self.workspace_open()
		elif mode == self.MODE_EDITOR:
			self.script_open()

	def script_open(self, *args, **kargs):
		""" opens an existing script """

		# Read the file and place the content of it into the script editor
		filename = scriptitem.Script("temp", None).load_dialog()
		if not filename: 
			return

		# Check if filename is already opened among available scripts
		filenames = self.get_script_filenames()
		if filename in filenames:
			self.editor_nb.set_current_page(filenames.index(filename))
			self.sb.push_textfield(_("Script already opened"))
			return

		# Open filename into script editor
		script = self.script_new()
		page = self.editor_nb.get_nth_page(self.editor_nb.get_current_page())
		script.load(page.get_buffer(), filename)

		script.set_changed(False)
		self.update_window_title()
		self.sb.push_textfield(_("Script opened from file: ") + 
								script.get_short_name())

	def workspace_open(self, *args, **kargs):
		""" opens an existing workspace """
		filename = None
		try:
			filename = kargs["filename"]
		except:
			chooser = gtk.FileChooserDialog(title   = _("Open R workspace"),\
							action  = gtk.FILE_CHOOSER_ACTION_OPEN,\
							buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
										 gtk.STOCK_OK, gtk.RESPONSE_OK))
			chooser.set_current_folder(os.path.abspath(os.path.curdir))
			for filter in self.get_workspace_filters():
				chooser.add_filter(filter)
			result = chooser.run()
			if result != gtk.RESPONSE_OK:
				chooser.destroy()
				return
			filename = chooser.get_filename()
			chooser.destroy()

		if filename.endswith(".Rdata"):
			# Tell R to open to load the workspace
			text = "load(\""+filename+"\")"
			self.rpyconsole.eval(text)
			self.set_current_file_wks(filename)
			self.object_browser.refresh()
			self.sb.push_textfield(_("workspace loaded from file: "+ filename))

			filename_history = filename.replace(".Rdata", ".Rhistory")
			if os.path.isfile(filename_history):
				self.rpyconsole.history_load(filename_history)
		elif filename.endswith(".Rhistory"):
			self.rpyconsole.hisory_load(filename)

	def get_workspace_filters(self):
		""" sets the filters for the gtk.filechooser dialog """
		result = []
		filter = gtk.FileFilter()
		filter.set_name(_("R data"))
		filter.add_pattern("*.Rdata")
		result.append(filter)
		filter = gtk.FileFilter()
		filter.set_name(_("R history"))
		filter.add_pattern("*.Rhistory")
		result.append(filter)
		filter = gtk.FileFilter()
		filter.set_name(_("All Files"))
		filter.add_pattern("*")
		result.append(filter)
		return result

	def item_close(self, widget):
		""" Close current item according to current mode"""

		mode = self.get_current_mode()
		
		if mode == self.MODE_EDITOR:
			self.script_close(widget)
		elif mode == self.MODE_HELP:
			self.help_close(widget)

	def script_close(self, widget):
		""" 
		Close selected script

		@param widget - gtk.Button - Close button available in each script tab
		@param widget - gtk.MenuItem - Menu item for closing current script
		"""

		# Check if user want to close an arbitrary script or the active one
		if isinstance(widget, gtk.Button):
			buttons = self.get_script_close_buttons()
			index = buttons.index(widget)
			script = self.scripts[index]
		else:
			index = self.editor_nb.get_current_page()
			script = self.get_current_script()

		# Ensure that selected scripts exists
		if not script:
			return

		# Check if the script has unsaved changes
		if script.is_changed():
			dialog = gtk.MessageDialog(type=gtk.MESSAGE_WARNING,\
						message_format=(_("Save the changes to script \"") +
										script.get_short_name() +
										_("\" before closing?")))
			dialog.wrap = True
			dialog.set_icon(self.icon)
			dialog.add_button(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL)
			dialog.add_button(gtk.STOCK_YES,gtk.RESPONSE_YES)
			dialog.add_button(gtk.STOCK_NO,gtk.RESPONSE_NO)
			result = dialog.run()
			dialog.destroy()				
			if result == gtk.RESPONSE_YES:
				self.script_save()
			elif result == gtk.RESPONSE_NO:
				pass
			else:
				return

		# Remove script from notebook and from internal collection
		self.editor_nb.remove_page(index)
		self.scripts.remove(self.scripts[index])

		self.update_window_title()
		self.sb.push_textfield(_("Script closed"))

	def help_close(self, widget):
		""" 
		Close selected script

		@param widget - gtk.Button - Close button available in each help tab
		@param widget - gtk.MenuItem - Menu item for closing current help item
		"""

		# Check if user want to close an arbitrary help item or the active one
		if isinstance(widget, gtk.Button):
			buttons = self.get_help_close_buttons()
			index = buttons.index(widget)
			help = self.helps[index]
		else:
			index = self.helpbrowser_nb.get_current_page()
			help = self.get_current_help()

		# Ensure that selected help item exists
		if not help:
			return

		# Remove help from notebook and from internal collection
		self.helpbrowser_nb.remove_page(index)
		self.helps.remove(self.helps[index])

		if not self.helpbrowser_nb.get_n_pages():
			self.help_new()

		self.update_window_title()
		self.sb.push_textfield(_("Help item closed"))

	def get_help_close_buttons(self):
		"""Returns all close buttons belonging to available scripts"""
		buttons = []
		
		for help in self.helps:
			buttons.append(help.get_tab_close_button())
		
		return buttons

	def item_save(self, widget):
		""" Close current item according to current mode"""

		mode = self.get_current_mode()
		
		if mode == self.MODE_CONSOLE:
			self.workspace_save()
		elif mode == self.MODE_EDITOR:
			self.script_save()

	def item_save_as(self, widget):
		""" Close current item according to current mode"""

		mode = self.get_current_mode()
		
		if mode == self.MODE_CONSOLE:
			self.workspace_save_as()
		elif mode == self.MODE_EDITOR:
			self.script_save_as()

	def script_save(self, *args, **kargs):
		""" saves the currently opened script """
		script = self.get_current_script()

		# Assert that there is at least one script available
		if not script:
			return

		page = self.editor_nb.get_nth_page(self.editor_nb.get_current_page())
		script.save(page.get_buffer(), script.get_filename())

		self.sb.push_textfield(_("Script saved"))

	def script_save_as(self, *args, **kargs):
		""" saves the currently opened script with a different name """
		script = self.get_current_script()

		# Assert that there is at least one script available
		if not script:
			return

		page = self.editor_nb.get_nth_page(self.editor_nb.get_current_page())
		script.save(page.get_buffer(), filename=None)

		self.sb.push_textfield(_("Script saved in this file: ") + 
								script.get_short_name())
	def workspace_save(self, *args, **kargs):
		""" saves the R session with a different name """
		filename = self.get_current_file_wks()
		if filename:
			# Tell R to save workspace into filename
			text = "save.image(\""+filename+"\")"
			self.rpyconsole.eval(text, store_history=False)

			# Save rpyconsole history
			filename_history = filename.replace(".Rdata", ".Rhistory")
			self.rpyconsole.history_save(filename_history)

			self.sb.push_textfield(_("workspace saved"))
		else:
			self.workspace_save_as(None, None)

	def workspace_save_as(self, *args, **kargs):
		""" saves the R session with a different name """
		filename = None
		try:
			filename = kargs["filename"]
		except:
			pass
		# if there is no filename given open the filechooser dialog
		# and let the user name one
		if not filename:
			chooser = gtk.FileChooserDialog(title = _("Save as"),\
				action  = gtk.FILE_CHOOSER_ACTION_SAVE,\
				buttons = (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OK, gtk.RESPONSE_OK))
		if filename:
			chooser = gtk.FileChooserDialog(title = _("Save as"),\
				action  = gtk.FILE_CHOOSER_ACTION_SAVE,\
				buttons = (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OK, gtk.RESPONSE_OK))
			chooser.set_current_folder(os.path.abspath(os.path.dirname(filename)))
			chooser.set_current_name(os.path.basename(filename))
		for filter in self.get_workspace_filters():
			chooser.add_filter(filter)
		chooser.set_do_overwrite_confirmation(True)

		result = chooser.run()
		if result != gtk.RESPONSE_OK:
			chooser.destroy()
			return
		# set the label on the editor notebook with the choosen filename
		filename = chooser.get_filename()
		chooser.destroy()


		if filename.endswith(".Rhistory"):
			#user selected to save only the history
			self.rpyconsole.history_save(filename)
			self.sb.push_textfield(_("command history saved in this file: " + filename))
		else:
			# Ensure that filename ends with .Rdata
			if not filename.endswith(".Rdata"):
				filename += ".Rdata"

			# Tell R to save workspace into filename
			text = "save.image(\""+filename+"\")"
			self.rpyconsole.eval(text, store_history=False)
			self.set_current_file_wks(filename)

			# Save rpyconsole history
			filename_history = filename.replace(".Rdata", ".Rhistory")
			self.rpyconsole.history_save(filename_history)

			self.sb.push_textfield(_("workspace saved in this file: " + filename))

	def page_setup(self, widget):
		"""
		Show page stup dialog
		"""
		self.print_factory.show_page_setup(self.window)
		
	def script_print_preview(self, widget):
		"""	
		Preview print output
		"""
		textbuf = self.get_current_buffer()	
		if textbuf: 
			self.print_factory.script_print_preview(textbuf)

	def script_print(self, widget):
		"""	
		Print current item according to running mode
		"""
		textbuf = self.get_current_buffer()	
		if textbuf: 
			self.print_factory.script_print(textbuf)

	def edit_undo(self, widget):
		"""
			Menu Callback for doing a undo on the current active editor tab
		"""
		buffer = self.editor_nb.get_nth_page(self.editor_nb.get_current_page()).get_buffer()
		if buffer.can_undo():
			buffer.undo()

	def edit_redo(self, widget):
		"""
			Menu Callback for doing a redo on the current active editor tab
		"""
		buffer = self.editor_nb.get_nth_page(self.editor_nb.get_current_page()).get_buffer()
		if buffer.can_redo():
			buffer.redo()


	def edit_select_all(self, widget):
		"""
			Menu Callback for selecting all text
		"""
		buffer = self.editor_nb.get_nth_page(self.editor_nb.get_current_page()).get_buffer()
		view   = self.editor_nb.get_nth_page(self.editor_nb.get_current_page()).get_view()
		start  = buffer.get_start_iter()
		end	   = buffer.get_end_iter()
		buffer.select_range(start, end)

	def edit_cut(self, widget):
		"""
			Menu Callback for cutting the selected text and pasting
			it to the clipboard
		"""
		buffer = self.editor_nb.get_nth_page(self.editor_nb.get_current_page()).get_buffer()
		view   = self.editor_nb.get_nth_page(self.editor_nb.get_current_page()).get_view()
		buffer.cut_clipboard(self.cb, view.get_editable())

	def edit_copy(self, widget):
		"""
			Menu Callback for copying the selected text to the clipboard
		"""
		buffer = self.editor_nb.get_nth_page(self.editor_nb.get_current_page()).get_buffer()
		buffer.copy_clipboard(self.cb)

	def edit_paste(self, widget):
		"""
			Menu Callback for pasteing the text from the clipboard
			to the current active editor tab
		"""
		buffer = self.editor_nb.get_nth_page(self.editor_nb.get_current_page()).get_buffer()
		view   = self.editor_nb.get_nth_page(self.editor_nb.get_current_page()).get_view()
		buffer.paste_clipboard(self.cb, None, view.get_editable())

	def edit_delete(self,widget):
		""" Menu Callback for deleting the selected text in the
			current active editor tab
		"""
		buffer = self.editor_nb.get_nth_page(self.editor_nb.get_current_page()).get_buffer()
		view   = self.editor_nb.get_nth_page(self.editor_nb.get_current_page()).get_view()
		buffer.delete_selection(True, view.get_editable())

	def show_package_manager(self, widget):
		""" shows the package manager """
		dialog = pkgmanager.PkgManager()

	def edit_preferences(self, widget):
		""" shows the Preferences window """
		parent = self.editor_nb
		rconvt = self.rpyconsole
		PrefDlg = preferences.PreferencesWindow(widget, parent, rconvt)

	def show_aboutdlg(self,widget):
		""" shows the About dialog """
		AboutDlg = about.AboutDlg(widget)

	def execute(self, widget):
		""" 
		Evaluate active script content into rpyconsole
		"""
		buffer = self.editor_nb.get_nth_page(self.editor_nb.get_current_page()).get_buffer()
		text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter()) + "\n"

		# Clean up the text from the buffer
		# - send only code, no empty lines or comments
		pattern = re.compile(r"(^\#.*$\n)|(^$\n)", re.MULTILINE)
		text = pattern.sub('', text)
		if text:
			self.rpyconsole.eval(text, store_history=False)
			self.sb.push_textfield(_("Execution finished"))
	
	def find_cb(self, widget):
		""" Callback for showing the searchbar """
		# check if a bar is visible
		if self.replace_bar.is_visible():
			self.replace_bar.close()
			self.search_bar.show()
		elif self.search_bar.is_visible():
			self.search_bar.close()
		else:
			self.search_bar.show()
	
	def replace_cb(self, widget):
		""" Callback for showing the replacebar """
		# check if a bar visible
		if self.search_bar.is_visible():
			self.search_bar.close()
			self.replace_bar.show()
		elif self.replace_bar.is_visible():
			self.replace_bar.close()
		else:
			self.replace_bar.show()

	def get_current_script(self):
		""" returns currently active tab's filename """
		index = self.editor_nb.get_current_page()
		try:
			script = self.scripts[index]
		except:
			script = None

		return script

	def get_current_help(self):
		""" returns currently active help item """
		index = self.helpbrowser_nb.get_current_page()
		try:
			help = self.helps[index]
		except:
			helps = None

		return help

	def find_replace_cb(self, widget):
		find_replace_dlg = findreplace.FindReplaceDlg()

	def get_tab_name(self, index):
		""" returns the notebook tab name based on given index """
		cur_tab = self.editor_nb.get_nth_page(index)
		return self.editor_nb.get_tab_label_text(cur_tab)

	def get_current_file_wks(self):
		""" returns current workspace filename """
		return self.file_wks

	def set_current_file_wks(self, filename):
		""" set current workspace filename """
		self.file_wks = filename

	def hb_home(self, widget):
		""" Help Browser Home Button Callback """
		self.hb_engine.load_url("file:///usr/share/doc/r-recommended/doc/html/index.html")

	def hb_back(self, widget):
		""" Help Browser Back Button Callback """
		self.hb_engine.go_back()

	def hb_forward(self, widget):
		""" Help Browser forward Button Callback """
		self.hb_engine.go_forward()

	def update_cursor_position(self, iter, mark, view):
		""" update the cursor position in the statusbar """
		tab = self.editor_nb.get_nth_page(self.editor_nb.get_current_page())
		line, row = tab.get_cursor_position()
		self.sb.push_cursor(line, row)

	def buffer_changed_cb(self, buffer):
		""" Callback for current editor buffer, if changed """
		script = self.get_current_script()
		script.set_changed(True)
		tab = self.editor_nb.get_nth_page(self.editor_nb.get_current_page())
		line, row = tab.get_cursor_position()
		self.sb.push_cursor(line, row)

	def helpbrowser_nb_switch(self, notebook, page, page_num):
		""" Callback for the editor notebook if switched """		
		tab = self.helpbrowser_nb.get_nth_page(page_num)
		help = self.helps[page_num]
		help.set_active()

		#line, row = tab.get_cursor_position()
		#self.sb.push_cursor(line, row)

		# since selected tab is not yet active manually pass to function
		# seld.update_window_title the correct name to show
		self.update_window_title(self.helps[page_num].get_short_name())

	def help_back(self, widget):
		""" 
		Go backward in help history
		"""		
		help = self.get_current_help()

		if help:
			help.go_backward()

		self.update_window_title()

	def help_forward(self, widget):
		""" 
		Go forward in help history
		"""		
		help = self.get_current_help()

		if help:
			help.go_forward()

		self.update_window_title()

	def nb_select_cb(self, notebook, move_focus):
		""" Callback for the editor notebook if selected """
		#tab = self.editor_nb.get_nth_page(self.editor_nb.get_current_page())
		#line, row = tab.get_cursor_position()
		#self.sb.push_cursor(line, row)
		print "selected"

	def nb_switch_cb(self, notebook, page, page_num):
		""" Callback for the editor notebook if switched """		
		tab = self.editor_nb.get_nth_page(page_num)
		line, row = tab.get_cursor_position()
		self.sb.push_cursor(line, row)

		# since selected tab is not yet active manually pass to function
		# seld.update_window_title the correct script name to show
		self.update_window_title(self.scripts[page_num].get_short_name())

	def main_nb_switch_cb(self, notebook, page, page_num):
		""" Callback for the main notebook, if switched """
		if page_num == 0:
			self.sb.cursor.set_sensitive(False)
			self.tb_console.show()
			self.tb_editor.hide()
			self.tb_help.hide()
		elif page_num == 1:
			self.sb.cursor.set_sensitive(True)
			self.tb_console.hide()
			self.tb_editor.show()
			self.tb_help.hide()
		else:
			self.sb.cursor.set_sensitive(False)
			self.tb_console.hide()
			self.tb_editor.hide()
			self.tb_help.show()

	def set_mode_console(self, widget):
		self.main_nb.set_current_page(0)
		self.live_text.set_text("")
		self.rpyconsole_input.grab_focus()
		self.update_window_title()

	def set_mode_editor(self, widget):
		self.main_nb.set_current_page(1)
		self.live_text.set_text("")
		self.update_window_title()

	def set_mode_help(self, widget):
		self.main_nb.set_current_page(2)
		self.live_text.set_text("")
		self.live_text.grab_focus()
		self.update_window_title()

	def get_script_filenames(self):
		"""Returns all filenames of available scripts"""
		filenames = []
		
		for script in self.scripts:
			filenames.append(script.get_filename())
		
		return filenames

	def get_script_short_names(self):
		"""Returns all short names of available scripts"""
		shortnames = []
		
		for script in self.scripts:
			shortnames.append(script.get_short_name())
		
		return shortnames

	def get_script_close_buttons(self):
		"""Returns all close buttons belonging to available scripts"""
		buttons = []
		
		for script in self.scripts:
			buttons.append(script.get_tab_close_button())
		
		return buttons
	def goto_line_cb(self):
		""" Goto a specific line in the current editor tab """

	def update_window_title(self, custom_name=None):
		"""
		Update the window title according to current mode

		@param custom_name - string - Custom name to show instead of default
		"""
		mode = self.get_current_mode()

		if custom_name:
			self.window.set_title(custom_name + " - RGnome")
		elif mode == self.MODE_HELP:
			help = self.get_current_help()
			self.window.set_title(help.get_short_name() + " - RGnome")
		else:
			script = self.get_current_script()
			if script:
				self.window.set_title(script.get_short_name() + " - RGnome")
			else:
				self.window.set_title("RGnome")

	def console_eval_expression(self, widget):
		self.rpyconsole.eval(self.rpyconsole_input.get_text())
		self.object_browser.refresh(self.live_text.get_text())
		self.rpyconsole_input.set_text("")
		self.rpyconsole_input.grab_focus()

	def console_clear_output(self, widget):
		self.rpyconsole.clear(robjects=False)

	def console_key_pressed(self, widget, event):
		"""
		Checks keyboard input and navigate console history if arrows are pressed

		@param widget - gtk.Widget - Widget sending the signal
		@param event - gdk.Event - key-press-event

		@return - boolean - False if the signal must be propagated downstream
		"""
		if event.keyval == gtk.keysyms.Up:
			# Up arrow unfolds history items back in time
			value = self.rpyconsole.history_back()
			if value:
				self.rpyconsole_input.set_text(value)
			return True
		elif event.keyval == gtk.keysyms.Down:
			# Down arrow unfolds history items back in time
			value = self.rpyconsole.history_forward()
			if value:
				self.rpyconsole_input.set_text(value)
			return True
		else:
			# No keyval was caught, propagate the event
			return False

	def get_current_mode(self):
		"""
		@return - integer - Current rgnome working mode
		"""

		index = self.main_nb.get_current_page()
		if index == 0 :
			return self.MODE_CONSOLE
		elif index == 1:
			return self.MODE_EDITOR
		else:
			return self.MODE_HELP

	def get_current_buffer(self):
		"""
		@return - SourceBuffer - Text buffer for current rgnome working mode
		"""

		textbuf = None
		mode = self.get_current_mode()

		if mode == self.MODE_CONSOLE:
			textbuf = self.rpyconsole.get_buffer()
		elif mode == self.MODE_EDITOR:
			script = self.get_current_script()
			if script: textbuf = script.get_buffer()
		elif mode == self.MODE_HELP:
			help = self.get_current_help()			
			if help: textbuf = help.get_buffer()

		return textbuf

	def console_history_back(self,widget):
		"""
		Display the command called by the user before the current one, if any
		"""
		text = self.rpyconsole.history_back()
		if text:
			self.rpyconsole_input.set_text(text)

	def console_history_forward(self, widget):
		"""
		Display the command called by the user after the current one, if any
		"""
		text = self.rpyconsole.history_forward()
		if text:
			self.rpyconsole_input.set_text(text)

	def destroy(self, widget, data=None):
		"""
		Called when is application is about to shutdown.
		Check if there are any changed scriptes that are unsaved,
		and ask the user to save these changes.
		"""
		unsaved_changes = False
		for script in self.scripts:
			if script.is_changed():
				unsaved_changes = True
				dialog = gtk.MessageDialog(type=gtk.MESSAGE_WARNING,\
						message_format=(_("Save the changes to script \"") +
										script.get_short_name() +
										_("\" before closing?")))
				dialog.wrap = True
				dialog.set_icon(self.icon)
				dialog.add_button(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL)
				dialog.add_button(gtk.STOCK_YES,gtk.RESPONSE_YES)
				dialog.add_button(gtk.STOCK_NO,gtk.RESPONSE_NO)
				result = dialog.run()
				dialog.destroy()				
				if result == gtk.RESPONSE_YES:
					page = self.editor_nb.get_nth_page(
						self.editor_nb.get_current_page())
					script.save(page.get_buffer(), script.get_filename())
				elif result == gtk.RESPONSE_NO:
					pass
				elif result == gtk.RESPONSE_CANCEL:
					return True

		if unsaved_changes:
			if result == gtk.RESPONSE_CANCEL:
				return True
			else:
				gtk.main_quit()
		else:
			gtk.main_quit()
