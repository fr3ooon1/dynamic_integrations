from optparse import Option
from dataclasses_json import config
import frappe
import json
from numpy import append
import requests
from .utils import create_error
import random


def make_login(func ,*args ,**kwargs ):
    def login(*args , **kwargs ):

        main = frappe.get_doc("Api Integration Profile" , "Magento")
        url =main.login_url #"https://moe.stylisheve.com/rest/V1/integration/admin/token"
        data = main.login_payload
        varint = kwargs.get("sku") if kwargs.get("sku")  else " "
        attr_code=  kwargs.get("attr_code")
        urlf = main.end_point #"https://moe.stylisheve.com/rest/V1/"
        end_points = {

            "attributes" : "products/attributes" ,
            "products" : "products" ,
            "customers": "customers/search?searchCriteria=1" ,
            "invocies" :  "invoices" ,
            "products" : "products" ,
            "categories" : "categories" ,
            "courier"    :"shipping/methods",
            "Configurable Attribute" : "configurable-products/{}/options".format(varint) ,
            "create_child":  "configurable-products/{}/child".format(varint) ,
            "add-attribute-option" : "products/attributes/{}/options".format(attr_code)

        }
        headers = {
            "Content-Type" :"application/json"
        }
        r = requests.post(url , data=data , headers=headers)
    
        if r.status_code == 200 :
            headers =  {
            "Content-Type" :"application/json" ,
            "Authorization" : "Bearer " +r.json() ,
             }
            
            if kwargs.get("api") :
                end_point = end_points[kwargs.get("api")] 
                if kwargs.get("method") == "get" :
                    end_point =  end_point +"?searchCriteria=1"
                uri = urlf +  end_point
                return func(headers = headers , url = uri , api =kwargs.get("api") , mathod= kwargs.get("method") ,obj =kwargs.get("obj") )
        else :
            #frappe.msgprint(str(r.text))
            return False
    return login


@make_login
def post_item_attr (*args , **kwargs ):
    url = kwargs.get("url") 
    headers =kwargs.get("headers") 
    api = kwargs.get("api") 
    
    if not headers :
        frappe.throw(""" Error in setting Headers """)
   
    if kwargs.get("mathod") == "post" :
       
        data = kwargs.get("obj") 
        # if api == "Configurable Attribute" :
        #     frappe.msgprint(str(data))
        request = requests.post(url , headers=headers , data =json.dumps(data))
        if request.status_code == 200 :
            # if api == "Configurable Attribute" :
            #frappe.msgprint(str(request.text))
            return request.json()
        else :
            erro = create_error(request.text if len(request.text) < 230 else request.text[1:230])
            # if api == "Configurable Attribute" :
            #frappe.msgprint(str(request.text))
            return False
        return request.text
    if kwargs.get("mathod") == "get" :
        request = requests.get(url , headers=headers)
        return request.json()
   





@frappe.whitelist()		
def item_attribute_sync() :
    item_data = frappe.db.sql(""" 
            SELECT name ,  attribute_name as default_frontend_label  ,
             'select' as frontend_input  , attribute_name as note  FROM `tabItem Attribute`  WHERE sync_id IS NULL or sync_id = ' '
                    """,as_dict = True)
    request_data = []
    for attr in item_data :
        name = attr.get("name")
        option = frappe.db.sql(""" SELECT  attribute_value as label , abbr as value 
          FROM `tabItem Attribute Value`  where parent = '{}' """.format(name) , as_dict=1)
        attr["options"] = option
        attr.pop("name" , None)
        request_data.append({"attribute":attr})
    for item in request_data :
     
        obj =  post_item_attr( api = "attributes" ,method="post" , obj=item)
        if obj :
           
            item_obj = item.get("attribute")
            # frappe.throw(str(item_obj))
            item_name = item_obj.get("default_frontend_label")
            # frappe.throw(str(item_name))
            create = obj
            # frappe.throw(str(create.get("attribute_id")))
            sync_id = obj.get("attribute_id")
            sunc_code = obj.get("attribute_code")
            frappe.db.sql(""" 
            UPDATE `tabItem Attribute` SET 	sync_id	 = '{}' ,sync_source = '{}' WHERE attribute_name = '{}'
            """.format(sync_id ,sunc_code,item_name  ) )
            frappe.db.commit()
            item_data  = frappe.db.sql(""" SELECT name FROM `tabItem Attribute`
             where attribute_name = '{}'""".format(item_name) ,as_dict=1)
            options = obj.get("options")
            for sub_atr in options :
                if sub_atr.get("label") and sub_atr.get("label") != " " :
                    frappe.db.sql("""UPDATE `tabItem Attribute Value` set  value ='{}'
                    where attribute_value = '{}'
                    """.format(sub_atr.get("value") ,sub_atr.get("label")))
                    frappe.db.commit()
            frappe.msgprint("updated")
        else :
            frappe.msgprint("Ctreation erro for item {}".format(item.get("attribute")))


def return_customer_obj(customer):

    # Check if customer is old customer 
    old_customer = frappe.db.sql(""" SELECT name FROM `tabCustomer` 
        WHERE remote_id  ='{}'   """.format(customer.get("id") ) ,as_dict =True)
    customer_obj =False
    if not old_customer or len(old_customer) == 0 :
        str_name = "{} {}".format(customer.get("firstname")  , customer.get("lastname"))
        old_customer =  frappe.db.sql(""" SELECT name FROM `tabCustomer` 
        WHERE name  ='{}'   """.format(str_name ) ,as_dict =True)
    
    if old_customer and len(old_customer) > 0 :
        if old_customer[0].get("name") :
            customer_obj = frappe.get_doc("Customer" , old_customer[0].get("name") )
            
    #if this function didnot return object then create new customer obj 
    name = "{} {}".format(customer.get("firstname")  , customer.get("lastname"))
    if not customer_obj:
        customer_obj = frappe.new_doc("Customer")
    customer_obj.customer_name = name
    customer_obj.customer_type = "Individual"
    customer_obj.e_mail_id     =  customer.get("email")
    customer_obj.phone         =     customer.get("custom_attributes")[0].get('value')
    #check for customer group 
    group_obj = False
    # frappe.throw(str( customer.get("custom_attributes")[0].get("value")  ))
    customer_obj.remote_id = customer.get("id")
    if customer.get("group_id") :
            customer_group = frappe.db.sql(""" SELECT name FROM `tabCustomer Group` 
            WHERE group_id ='{}' 
            """.format( customer.get("group_id")  ) ,as_dict=True)
            if customer_group  and customer_group[0].get('name'):
                group_obj = frappe.get_doc("Customer Group" , customer_group[0].get('name') )
    if not group_obj :
        customer_obj.customer_group = "All Customer Groups" 
    else :
        customer_obj.customer_group = group_obj.name
    customer_obj.territory = "All Territories"
    try :
        customer_obj.save()
    except:
        customer_obj.customer_name = name  +str(random.randint(2,150))
        customer_obj.save()
    return customer_obj
@frappe.whitelist()	
def get_customer(*args , **kwargs):
    rquest = post_item_attr( api = "customers" ,method="get")
    # frappe.throw(str(rquest))
    customers = rquest.get("items")
    for customer in customers :
        try :
             return_customer_obj(customer)
        except :pass

def confgi_product(item_sku , configrable):
    data = {"option" : configrable  }
    pass
def get_item_price(item_code , price_list =None) :
    qr = f""" 
    SELECT price_list_rate as price FROM `tabItem Price` WHERE item_code = '{item_code}'  and selling =1
    """
    if price_list :
        qr = qr + "and price_list = '{}'".format(price_list)

    price = frappe.db.sql(qr , as_dict=True)
    if price and len(price) > 0 :
        return price[-1].get('price')
    else :
        return 0 

def get_item_stock(item , wharehouse=None) :
    qty = frappe.db.sql(f""" SELECT SUM(actual_qty) as qty FROM `tabBin` WHERE item_code ='{item}'""",as_dict=1)
    if qty and len(qty) > 0 :
        # frappe.throw(str(qty[0].get("qty")))
        return qty[0].get("qty")
    else :
        return 0 
@frappe.whitelist()
def post_item(*args , **kwargs):
    sql = """SELECT name as code ,item_code as name  ,sku as sku , 
    '4' as attribute_set_id , '1' as status  , '4' as visibility  ,
     ( CASE when has_variants = 0 THEN
    'simple'   ELSE   'configurable'  end )as  "type_id" , '1' as weight FROM `tabItem` 
     WHERE   publish_in_hub = 1  and remote_id IS NULL or remote_id = ' ' 
    """
    if kwargs.get("item") :
        sql = sql + "and item_code = '{}' ".format(kwargs.get("item"))
    items = frappe.db.sql(sql,as_dict=1)
    request_data = []
    # frappe.throw(str(items))
    for obj in items :
        if not obj.get('sku') or len(obj.get('sku')) < 2  :
                obj['sku'] = str(obj.get("name")).replace(' ' , '-')   
        obj['price'] = get_item_price(obj.get('name'))
     
        obj["extension_attributes"]=  {
                    "website_ids" :[ 1 ],
                        "category_links": [{
                            "position": 0,
                            "category_id": "1"
                        }],
                        "stock_item": {
                        "qty": str(get_item_stock(obj.get('name')) or '0'),
                        "is_in_stock": 1
                        }
                    }
        config = []
        item_atr = frappe.db.sql(""" SELECT  attribute  as name FROM `tabItem Variant Attribute`
             WHERE parent = '{}' """.format(obj.get('code')) ,as_dict =1 )
        
        if obj.get("type_id") == "configurable"  :
            pass
        for attr in item_atr :
            attrs = frappe.db.sql(""" SELECT name as name , sync_source as label ,  sync_id as attribute_id
                from `tabItem Attribute` 
                        where name = '{}'  """.format(attr.get('name')) ,as_dict=True) 
            if attrs and attrs[0].get('attribute_id') :
                config.append(attrs[0])        
        obj["custom_attributes"] = [
                                {"attribute_code": "erp_id",  "value": obj.get('name') }
                                ]

        # frappe.throw(str(config))
        if obj.get("type_id") == "simple" and  len(config) > 0 :
           
            for con in config :
                # frappe.msgprint(str(obj.get('name')))
                variante_name=  str(obj.get('name')).split('-')
                last_name = str(variante_name[-1])
                tuple_names = tuple(variante_name[1::])
                tuple_str=(str('(') + str(tuple_names)[0:-1] + ')')
                # frappe.throw(variante_name[-1])
                item_attr_code  = frappe.db.sql("""SELECT attribute_value as attribute_code ,
                value as value FROM `tabItem Attribute Value` 
                WHERE parent = '{}'  and abbr = '{}' """.format(con.get('name'),variante_name[-1] ), as_dict=1)   
                obj["custom_attributes"].append(
                    {"attribute_code" : con.get("label") , 
                    "value" :item_attr_code[0].get('value') })
        else :
            for con in config :
                item_attr_code  = frappe.db.sql("""SELECT attribute_value as attribute_code ,value as value FROM `tabItem Attribute Value` 
                WHERE parent = '{}'  and value IS  NOT NULL or value != ' ' """.format(con.get('name')), as_dict=1)   
                obj["custom_attributes"].append({"attribute_code" : con.get("label") , 
                "value" :item_attr_code[0].get("value") })   


        
        
        obj.pop("code" , None)
        request_data.append({"product" : obj})
        # frappe.msgprint(str(obj))
        for item in request_data :
                
                items = item.get("product")
                # 1- create product 
                obj =  post_item_attr( api = "products" ,method="post" , obj=item)
                frappe.msgprint(str(obj))
                if not obj :
                     frappe.throw("Can Not create product %s"%items.get("name"))
                if obj :
                    remote_id = obj.get("id")
                    sku = obj.get("sku")
                    # frappe.throw(str(obj.get("sku")))
                    frappe.db.sql("""UPDATE `tabItem` set remote_id ='{}'  , sku = '{}'where 
                    item_code = '{}' """.format(str(remote_id) , sku,items.get("name"))) 
                    frappe.db.commit()
                    if obj.get("type_id") ==  "configurable" and len(config) > 0 :
                        for e in config  :
                            # frappe.throw(str(e))
                            parent = e.get("name")
                            values = frappe.db.sql(""" SELECT value as value_index 
                            FROM `tabItem Attribute Value` 
                            WHERE parent = '{}'  and value IS NOT NULL or value <> ' ' """.format(parent) ,as_dict=1)
                            # frappe.throw(str(values))
                            e.pop("name" , None)
                            e["position"] =  0
                            e["is_use_default"] = 1 
                            e["values"] = values
                            re_data = {"option" : e}
                            #config configrable
                            atrr_post = post_item_attr( api = 'Configurable Attribute' ,method="post" ,
                                                         obj=re_data , sku=sku)
                            # frappe.throw(str(atrr_post))
                            if not  atrr_post :
                                frappe.throw("Can not config product %s"%sku)
                    item_v = frappe.db.sql(""" 
                            select name, sku , variant_of from `tabItem` WHERE item_code='{}' and variant_of IS NOT NULL
                    """.format(items.get("name")) ,as_dict=1)
                    if item_v and item_v[0].get("variant_of") :
                        
                        route = str(item_v[0].get("variant_of")).replace(" " ,"-")
                        data_obj =  {
                                            "childSku": "{}".format(item_v[0].get('sku'))
                                        }
                        #add child to configrable item 
                        #      
                        # frappe.msgprint(str(data_obj))
                        # frappe.msgprint(str(route))
                        atrr_post = post_item_attr( api = 'create_child' ,method="post" , obj=data_obj , sku=route)
                        if not  atrr_post :
                                frappe.msgprint("Can not add Child to  %s"%(item_v[0].get('sku')))
                        
                    frappe.msgprint("updated")
                else :
                    frappe.msgprint("errro")



def return_courier_obj(c):

    """
        1- check fo existing courier
        2-update if exist
        3-create new one if not exist
    """

    # 1-
    old_courier = frappe.db.sql(""" SELECT name FROM `tabCourier` 
        WHERE remote_id  ='{}'   """.format(c.get("label") ) ,as_dict =True)
        

    # 2-
    if len(old_courier) > 0:
        courier = frappe.get_doc("Courier",c.get("label"))
        #for item in old_courier.values:
        courier.values = []
        courier.save()
        for item in c.get("value"):
            row = courier.append("values",{})
            row.value = item.get("value")
            row.label = item.get("label")
        courier.save()
        return courier
    # 3-
    else:
        if c.get("label"):
            corier = frappe.new_doc("Courier")
            corier.label = c.get("label")
            corier.remote_id = c.get("label")
            corier.save()
            if len(c.get("value")) > 0:
                for item in c.get("value"):
                    row = corier.append("values",{})
                    row.value = item.get("value")
                    row.label = item.get("label")
            
            corier.save()
            return corier
    return 

    



        
@frappe.whitelist()   
def get_courier(*args,**Kwargs):
    rquest = post_item_attr( api = "courier" ,method="get")
    for courier in rquest :
        try :
             return_courier_obj(courier)
        except Exception as ex:
            print("hello from exception",str(ex))
            pass