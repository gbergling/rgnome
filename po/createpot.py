#!/usr/bin/env python

# copied from exaile
import os, sys

if len(sys.argv) <= 1:
    os.system("intltool-extract --type=gettext/glade ../resource/rgnome.glade")
    os.system("xgettext -k_ -kN_ -o messages.pot ../rgnome.py ../librgnome/*.py ../resource/rgnome.glade.h ../plugins/*.py")
    print "Now edit messages.pot, save it as <locale>.po, \n"\
		"and send it to gordon@boltzmann-konstante.de.\nThanks!\n"
