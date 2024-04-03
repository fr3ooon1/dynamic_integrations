# Copyright (c) 2022, Dynamic Technology and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.model.document import Document
from html2text import re
import requests
class ApiIntegrationProfile(Document):
	def validate(self):
		if self.login_url :
			self.validate_login_data()
		if self.fieldname :
			self.fieldname = self.fieldname.strip().lower().replace(" ","_")
	def validate_login_data(self):
		if not self.login_payload :
			frappe.throw("No Valid Payload for login")
		if not self.request_header :
			frappe.throw("Please set Valide header ")
		#set token 

		# frappe.throw(str(self.login_payload))
		request = requests.post(self.login_url  , data = self.login_payload ,headers={ "Content-Type" :"application/json" } )
		# frappe.throw(str(request.text))
		if request.status_code != 200 :
			frappe.throw(str("Login erro") +str(request.text))
		
		else :
			
			self.token = request.json()
			headers = str(self.request_header).replace("doc.token"  ,self.token)
			self.headers = headers
			frappe.msgprint("<h1>  Login success </h1>")




