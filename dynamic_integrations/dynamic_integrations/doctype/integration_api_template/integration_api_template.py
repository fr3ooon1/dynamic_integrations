# Copyright (c) 2022, Dynamic Technology and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class IntegrationApiTemplate(Document):
	def validate (self) :
		add_custom_field(self.document_type,self.integration_id)
		add_custom_field(self.document_type,"sync_source")




def add_custom_field (document_type,fieldname) :
	frappe.clear_cache(doctype=document_type)
	meta = frappe.get_meta(document_type)
	if not meta.get_field(fieldname):
		# create custom field
		frappe.get_doc({
			"doctype":"Custom Field",
			"dt": document_type,
			"__islocal": 1,
			"fieldname": fieldname,
			"label": fieldname.replace("_", " ").title(),
			"read_only": 1,
			"allow_on_submit": 1,
			"no_copy": 1,
			"in_filter":1,
			"in_standard_filter":1,
			"fieldtype": "Data",
			"owner": "Administrator"
		}).save()

		frappe.msgprint(_("Created Custom Field {0} in {1}").format(fieldname,
			document_type))

	

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_item_template(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(""" select * from `tabIntegration Api Template`
		where document_type in (
			select distinct options from `tabDocField` 
			where parent =  %(document_type)s and fieldtype in ('Link','Table')
		)  and profile = %(profile)s and is_link = 1 and
		(name like %(txt)s or document_type like %(txt)s)
		
		limit %(start)s, %(page_len)s""", {
			'profile': filters.get("profile"),
			'document_type': filters.get("document_type"),
			'start': start,
			'page_len': page_len,
			'txt': "%%%s%%" % txt
		})
