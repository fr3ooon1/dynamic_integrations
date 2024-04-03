import frappe
import json
from dynamic_integrations.main_api import post_item
from erpnext.selling.doctype.sales_order.sales_order import  make_sales_invoice
@frappe.whitelist()
def order_obj():
    try :
        data = json.loads(frappe.request.data)
        main_data = data.get("data")
        #get customer main_data.get("customer") 
        if not main_data.get("customer")  :
             frappe.local.response['message'] = "cunstomer None Note found "
             frappe.local.response['http_status_code'] = 404 
        customer = frappe.db.sql("""SELECT name from 
               `tabCustomer` WHERE remote_id ='{}' """.format(main_data.get("customer") ) ,as_dict=True)
        if not customer or not customer[0].get('customer_name') :
            frappe.local.response['message'] = "cunstomer '{}' Note found ".format(main_data.get("customer") )
            frappe.local.response['http_status_code'] = 404 

        if not main_data.get("currency") : 
            frappe.local.response['message'] = "Currency not found "
            frappe.local.response['http_status_code'] = 404 

        if not main_data.get("items") :
            frappe.local.response['message'] = " Items not found "
            frappe.local.response['http_status_code'] = 404 
        order = frappe.new_doc("Sales Order")
        order.customer = customer[0].get('name')
        order.order_type = "Sales"
        order.delivery_date = main_data.get("created_at")
        order.currency = main_data.get("currency")
        order.conversion_rate = main_data.get("conversion_rate") or 1
        order.remote_id =  main_data.get("entity_id")
        order.increment_id = main_data.get("increment_id")
        for item in main_data.get("items"):
            #it=frappe._dict(it)
            row = order.append("items",{})
            row.item_code=item.get("item_code")
            row.qty= item.get ("qty")
            row.rate= item.get ("rate")
        try :
            order.save()
            order.docstatus = 1
            order.save()
            erp_id =" " +  str(order.name) + " "
            #frappe.local.response["erp_id"] = str(order.name or 'Error')
            #frappe.local.response["entity_id"] = main_data.get("entity_id") 
            frappe.local.response['http_status_code'] = 200
            return  {"erp_id" : "{}".format(erp_id)  }
        except Exception as e :
            frappe.local.response['message'] = "Order Create Error" + str(e)
            frappe.local.response['http_status_code'] = 400 
    except Exception as e :
        
        frappe.local.response['message'] = str(e)
        frappe.local.response['http_status_code'] = 400 




def validate(self ,*args ,**kwargs):
    if self.item_code :
        self.sku = str(self.item_code).replace(' ' , '-')

    if self.publish_in_hub :
        post_item(item = self.item_code)

def validate_price(self,*args , **kwargs):
    if self.selling :
         item = frappe.get_doc("Item" , self.item_code)
         if item.publish_in_hub :
             post_item(item = self.item_code)

""" 
bill_of_landing reuqet 
end_poit =api/method/dynamic_integrations.dynamic_integrations.order.bill_of_landing

{"data" :{
    "bill_of_lading_no" :"transaction number" ,
    "erp_id" : "document erp id if meyhod is update else null in method is create" ,
    "courier" : "value is one of courier values value " ,
    "sales_order" : "order erp id ",
    "entity_id" :"magento transaction ID",

}}


respone = {
    "erp_id" "document_local_name", 
    "entity_id": "entity_id" ,
    
}

"""

@frappe.whitelist()
def bill_of_landing():
    bill_of_landing = False
    json_data = json.loads(frappe.request.data)
    data = json_data.get("data")
    number = data.get("bill_of_lading_no")
    if not number  : 
        frappe.local.response['message'] = "Please Set Transation Number "
        frappe.local.response['http_status_code'] = 400 
    #check if request for update  
    if  data.get("erp_id") and  len(data.get("erp_id")) > 1 :    
        bill_of_landing = frappe.get_doc("Bill of lading" , data.get("erp_id"))
    else :
        bill_of_landing = frappe.new_doc("Bill of lading")
    old_name  , transaction_number = str(data.get("erp_id") or "none")  ,str(number or "No Number")
    if not bill_of_landing :
        frappe.local.response['message'] = "Transation {} Erro Accourd  Local Name {} ".format(transaction_number,old_name )
        frappe.local.response['http_status_code'] = 400 
        return
    if bill_of_landing :
        #get Parent Courier 
        courier = data.get("courier")
        if not courier :
            frappe.local.response['message'] = """Transation {} Has no Courier 
            """.format(transaction_number,old_name )
            frappe.local.response['http_status_code'] = 400 
            return
        parent_courier  = frappe.db.sql(""" SELECT name From `tabCourier`
                            WHERE label = '{}' """.format(courier) ,as_dict =1)
        if not parent_courier or len(parent_courier) == 0  or not parent_courier[0].get('name'):
            frappe.local.response['message'] = "Courier {} Not found ".format(courier)
            frappe.local.response['http_status_code'] = 400 
            return
        bill_of_landing.courier =parent_courier[0].get('name')
        #api Send Sales Order erp id 
        sales_order = data.get('sales_order')
        #validate sales order 
        sales_order_sec = frappe.db.sql(""" SELECT name FROM 
        `tabSales Order` WHERE name ='{}'
             """.format(sales_order) ,as_dict =1)
        
        if not sales_order_sec or len(sales_order_sec ) ==0 or not  sales_order_sec[0].get('name'):
            frappe.local.response['message'] = "Sales ORder{} Not found ".format( sales_order)
            frappe.local.response['http_status_code'] = 400 
            return
        #last Creation
        bill_of_landing.sales_order = sales_order
        bill_of_landing.status= "On Progress"
        bill_of_landing.instance_id = data.get("entity_id")
        bill_of_landing.save()
        
        frappe.local.response['erp_id'] = str(bill_of_landing.name)
        frappe.local.response['entity_id'] = str(bill_of_landing.instance_id)
        frappe.local.response['http_status_code'] = 200