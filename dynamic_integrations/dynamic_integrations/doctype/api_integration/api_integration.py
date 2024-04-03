# Copyright (c) 2022, Dynamic Technology and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import base64
import hashlib
import hmac
import json
from codecs import ignore_errors
from datetime import date, datetime, time, timedelta

import frappe
import requests
from dateutil import parser
from dynamic_integrations.utils import (create_error, fetch_request_json,
                                        save_doc)
from frappe import _, log, throw
from frappe.model.document import Document
# from time import sleep
from frappe.model.naming import set_new_name
# from venv import create
from frappe.utils.data import get_link_to_form, now_datetime
from six.moves.urllib.parse import urlparse

# from numpy import append


# from frappe.utils.jinja import validate_template
# from frappe.utils.safe_exec import get_safe_globals


LOG_DOCTYPE = "Profile Doctype Integration"


class ApiIntegration(Document):
	def validate(self):
		self.validate_request_url()
		self.validate_login_url()

	def validate_request_url(self):

		if not self.end_point:
			lnk = get_link_to_form("Api Integration Profile",self.profile)
			frappe.throw(_("Please Set End Point in Api Integration Profile {}").format(lnk))
		
		try:
			request_url = urlparse(self.end_point+self.request_url).netloc
			if not request_url:
				raise frappe.ValidationError
		except Exception as e:
			frappe.throw(_("Check Request URL"), exc=e)

	def validate_login_url(self):
		try:
			if not (self.enable_security and self.auth_type == "Bearer"):
				return
			request_url = urlparse(self.end_point + self.login_request_url).netloc
			if not request_url:
				raise frappe.ValidationError
		except Exception as e:
			frappe.throw(_("Check Login Request URL"), exc=e)

	@frappe.whitelist()
	def execute(self):
		self.integration_id = frappe.db.get_value(
			"Api Integration Profile", self.profile, "fieldname")
		if self.request_method == "GET":
			self.execute_get_method()
		else:
			self.execute_post_method()
		self.set_next_excecution_date()

	def set_next_excecution_date(self):
		self.last_execution_date = datetime.now()
		self.next_execution_date = self.last_execution_date + \
			timedelta(minutes=(self.period or 0))
		self.save()

	def execute_get_method(self):
		self.validate()
		auth_token = ""
		if self.enable_security:
			if self.auth_type == "Bearer":
				auth_token = self.get_auth_token()

		request_headers = self.get_request_headers(auth_token)
		parameters = self.get_request_parameters()
		request_data = requests.request(self.request_method, self.end_point + self.request_url, params=parameters, headers=request_headers,
										data=self.json_request_body)

		response_json = fetch_request_json(request_data)
		self.create_log(request_headers, self.json_request_body, request_data)
		self.serialize_json_response(response_json)

	def execute_post_method(self):
		self.validate()
		auth_token = ""
		if self.enable_security:
			if self.auth_type == "Bearer":
				auth_token = self.get_auth_token()
		request_headers = self.get_request_headers(auth_token)
		documents = self.get_unsynced_documents() or []
		for docname in documents:
			doc = frappe.get_doc(self.webhook_doctype, docname)
			json_request_body = self.serialize_json_request(doc)
			request_data = requests.request(self.request_method, self.end_point + self.request_url, headers=request_headers,
											data=json.dumps(json_request_body))

			response_json = fetch_request_json(request_data)
			self.create_log(request_headers,
							json_request_body, request_data)
			if self.response_template :
				if request_data.ok:
					
					if isinstance(response_json, dict):
						self.serialize_json_response(response_json, doc)
					elif not isinstance(response_json, list):
						setattr(doc, self.integration_id, str(response_json))
						doc.save()
						self.update_doc_lastdate(doc.modified)

	def get_unsynced_documents(self):
		# conditions = "" if (self.conditions or "").strip(
		# ) == "" else f" and {self.conditions}"
		if self.integration_type == "Create":
			sql = f"""
				select name from `tab{self.webhook_doctype}`  where ifnull(`{self.integration_id}`,0) = 0
			"""
			return frappe.db.sql_list(sql) or []
			# frappe.throw(sql)
		else:
			doc_log = frappe.db.get_value(LOG_DOCTYPE,
											{"document_type": self.webhook_doctype,
											"profile": self.profile},
											["last_creation", "last_modified"],
											as_dict=1
											) or frappe._dict({})
			last_modified = getattr(
				doc_log, 'last_modified') or str(datetime.min)
			sql = f"""
				select name from `tab{self.webhook_doctype}`  where
				 modified >  '{last_modified}' or ifnull(`{self.integration_id}`,'0') = '0'
				
			"""
			# frappe.msgprint(str(sql))
			return frappe.db.sql_list(sql) or []
			
		return frappe.db.sql_list(sql) or []

	def create_log(self, headers, data, response):
		doc = frappe.new_doc("Api Integration Log")
		doc.api = self.name
		doc.posting_date = now_datetime()
		doc.user = frappe.session.user
		doc.headers = str(headers)
		doc.data = str(data)
		doc.url = response.url
		doc.response = str(fetch_request_json(response))
		doc.status_code = response.status_code
		doc.ok = response.ok
		doc.save()

	def get_request_parameters(self):
		doc_log = frappe.db.get_value(LOG_DOCTYPE,
										{"document_type": self.webhook_doctype,
										"profile": self.profile},
										["last_creation", "last_modified"],
										as_dict=1
										) or frappe._dict({})
		params = {}
		for row in getattr(self, 'parameters', []):

			if row.value in ["last_creation", "last_modified"]:
				params[row.param_name] = getattr(
					doc_log, row.value, '') or str(datetime.min)
			else:
				params[row.param_name] = row.value or ''
		return params

	def get_request_headers(self, auth_token=""):
		headers = {}
		for row in self.webhook_headers:
			headers[row.key] = row.value
		if auth_token != "" and auth_token:
			headers["Authorization"] = f"Bearer {auth_token}"
		return headers

	def get_auth_token(self):
		headers = {"Content-Type": "application/json"}
		# if (self.login_request_type == 'POST'):
		req_login = requests.request(self.login_request_type, self.end_point + self.login_request_url, headers=headers,
										data=self.login_request_body)

		response_json = fetch_request_json(req_login)
		# self.create_log(headers,self.login_request_body,req_login)
		if req_login.ok:
			token = str(response_json) if not self.token_fieldname or isinstance(
				response_json, str) else response_json.get(self.token_fieldname)

			if not token:
				frappe.throw("Invalid Token Fieldname")
			return token
		else:
			frappe.throw(_(str(response_json)))

	def serialize_json_response(self, json_data, update_doc=None):
		# Prepare Retrieved Data
		documents_data = []

		template_name = self.integration_api_template
		if update_doc:
			template_name = self.response_template

		template = frappe.get_doc(
			"Integration Api Template", template_name)
		# case response one item as dict or dict has list of item
		if isinstance(json_data, dict):
			if template.main_property and template.main_property.strip() != "":
				documents_data = json_data.get(template.main_property) or []
			else:
				documents_data = [json_data]
		# default Case to get List Of Item
		elif isinstance(json_data, list):
			documents_data = json_data

		# fetch every row as document with mapper field
		for json_row in documents_data:
			doc_error = ""
			log_doc = frappe.new_doc("Profile Integration Log")
			log_doc.posting_date = now_datetime()
			log_doc.user = frappe.session.user
			log_doc.profile = self.profile
			log_doc.api = self.name
			log_doc.url = self.end_point + self.request_url
			log_doc.document_type = self.webhook_doctype
			log_doc.data = str(json_row)

			try:
				doc_props = {}
				if isinstance(json_row, dict):
					# fetch Main Props
					doc_props = fetch_normal_properties_response(
						doc_props, template, json_row)
					doc_props = fetch_list_properties_response(
						doc_props, template, json_row)

				doc_props["sync_source"] = self.profile
				doc_props["doctype"] = self.webhook_doctype
				# print ("doc_props => " , doc_props)
				if not update_doc:
					doc = save_doc(doc_props)
					self.update_doc_lastdate(doc.modified)
					# doc = frappe.get_doc({"doctype":self.webhook_doctype})
					# print("doc.name => ", doc)
				else:
					update_doc.update(doc_props)
					update_doc.save()
					self.update_doc_lastdate(update_doc.modified)
					doc = update_doc
					# for key,value in self.json_row.items() :
					# doc = fetch_normal_properties_response(
					# 	doc, template, json_row)
					# # fetch Child Tables Props
					# doc = fetch_list_properties_response(
					# 	doc, template, json_row)

					# doc.__setattr__("sync_source", self.profile)

					# doc = save_doc(doc_props)

				log_doc.ok = 1
				log_doc.document_name = doc.name

			except Exception as e:
				create_error(e)
				log_doc.ok = 0
				log_doc.exception = str(e)
			log_doc.save()

	def update_doc_lastdate(self, last_date):
		doc_log_name = f'{self.profile}-{self.webhook_doctype}'
		if frappe.db.exists(LOG_DOCTYPE, doc_log_name):
			doc_log = frappe.get_doc(
				LOG_DOCTYPE, f'{self.profile}-{self.webhook_doctype}')
		else:
			doc_log = frappe.new_doc(LOG_DOCTYPE)
			doc_log.profile = self.profile
			doc_log.document_type = self.webhook_doctype

		if self.integration_type == "Create":
			doc_log.last_creation = last_date

		if self.integration_type == "Update":
			doc_log.last_modified = last_date

		doc_log.save()

	def serialize_json_request(self, doc):
		# Prepare Request Data
		documents_data = {}
		template = frappe.get_doc(
			"Integration Api Template", self.integration_api_template)
		# case response one item as dict or dict has list of item
		documents_json = fetch_doc_properties_request(doc, template) or {}
		if template.main_property_type == 'Dict':

			documents_data = documents_json if not template.main_property else {
				template.main_property: documents_json}

		return documents_data

# Fetch Response Json To Document


def fetch_normal_properties_response(doc, template, json_row, as_dict=0):
	# print("heeeeeeeeeeeeeereeeeeeeeeeeeee")
	normal_props = [
		x for x in template.attributes_mapping if x.fieldtype == "Normal"]
	for prop in normal_props:
		# if json_row.get(prop.mapping_name) :
		row_value = prop.default_value if check_value_None(json_row.get(prop.mapping_name)) \
			else json_row.get(prop.mapping_name)

		# print(" row_value => ", row_value)
		row_value = get_value_of_mapping_field(row_value, prop.mapping_type)
		# if prop.mapping_name and not prop.mapping_name in json_row.keys():
		# 	row_value = prop.mapping_name
		if as_dict:
			setattr(doc, prop.fieldname, row_value or "")
		else:
			doc[prop.fieldname] = row_value

	link_props = [
		x for x in template.attributes_mapping if x.fieldtype == "Link"]
	for prop in link_props:
		# if json_row.get(prop.mapping_name) :
		if prop.template:
			row_template = frappe.get_cached_doc(
				"Integration Api Template", prop.template)
			integration_id = json_row.get(prop.mapping_name)
			docname = frappe.db.get_value(row_template.document_type, {
				row_template.integration_id: integration_id}, "name")
			
			if check_value_None(docname) :
				docname = prop.default_value if not check_value_None(prop.default_value) else "" 

			
			if docname:
				if as_dict:
					setattr(doc, prop.fieldname, docname or "")
				else:
					doc[prop.fieldname] = docname or ""
	if not as_dict:
		# valid = all([v and str(v).strip() != "" for k, v in doc.items()])
		if not valid_dict(doc):
			return
	return doc


def valid_dict(data):
    valid = any([not check_value_None(v) for k, v in data.items()])
    return valid


def fetch_list_properties_response(doc, template, json_row):
    table_props = [
        x for x in template.attributes_mapping if x.fieldtype == "List"]

    for prop in table_props:
        if prop.template:
            row_template = frappe.get_doc(
                "Integration Api Template", prop.template)
            if json_row.get(prop.mapping_name) and isinstance(json_row.get(prop.mapping_name), list):
                for json_item in json_row.get(prop.mapping_name):
                    row = fetch_normal_properties_response(
                        {}, row_template, json_item, as_dict=0)
                    if row:
                        doc.append(prop.fieldname, row)

    return doc


# Fetch Document for Json Request


def fetch_normal_properties_request(doc, template, json_row={}):
	normal_props = [
		x for x in template.attributes_mapping if x.fieldtype == "Normal"]
	normal_json = {}
	for prop in normal_props:
		# if json_row.get(prop.mapping_name) :
		fieldvalue = "" if not hasattr(
			doc, prop.fieldname) else getattr(doc, prop.fieldname, "")

		if check_value_None(fieldvalue):
			fieldvalue = prop.default_value
		# print("fieldvalue 11 => ", fieldvalue)
		# print("fieldvalue 11 => ", prop.default_value)
		fieldvalue = get_value_of_mapping_field(
			fieldvalue, prop.mapping_type, post=1)
		if not check_value_None(fieldvalue):
			normal_json[prop.mapping_name] = fieldvalue
		# print("fieldvalue 22222 => ", fieldvalue)
	link_props = [
		x for x in template.attributes_mapping if x.fieldtype == "Link"]
	for prop in link_props:
		# if json_row.get(prop.mapping_name) :
		if prop.template and hasattr(doc, prop.fieldname):
			row_template = frappe.get_cached_doc(
				"Integration Api Template", prop.template)
			integration_id = prop.fetch_field or  row_template.integration_id
			docname = frappe.db.get_value(row_template.document_type, getattr(
				doc, prop.fieldname, ''), integration_id)
			
			if not check_value_None(docname):
				fieldvalue = docname
			else :
				fieldvalue = prop.default_value if not check_value_None(prop.default_value) else "" 


			normal_json[prop.mapping_name]  = get_value_of_mapping_field(fieldvalue, prop.mapping_type, post=1)
	# valid = all([v and str(v).strip() != "" for k, v in normal_json.items()])
	if valid_dict(normal_json):
		json_row.update(normal_json)
	return json_row


def fetch_list_properties_request(doc, template, json_row={}):
    table_props = [
        x for x in template.attributes_mapping if x.fieldtype == "List"]

    for prop in table_props:
        if prop.template:
            row_template = frappe.get_doc(
                "Integration Api Template", prop.template)
            json_list = []
            for item in getattr(doc, prop.fieldname, []):
                row_json = {}
                row_json = fetch_doc_properties_request(item, row_template)
                if row_json:
                    json_list.append(row_json)
            json_row[prop.mapping_name] = json_list
    return json_row


def fetch_dict_properties_request(doc, template, json_row={}):
    table_props = [
        x for x in template.attributes_mapping if x.fieldtype == "Dict"]

    for prop in table_props:
        if prop.template:
            row_template = frappe.get_doc(
                "Integration Api Template", prop.template)
            if hasattr(doc, prop.fieldname):
                row_doc = frappe.get_doc(
                    prop.document_type, getattr(doc, prop.fieldname))
                dict_json = fetch_doc_properties_request(row_doc, row_template)
                if dict_json:
                    json_row[prop.mapping_name] = dict_json

    return json_row


def fetch_doc_properties_request(doc, template):
    doc_json = {}
    normal_json = fetch_normal_properties_request(doc, template, {}) or {}
    doc_json.update(normal_json)
    list_json = fetch_list_properties_request(doc, template, {}) or {}
    doc_json.update(list_json)
    dict_json = fetch_dict_properties_request(doc, template, {}) or {}
    doc_json.update(dict_json)
    # valid = all([v and str(v).strip() != "" for k, v in normal_json.items()])
    if not valid_dict(normal_json):
        return
    return doc_json


def get_unsynced_documents(doctype):
    sql = f"""
		select name from `tab{doctype}`  where name not in 
		(select DISTINCT document_name  from `tabProfile Integration Log` profile
		where document_type = '{doctype}' 
		and IFNULL(document_name,'') <> '')
	"""
    return frappe.db.sql_list(sql) or []


def check_value_None(value):
	# print (value , " => " , (value == None or str(value).strip() in ["", "None"]))
	return value == None or str(value).strip() in ["", "None" , 'None']


def get_value_of_mapping_field(value, mapping_type, post=0):
    try:
        if mapping_type == "Data":
            value = str(value)

        if mapping_type == "Int":
            value = int(value)

        if mapping_type == "Float":
            value = float(value)

        if mapping_type == "Date":
            value = parser.parse(str(value)).date()
            value = value if not post else str(value)

        if mapping_type == "Datetime":
            value = parser.parse(str(value))
            value = value if not post else str(value)

    except Exception as e:
        create_error(e)
    return value

# def get_unsynced__created_documents(doctype):
#     sql = f"""
# 		select name from `tab{doctype}`  where name not in
# 		(select DISTINCT document_name  from `tabProfile Integration Log` profile
# 		where document_type = '{doctype}'
# 		and IFNULL(document_name,'') <> '')
# 	"""
#     return frappe.db.sql_list(sql) or []
