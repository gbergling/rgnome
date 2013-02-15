#!/usr/bin/env python
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

import os, sys
import locale, gettext
from gettext import gettext as _

import pygtk
pygtk.require('2.0')
import gtk, gtk.glade

## Find out the location of rgnome's working directory, and go there
basedir = os.path.dirname(os.path.realpath(__file__))
if not os.path.exists(os.path.join(basedir, "rgnome.py")):
    if os.path.exists(os.path.join(os.getcwd(), "rgnome.py")):
        basedir = os.getcwd()
sys.path.insert(0, basedir)
os.chdir(basedir)
os.path.join(basedir)

from librgnome.ui import mainwindow
from librgnome import cli

try:
	locale.setlocale(locale.LC_ALL, '')
except locale.Error:
	print "Setting locale failed!"

from gettext import gettext as _
gettext.bindtextdomain('rgnome', '/usr/local/share/locale')
gettext.textdomain('rgnome')
gtk.glade.bindtextdomain('rgnome', '/usr/local/share/locale')
gtk.glade.textdomain('rgnome')

if __name__ == '__main__':
	cliobj = cli.cli()
	args = cliobj.parse_args(sys.argv[1:])
	rg = mainwindow.MainWindow()
	if len(args) > 0:
		for i in range(len(args)):
			rg.file_open(filename = args[i])
	# finally launch the gtk loop
	gtk.main()
