import frappe
import json

@frappe.whitelist()

def courier():
    data = json.loads(frappe.request.data)
    main_data = data.get("data")
    if not main_data :
            frappe.local.response['message'] = "No Data Found" 
            frappe.local.response['http_status_code'] = 400
            return
    #required fields 
    #label code
    if not main_data.get("label") or not main_data.get("code") :
        frappe.local.response['message'] = "Please Add code and label For courier Objects " 
        frappe.local.response['http_status_code'] = 400
    #get old to update 
    old_courier =  frappe.db.sql(""" SELECT name From `tabCourier`  WHERE code = '{}'
        """.format(main_data.get("code")) ,as_dict = 1)
    if old_courier and len(old_courier) > 0 :
        frappe.db.sql(""" UPDATE  `tabCourier` set label = '{}' WHERE code='{}'
         """.format(main_data.get("label"), main_data.get("code")  ))
        frappe.db.commit()
        frappe.local.response['message'] = "Courier %s Updated"%(main_data.get("code")) 
        frappe.local.response['http_status_code'] = 200
        return 
    cour = frappe.new_doc("Courier")
    cour.code = main_data.get("code")
    cour.label = main_data.get("label")
    cour.save()
    frappe.local.response['message'] = "Courier %s created"%(main_data.get("code")) 
    frappe.local.response['erp_id'] = cour.name
    frappe.local.response['http_status_code'] = 200