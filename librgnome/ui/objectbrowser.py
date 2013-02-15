# -*- coding: utf-8 -*- 
# 
# Copyright (C) 2007 Luca Della Santina
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
# - Check on huge R workspaces if current filtering method is slow (and in case 
#	switch to a gtk.TreeSelection based filtering method, supposed to be faster)
# - Preserve previous folding status of parent nodes when refreshing the browser
# - Make functions tooltip properly disting between optional and required params

import string
import pygtk
pygtk.require("2.0")

import gtk, gtk.gdk
from rpy import *

from librgnome import config
from librgnome.ui import objecttips

R_CATEGORY_OTHER = -1
R_OTHER_TYPES = ["NULL", "symbol", "pairlist", "pairlist", "environment",
				"promise", "language", "...", "any", "expression", "bytecode",
				"externalptr", "S4"]

R_CATEGORY_DATA = 0
R_DATA_TYPES = ["char", "logical", "integer", "double", "complex", "character",
				"raw"] 
R_DATA_CLASS = ["numeric", "character"]

R_CATEGORY_DATA_FRAME = 1
R_DATA_FRAME_CLASS = ["data.frame"]

R_CATEGORY_MODEL = 2
R_MODEL_TYPES = ["list"]
R_MODEL_CLASS = ["lm", "glm", "lme", "nlme"]

R_CATEGORY_FUNCTION = 3
R_FUNCTION_TYPES = ["closure", "special", "builtin"]
R_FUNCTION_CLASS = ["function"]

class ObjectBrowser:
	""" Object browser for R """
	def __init__(self, treeview):
		""" 
		Initialize Object Browser

		@param treeview - gtk.Treeview - Treeview widget used for visualization
		"""
	
		self.view = treeview
		self.model = gtk.TreeStore(gtk.gdk.Pixbuf, str)
		self.objects = {}

		# init tree model
		self.iter_data = self.model.append(None, [None, _("Data")])
		self.iter_model = self.model.append(None, [None, _("Models")])
		self.iter_function = self.model.append(None, [None, _("Functions")])
		self.iter_other = self.model.append(None, [None, _("Other")])

		self.synch_objects()
		self.synch_model()

		# init tree view
		self.view.set_model(self.model)	
		column = gtk.TreeViewColumn(_("R Objects"))

		self.view.append_column(column)
		cell = gtk.CellRendererText()
		column.pack_start(cell, True)
		# Display and sort the name field
		column.add_attribute(cell, 'text', 1)
		column.set_sort_column_id(1)

		# assign the tooltip
		self.tips = ObjectTooltips()
		self.tips.add_view(self.view)

	def set_filter(self, filter_text):
		""" 
		Filter object list showing only the ones that contains text

		@param filter_text - string - Text to be contained in visualized items
		"""
		self.synch_model(filter_text)

	def refresh(self, filter_text=None):
		""" 
		Refresh object browser data, applying optional visualization filter

		@param filter_text - string - Text to be contained in visualized items
		"""
		self.synch_objects()
		self.synch_model(filter_text)

	def synch_objects(self):
		""" Reloads objects from R """
		items = with_mode(BASIC_CONVERSION, lambda: r.ls())()
		objects = {}
		for name in items:
			objects[name] = r(name)
		self.objects = objects

	def synch_model(self, filter_text = None):
		""" 
		Reloads items into tree model, according to optional filter criterium 

		@param filter_text - string - Text to be contained in visualized items
		"""

		self.model.remove(self.iter_data)
		self.iter_data = self.model.append(None, [None, _("Data")])

		self.model.remove(self.iter_model)
		self.iter_model = self.model.append(None, [None, _("Models")])

		self.model.remove(self.iter_function)
		self.iter_function = self.model.append(None, [None, _("Functions")])

		self.model.remove(self.iter_other)
		self.iter_other = self.model.append(None, [None, _("Other")])


		for name in self.objects.keys():
			if filter_text and (name.find(filter_text) < 0):
				continue

			category = robj_get_category(self.objects[name])
			if category == R_CATEGORY_DATA:
				self.model.append(self.iter_data, [None, name])
			elif category == R_CATEGORY_DATA_FRAME:
				self.model.append(self.iter_data, [None, name])
			elif category == R_CATEGORY_MODEL:
				self.model.append(self.iter_model, [None, name])
			elif category == R_CATEGORY_FUNCTION:
				self.model.append(self.iter_function, [None, name])
			elif category == R_CATEGORY_OTHER:
				self.model.append(self.iter_other, [None, name])

		self.view.expand_all()

#-------------------------------------------------------------------------------

class ObjectTooltips(objecttips.TreeViewTooltips):
	def __init__(self):
		# call base class init
		objecttips.TreeViewTooltips.__init__(self)

	def get_tooltip(self, view, column, path):
		"""@return - string - tooltip for the current object (with markup)"""
		it = view.get_model().get_iter(path)
		value = view.get_model().get_value(it,1)

		try:
			robj = r(value)
		except:
			return None

		tip = "<b><big>%s</big></b> <tt>(%s)</tt>\n\n" %(str(value), 
														robj_get_class(robj))

		obj = with_mode(BASIC_CONVERSION, lambda: r(value))()
		category = robj_get_category(robj)

		if category == R_CATEGORY_DATA:
			tip += "  <i>type:</i> <tt>%s</tt> \n" %(robj_get_type(robj))
			tip += "  <i>value:</i> <tt>%s</tt>" %(str(obj))

		if category == R_CATEGORY_DATA_FRAME:
			# list fields as <name>(<class>)
			tip += "  <i>fields:</i>\n"
			for item in obj:
				item_robj = r(value + "$" + item)
				tip += "    <tt>%s <small>(%s)</small></tt>\n" %(item, 
													robj_get_class(item_robj))

		elif category == R_CATEGORY_MODEL:
			# retrieve formula used for generating the model
			formula = with_mode(BASIC_CONVERSION, 
								lambda: r.capture_output(r.formula(value)))()
			tip += "  <i>formula:</i> <tt>%s</tt>\n" %(str(formula))

			# retrieve family and link items if generalized linear models
			if robj_get_class(robj) == "glm":
				family = obj["family"]
				tip += "  <i>family:</i> <tt>%s</tt>\n" %(str(family["family"]))
				tip += "  <i>link:</i> <tt>%s</tt>\n" %(str(family["link"]))

			# retrieve contrasts list
			contrasts = obj["contrasts"]
			tip += "  <i>contrasts:</i>\n"
			for key in contrasts.keys():
				tip += "    <tt>%s %s</tt>\n" %(key,contrasts[key])

			tip += "  <i>residuals df:</i> <tt>%s</tt>\n" %(str(obj["df.residual"]))

		elif category == R_CATEGORY_FUNCTION:
			params = with_mode(BASIC_CONVERSION, lambda: r.formals(robj))()

			tip_req = ""
			tip_opt = ""

			# evaluate parameters one by one
			for key, value in params.iteritems():
				value_str = str(value)
				if key == "...": value_str = "custom params"
				if value_str.find("Robj") >= 0:
					try:
						# optional param with an Robj as default value
						value_type = robj_get_type(value)
						value_type.replace("closure", "function")
						tip_opt += "    <tt>%s = %s</tt>\n" %(key,value_type)
					except:
						# required param raises the exception
						tip_req += "    <tt>%s</tt>\n" %(key)
				else:
					# reconvert python type strings to R equivalent
					value_str = value_str.replace("True", "TRUE")
					value_str = value_str.replace("False", "FALSE")
					value_str = value_str.replace("None", "NULL")
					if value_str == "": value_str = "\"\""
					# optional parameter with default value of primitive type
					tip_opt += "    <tt>%s = %s</tt>\n" %(key, value_str)

			if tip_req <> "": tip += "  <i>required parameters:</i>\n%s" %(tip_req)
			if tip_opt <> "": tip += "\n  <i>optional parameters:</i>\n%s" %(tip_opt)

		return tip

#-------------------------------------------------------------------------------

def robj_get_type(robj):
	""" 
	Inspects the type of and R object

	@param robj - Robj - R object to be inspected
	@return - string - Type of passed R object 
	"""
	return with_mode(BASIC_CONVERSION, lambda: r.typeof(robj))()

def robj_get_class(robj):
	"""
	Inspect the class of an R objects

	@param robj - Robj - R object to be inspected
	@return - string - Class of passed R object
	"""
	robj_class = with_mode(BASIC_CONVERSION, lambda: r.class_(robj))()
	if isinstance(robj_class, list): robj_class = robj_class[0]
	return robj_class

def robj_get_category(robj):
	""" 
	Categorize an object upon its type/class

	@param robj - Robj - R object to be inspected
	@return - constant - Category of passed R object """
	robj_type = robj_get_type(robj)
	robj_class = robj_get_class(robj)

	if robj_class in R_MODEL_CLASS:
		return R_CATEGORY_MODEL
	elif robj_class in R_DATA_FRAME_CLASS:
		return R_CATEGORY_DATA_FRAME
	elif robj_type in R_DATA_TYPES:
		return R_CATEGORY_DATA
	elif robj_type in R_FUNCTION_TYPES:
		return R_CATEGORY_FUNCTION
	else:
		return R_CATEGORY_OTHER

