from dynamic_integrations.utils import create_error
import frappe


# Cost Center Doc Events
def create_cost_center (self,fun=''):
    run_api_integrations(self.doctype,request_method = "POST",integration_type = "Create")


def update_cost_center (self,fun=''):
    run_api_integrations(self.doctype,request_method = "POST",integration_type = "Update")







# Asset Doc Events

def submit_asset (self,fun=''):
    run_api_integrations(self.doctype,request_method = "POST",integration_type = "Update")



# Asset Movements Doc Events



def submit_asset_movements (self,fun=''):
    run_api_integrations(f"{self.doctype} Item",request_method = "POST",integration_type = "Update")






def run_api_integrations (doctype,request_method = "POST",integration_type = "Update"):
    integration_doctype = "Api Integration"
    sql = f"""
    select row.name from `tab{integration_doctype}` row where ifnull(row.enabled,0) <> 0
    and webhook_doctype ='{doctype}'
    and request_method ='{request_method}'
    and  integration_type = '{integration_type}'
    """
    # frappe.msgprint(sql)
    doc_list = frappe.db.sql_list(sql)
    for docname in doc_list :
        try : 
            doc = frappe.get_doc(integration_doctype,docname)
            doc.execute()
        except Exception as e:
            create_error(e)
        # doc.save()


