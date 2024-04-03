from email import parser
import frappe
from frappe.model.document import Document
import json
from dateutil import parser
@frappe.whitelist()
def create_customer_with_address (data):
    try:
        # print (type(data))
        # data = json.loads(str(data))
        # print (data)
        customer_data = data.get("customer")
        address_data = data.get("address")
        if not customer_data : 
            frappe.local.response["message"] = "Customer Data is Required"
            frappe.local.response['http_status_code'] = 400
        

        customer_data["doctype"] = "Customer"
        customer = frappe.get_doc(customer_data)
        if address_data :
            address_data ["doctype"] = "Address"
            address = frappe.get_doc(address_data)
            print('address.__dict__')
            print(address.__dict__)
            print('address_data')
            print(address_data)
            address.save()
        customer.customer_primary_address = address.name
        customer.save()
        frappe.local.response["message"] = "Created Successfully"
        frappe.local.response["customer"] = frappe.get_doc("Customer",customer.name)
        frappe.local.response["address"] = frappe.get_doc("Address",address.name)
        frappe.local.response['http_status_code'] = 200

    except Exception as e :
        frappe.local.response["message"] = str(e)
        frappe.local.response['http_status_code'] = 400


    



@frappe.whitelist()
def get_full_doctype_with_date_condition():
    obj = json.loads(frappe.request.data)
    if obj.get("doctype") :
        doctype = str(obj.get("doctype"))
        field = obj.get("field")
        value = obj.get("value")
        try :
            conditions = ""
            if field and value:
                value = parser.parse(str(value))
                conditions = f" and `{field}` >= '{value}' "
            data = frappe.db.sql_list("""
            select name from `tab%(doctype)s` where 1 = 1 %(conditions)s 
            """%{'doctype':doctype,'conditions':conditions})
            result = []
            for docname in data :
                doc = frappe.get_doc(doctype,docname)
                result.append(doc)
            return result
        except Exception as e :
            frappe.local.response["message"] = f"doctype not found {e}"
            frappe.local.response['http_status_code'] = 406
    else :
        frappe.local.response["message"] = "Invalid Params "
        frappe.local.response['http_status_code'] = 404

