import frappe
import json

@frappe.whitelist()
def customer_obj():
    try :
        data = json.loads(frappe.request.data)
        main_data = data.get("data")
        if not main_data :
            frappe.local.response['message'] = "No Customer Found" 
            frappe.local.response['http_status_code'] = 400
            return

        old_customer = frappe.db.sql(""" SELECT name FROM `tabCustomer` 
        WHERE remote_id  ='{}'   """.format(main_data.get("remote_id") ) ,as_dict =True)
        customer = False
        if old_customer and old_customer[0].get("name") :
            customer = frappe.get_doc("Customer" ,old_customer[0].get("name") )
        if not customer :
            customer = frappe.new_doc("Customer")
        customer.customer_name = main_data.get("customer_name")
        customer.customer_type = "Individual"
        customer.phone = main_data.get("mobile_no")
        customer.e_mail_id = main_data.get("email")
        customer.website = main_data.get("website")
        customer.store = main_data.get("store")
        group_obj = False
        if main_data.get("customer_group") :
            customer_group = frappe.db.sql(""" SELECT name FROM `tabCustomer Group` 
            WHERE group_id ='{}' 
            """.format( main_data.get("customer_group")  ) ,as_dict=True)
            if customer_group  and customer_group[0].get('name'):
                group_obj = frappe.get_doc("Customer Group" , customer_group[0].get('name') )
        if not  group_obj :
            customer.customer_group = "All Customer Groups"  
        else :
            customer.customer_group = group_obj.name
       
        customer.territory = "All Territories"
        customer.remote_id = main_data.get("remote_id")
        customer.save()
        
        # if not customer.mobile_no :
        if customer.customer_primary_contact :
            frappe.db.sql(""" DELETE from `tabContact` WHERE
             name = '{}' """.format(customer.customer_primary_contact))
        customer.customer_primary_contact  = ""
        
        #customer.e_mail_id = main_data.get("email_id")
        customer.save()
        
        if main_data.get("address")  and len( main_data.get("address")) > 0 :
            for address in  main_data.get("address") :
                #if exit address 
                addr =False
                # addr = frappe.get_doc("Address" , customer.customer_name +"-"+address.get("address_type"))
                try :
                            addr = frappe.get_doc("Address" , customer.customer_name +"-"+address.get("address_type"))
                  
                            
                except :pass

                if not addr :
                    addr = frappe.new_doc("Address")
                    
                # addr.title = customer.name
                addr.address_type = address.get("address_type")
                addr.address_line1 = address.get("address_line1")
                addr.city = address.get("city")
                addr.country = address.get("country") or "Egypt"
                addr.is_primary_address = address.get("is_primary_address")
                addr.links= []
                da = addr.append("links" ,{})
                da.link_doctype = "Customer"
                da.link_name = customer.name
                addr.save()




        frappe.local.response['erp_id'] = customer.name
        frappe.local.response['customer_id'] = customer.remote_id
        frappe.local.response['http_status_code'] = 200
    except Exception as e :
        
        frappe.local.response['message'] = str(e)
        frappe.local.response['http_status_code'] = 400 
