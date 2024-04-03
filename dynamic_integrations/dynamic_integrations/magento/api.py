from urllib import response
import frappe
import requests
import json 
import random



DATA_TEMPATES = {
  "attributes" : {
            "default_frontend_label" :"" , 
            "frontend_input" : "" ,
            "note" : "" ,
            "item_attribute_values" :[
                                        {
                                            "label"  : "" ,
                                            "value"  :  "" 
                                            
                                        }
                                    ]
            
            
  }

}


# """ 
# Create Standard Function To create Customer 
# # return_customer_obj Take rresponse customer obj with customer data
# "customer": {
#    "firstname": "test", 
#    "lastname":"string" ,

# "customer_type": "Individual" #not req ,
# "group_id ": "int" #not req ,

# "mobile_no": "01283699858",
# "email" :"testmail@gail.com"
# },
# "address": [{
# "title": "test",
# "address_title": "test",
# "address_type": "Billing" or "\ Shipping",
# "address_line1": "مدينه العبور محطه حليم ",
# "city": "القاهره",
# "country": "Egypt",
# "is_primary_address": 0,
# "is_shipping_address": 0,
# "disabled": 0,
# "is_your_company_address": 0

# }]
#     }


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
    #check for customer group 
    group_obj = False
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
    
    # if customer.get('email') :
    #     #check if customer has old acintact 
    #     if customer_obj.customer_primary_contact :
    #         customer_obj.customer_primary_contact = ""
    #         conatct = frappe.get_doc("Contact" , customer_obj.customer_primary_contact)
    #         conatct.links = []
    #         conatct.save()
    #         # conatct.delete()
       
    # customer_obj.email_id = customer.get('email')
    try :
        customer_obj.save()
    except:
        customer_obj.customer_name = name  +str(random.randint(2,150))

    return customer_obj




#get api to call


def make_login(func ,*args ,**kwargs ):
    def login(*args , **kwargs ):
        print("\n\n\n\n--loogin->")
        print(func)
        print(args)
        print(kwargs)
        print("\n\n\n\n--->")
        url = "https://karim-mage2.rushbrush.net/rest/V1/integration/admin/token"
        data = {
            "username" :"admin" ,
            "password" :"admin123"
        }
        urlf = "https://karim-mage2.rushbrush.net/rest/V1/"
        end_points = {

            "attributes" : "products/attributes" ,
            "products" : "products" ,
            "customers": "customers/search?searchCriteria=1" ,
            "invocies" :  "invoices" ,
            "products" : "products" ,
            "categories" : "categories"
        }
        headers = {
            "Content-Type" :"application/json"
        }
        r = requests.post(url , data=json.dumps(data) , headers=headers)
        
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
                return func(headers = headers , url = uri , api =kwargs.get("api") ,
                      doctype=kwargs.get("doctype"), mathod= kwargs.get("method") )
        else :
            return False
    return login

# @make_login
# @frappe.whitelist()
# def teste_api(*args , **kwargs ):
#     import requests
#     url = "http://92.205.106.50:8091/api/checkuser?UserName=1050&password=12&brcode=1&devicecode=/"
#     payload={}
#     headers = {}
#     response = requests.request("GET", url, headers=headers, data=payload)
#     print(response.text)
#     print("\n\n\n\n--->")
#     # print(kwargs)
#     frappe.throw(str(response.text))
#     return {"test":1}

# @make_login
@frappe.whitelist()
def post_item_attr (*args , **kwargs ): 
    url = kwargs.get("url") 
    headers =kwargs.get("headers")
    # print("\n\n\n\n--->")
    print(kwargs)
    # request = requests.get("http://92.205.106.50:8091/api/checkuser?UserName=1050&password=12&brcode=1&devicecode=/")
    # frappe.throw(str(request.text))
    if not headers :
       return ("error55")
    if kwargs.get("mathod") == "post" and kwargs.get("doctype") :
        data =data_sql( kwargs.get("doctype"))
        for i in data :
            
            data  = {
                    "product": {
                        "sku": "MS-Champ",
                        "name": "Champ Tee",
                        "attribute_set_id": 9,
                        "status": 1,
                        "visibility": 4,
                        "type_id": "configurable",
                        "weight": "0.5",
                        "extension_attributes": {
                            "category_links": [
                                {
                                    "position": 0,
                                    "category_id": "11"
                                },
                                {
                                    "position": 1,
                                    "category_id": "12"
                                },
                                {
                                    "position": 2,
                                    "category_id": "16"
                                }
                            ]
                        },
                        "custom_attributes": [
                            {
                                "attribute_code": "description",
                                "value": "The Champ Tee keeps you cool and dry while you do your thing. Let everyone know who you are by adding your name on the back for only $10."
                            },
                            {
                                "attribute_code": "tax_class_id",
                                "value": "2"
                            },
                            {
                                "attribute_code": "material",
                                "value": "148"
                            },
                            {
                                "attribute_code": "pattern",
                                "value": "196"
                            },
                            {
                                "attribute_code": "color",
                                "value": "52"
                            }
                        ]
                    }
                    }

            request = requests.post(url , data= json.dumps(data) , headers=headers)
            frappe.throw(str(request.text))


    


def data_sql(doctype):
    data = frappe.db.sql("""SELECT  name  from `tab{}` WHERE sync_id  IS NULL or  sync_id= " "  """.format(doctype) ,as_dict=1)
    # data = frappe.get_all("Item Attribute" ,fields= ['*'] )
    # frappe.throw(str(data))
    return data

def data_templates(name , item):
    if name == "attributes":

       
       child_list =[]
       child_data = frappe.db.sql(""" SELECT attribute_value as value, abbr as label FROM `tabItem Attribute Value` 
                        WHERE parent ='{}' """.format(item.get("name"))  ,as_dict=1)

    
       template =  DATA_TEMPATES['attributes'] 
       template['default_frontend_label'] = item.get("name")
       template['frontend_input'] = "1" 
       template['note'] = item.get("name")
       template['item_attribute_values'] = child_data
       return {"attribute" : template}

    if name =="products":
       {
  "product": {
    "sku": "MS-Champ",
    "name": "Champ Tee",
    "attribute_set_id": 9,
    "status": 1,
    "visibility": 4,
    "type_id": "configurable",
    "weight": "1",
    "extension_attributes": {
        "category_links": [
            {
                "position": 0,
                "category_id": "11"
            },
            {
                "position": 1,
                "category_id": "12"
            },
            {
                "position": 2,
                "category_id": "16"
            }
        ]
    },
    "custom_attributes": [
        {
            "attribute_code": "description",
            "value": "The Champ Tee keeps you cool and dry while you do your thing. Let everyone know who you are by adding your name on the back for only $10."
        },
      
        {
            "attribute_code": "pattern",
            "value": "196"
        },
        {
            "attribute_code": "color",
            "value": "52"
        }
    ]
  }
}





def get_item_price(item_code , price_list =None) :
    qr = """ 
    SELECT price_list_rate as price FORM `tabItem Price` WHERE item_code = item_code  and selling =1
    """
    if price_list :
        qr = qr + "and price_list = '{}'".format(price_list)

    price = frappe.db.sql(qr , as_dict=True)
    if price and len(price) > 0 :
        return price[-1].get('price')
    else :
        return 0 

"""
  "sku": "testAgain--2-1",
                "name": "Test-002-1",
                "attribute_set_id": 4,
                "price": 250,
                "status": 1,
                "visibility": 3,"extension_attributes": {
                "type_id": "simple",
                "weight": "0.5",
                 
                    "category_links": [
                        {
                            "position": 0,
                            "category_id": "3"
                        }
                    ],
                    "stock_item": {
                        "qty": "10000",
                        "is_in_stock": 1
                    }
                },

"""

# @make_login
@frappe.whitelist()
def post_product_magento(product):
    #product data 
    data = {
        "sku"              : product.item_code ,
        "name"             : product.item_name ,
        "attribute_set_id" :   4 ,
        "price"            : float(get_item_price(product.item_code , None) or 0) ,
        "status"           : 1 ,
        "visibility"       : 1 ,
        "type_id"          : "simple",
        "weight"           : "0.5",
        "extension_attributes": {
             "category_links": [
                        {
                            "position": 0,
                            "category_id": "3"
                        }
                    ],
                    "stock_item": {
                        "qty": "100",
                        "is_in_stock": 1
                    }

                     },
              
         "custom_attributes": [
                   
                    {
                        "attribute_code": "erp_id",
                        "value": product.name,
                       
                    } ,
                ]


    }

    # items_data = frappe.db.sql("""  SELECT name , item_name , item_code FROM `tabItem` WHERE
    # remote_id
    
    # """)

    return data



@frappe.whitelist()
def get_stock_balance():
    try:
        condition = " where 1=1"
        data = json.loads(frappe.request.data)
        if data.get("item_code"):
            condition += " and tb.item_code='%s'"%data.get("item_code")
        if data.get("warehouse"):
            condition += " and tb.warehouse='%s'"%data.get("warehouse")
        if data.get("template"):
            condition += " and ti.variant_of = '%s'"%data.get("template")
        if data.get("item_name"):
            condition += " and ti.item_name like '%%%s%%'"%data.get("item_name")
        if data.get("item_group"):
            condition += " and ti.item_group like '%%%s%%'"%data.get("item_group")

        sql_q =f"""
            SELECT 
            tb.item_code
            ,tb.stock_uom  
            ,tb.warehouse 
            ,tb.actual_qty
            ,tb.valuation_rate
            ,ti.item_name 
            ,ti.variant_of as 'template'
            ,ti.item_group 
            FROM tabBin tb 
            inner join tabItem ti 
            on ti.name =tb.item_code 
            {condition}
            """
        print("sql_q ==> ",sql_q)
        res = frappe.db.sql(sql_q,as_dict=1)

        # frappe.local.response["data"] = res
        # frappe.local.response['http_status_code'] = 200
        return res
    except Exception as ex:
        frappe.local.response['http_status_code'] = 400
        return

