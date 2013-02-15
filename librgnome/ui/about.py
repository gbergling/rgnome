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

GPL_Header = '''This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
'''
class AboutDlg:
	"""
		implements an AboutDialog
	"""
	def __init__(self, widget):
		"""
			initiat the AboutDialog and sets the respective
			values
		"""

		self.config = config.config()
		self.comment = _("A featureful GNU R frontend.")

		self.AboutDlg = gtk.AboutDialog()
		self.AboutDlg.connect("response", self.close)
		self.AboutDlg.set_name("RGnome")
		self.AboutDlg.set_comments(self.comment)
		self.AboutDlg.set_version(self.config.get_version())
		self.AboutDlg.set_authors(["Gordon Bergling", "Luca Della Santina"])
		self.AboutDlg.set_translator_credits("Gordon Bergling")
		self.AboutDlg.set_website("http://rgnome.boltzmann-konstante.de/")
		self.AboutDlg.set_copyright("Copyright (C) 2007 Gordon Bergling, Luca Della Santina")
		self.AboutDlg.set_license(GPL_Header)

		img = os.path.abspath(os.getcwd()) + "%sresource%srgnome.png" % (os.sep, os.sep)
		icon = gtk.gdk.pixbuf_new_from_file(img)
		self.AboutDlg.set_icon_from_file(img)
		self.AboutDlg.set_icon(icon)
		self.AboutDlg.set_logo(icon)
		self.AboutDlg.show()

	def close(self, widget, *args):
		"""
			closed the AboutDialog
		"""
		self.AboutDlg.hide()
