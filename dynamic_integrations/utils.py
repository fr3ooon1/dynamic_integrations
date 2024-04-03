import frappe
from frappe import _
import requests



@frappe.whitelist()
def save_doc (doc_props):
	doc = frappe.get_doc(doc_props)
	try:		
		doc.save()
	except frappe.DuplicateEntryError as e :
			exist_doc = frappe.get_doc(doc.doctype , doc.name)
			exist_doc.update(doc_props)
			exist_doc.save()
			return exist_doc

	except Exception as e :
		create_error(e)
	return doc


@frappe.whitelist()
def fetch_request_json(request_data):
    response_json = {}
    try:
        response_json = request_data.json() or {}
    except Exception as e:
        create_error(e)
    return response_json


@frappe.whitelist()
def create_error(e):
    error = frappe.new_doc('Error Log')
    error.error = str(e)
    error.save()
    return True