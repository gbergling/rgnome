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

import os, sys, getopt, gettext

from librgnome import config

class cli:
	def __init__(self):
		""" initiates the cli class """
		self.c = config.config()
		gettext.install("rgnome")
		_ = gettext.gettext

	def usage(self):
		""" display a usage text on the commandline """

    		license = _('rgnome is free software; you can redistribute it and/or\n\
modify it under the terms of the GNU General Public License as\n\
published by the Free Software Foundation; either version 2 of the\n\
License, or (at your option) any later version.')

		print 'rgnome ' + self.c.get_version()
		print _('A frontend for GNU R')
		print ''
		print (license)
		print ''
		print _('Syntax: ')
		print (' rgnome [options] [filename]...')
		print ''
		print _('Options:')
		print _(' -v | --version: prints the program version and exits')
		print _(' -h | --help: prints this help message and exits')

	def parse_args(self, sysargs):
		""" method parses the commandline arguments """

		try:
			self.opts, self.args = getopt.getopt(sys.argv[1:], ":hv",
					["help", "version"])
		except getopt.GetoptError:
			self.opts = []
			self.args = []
			pass
		for o, a in self.opts:
			if o in ("-h", _("--help")):
				self.usage()
				sys.exit()
			if o in ("-v", "--version"):
				print "rgnome " + self.c.get_version() 
				sys.exit()
		return self.args
