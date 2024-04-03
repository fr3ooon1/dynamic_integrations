# Copyright (c) 2022, Dynamic Technology and contributors
# For license information, please see license.txt

from curses import meta
from os import replace
import frappe
from frappe.model.document import Document
import json

import re 
class DataTemplate(Document):
	def validate(self):

		if self.document :

				meta = frappe.get_meta("{}".format(self.document))
				convert_str_to_object(self.template  ,meta )







def convert_str_to_object(st  ,doc):
	data  =  False
	#valiadate syntaces As json 
	new_st = st.replace("'" , '"')
	# frappe.throw(new_st)
	
	try :
		data = json.loads(new_st)
		
	except :
		frappe.throw(""" Please check the json syntaces !""")
	#check valide meta data 
	if data :
		for k,v in data.items():
			# frappe.throw(str(type(v)))
			if isinstance(v ,str) :
				
				field = v.find("doc")
				# frappe.msgprint(str(field))
				if int(field ) !=  -1  :
					filed_name = str(v[(int(field ) + 4)::])
					
					if doc.has_field(f'{filed_name}')  or filed_name =="name":
						
						frappe.msgprint("ok")
					else :
						frappe.msgprint("no")
				else :
					frappe.msgprint("static")
			if isinstance(v ,dict) :
				for k_1,v_1 in v.items():
					if isinstance(v_1 ,str) :
						
						field = v_1.find("doc")
					
						if int(field ) !=  -1  :
							filed_name = str(v_1[(int(field ) + 4)::])
							re.sub(' ','',filed_name)
							if doc.has_field(f'{filed_name}') or filed_name =="name":
								
								frappe.msgprint("ok")
							else :
								frappe.msgprint("no")




			