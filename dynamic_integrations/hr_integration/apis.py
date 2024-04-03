from ast import arg
from dynamic_integrations.utils import fetch_request_json
import frappe
from frappe import _, rename_doc
import frappe
from frappe.utils.data import flt, get_link_to_form, now_datetime, nowdate
import requests
from dateutil.parser import parse
from erpnext import get_default_company



@frappe.whitelist()
def get_hr_auth_token():
    hr_integration_setting = frappe.get_single("HR Integration Setting")
    if not hr_integration_setting :
        frappe .throw(_("Please Set HR Integration Setting"))


    login_request_type = hr_integration_setting.login_request_type
    login_request_url = hr_integration_setting.login_request_url
    login_request_body = hr_integration_setting.login_request_body or {}
    token_fieldname = hr_integration_setting.token_fieldname
    headers = {"Content-Type": "application/json"}

    # login_request_url = """http://160.153.234.244:65/api/checkuser?UserName=9&password=12&brcode=1&devicecode="""
    
    # login_request_body = {}
    # token_fieldname = "Token"
    token = ""
        # if (self.login_request_type == 'POST'):
        # frappe.msgprint(self.login_request_body)
    req_login = requests.request(login_request_type,login_request_url, headers=headers,
                                data=login_request_body)

    response_json = fetch_request_json(req_login)
    # self.create_log(headers,self.login_request_body,req_login)
    if req_login.ok:
        token = str(response_json) if not token_fieldname or isinstance(
            response_json, str) else response_json.get(token_fieldname)
        
        if not token:
            frappe.throw("Invalid Token Fieldname")
        
    else:
        frappe.throw(_(str(response_json)))

    return token


@frappe.whitelist()
def post_unposted_advances(error_list=[],stellment=0) :
	payroll_month = frappe.get_doc("Payroll Month" , payroll_month)
	token = get_hr_auth_token()
	server_url = frappe.db.get_single_value("HR Integration Setting","server_url")
	if stellment :
		method_url = "/api/ERPAdvanceSettlement"
	else :
		method_url = "/api/ERPAdvance"
	url = server_url+method_url
	method = "POST"
	parameters = {
		# "YEARID":payroll_month.year_id,
		# "MONTHID":payroll_month.month_id,
		"brcode":payroll_month.branch_code
	}
	headers = {
		"Content-Type":"application/json",
		"Authorization":f"Bearer {token}"
	}
	result = requests.request(method,url,params=parameters,headers=headers,json=error_list)



# @frappe.whitelist()
# def create_employee_advance(*args,**kwargs):        

#     company = frappe.get_doc("Company",get_default_company())
#     if not frappe.db.exists("Company Accounts",company.name):
#         frappe.response["http_status_code"] = 400
#         frappe.response["message"] = _("Please Set Company Accounts")
#         return 


#     company_settings = frappe.get_doc("Company Accounts",company.name)

#     if not (company_settings.advance_payment_account and company_settings.employee_advance_account) :
#         frappe.response["http_status_code"] = 400
#         frappe.response["message"] = _("Please Set Employee Advance Company Accounts")
#         return 
    
#     advance_amount = kwargs.get("amount") or 0
#     employee_no = kwargs.get("employee") or ''
#     posting_date = kwargs.get("posting_date") or nowdate()
#     if posting_date :
#         posting_date = parse(str(posting_date)).date()

#     if not frappe.db.exists("Employee",employee_no):
#         frappe.response["http_status_code"] = 400
#         frappe.response["message"] = _("Invalid Employee")
#         return 

#     if not advance_amount :
#         frappe.response["http_status_code"] = 400
#         frappe.response["message"] = _("Invalid Advance Amount")
#         return 
    
#     employee = frappe.get_doc("Employee",employee_no)

#     je = frappe.new_doc("Journal Entry")
#     je.posting_date = posting_date
#     je.voucher_type = 'Journal Entry'
#     je.company = company.name
#     je.remark = f'Journal Entry against Employee Advance for {employee.name} : {employee.employee_name} => {advance_amount}'
#     je.user_remark = f'Journal Entry against Employee Advance for {employee.name} : {employee.employee_name} => {advance_amount}'
    
#     je.append("accounts", {
#         "account":  company_settings.advance_payment_account,
#         "credit_in_account_currency": flt(advance_amount),
#         "cost_center": company_settings.advance_cost_center,
#     })

#     je.append("accounts", {
#         "account":   company_settings.employee_advance_account,
#         "debit_in_account_currency": flt(advance_amount),
#         "party_type" :"Employee",
#         "party":employee_no
#     })

    
#     # for i in je.accounts :
#     # 	frappe.msgprint(f"account : {i.account} | account_currency : {i.account_currency} | debit_in_account_currency : {i.debit_in_account_currency} | credit_in_account_currency : {i.credit_in_account_currency}")
#     try :
#         if company_settings.submit_payment_jv :
#             je.submit()
#         else :
#             je.save()
#     except Exception as e :
#         frappe.response["http_status_code"] = 400
#         frappe.response["message"] = _(str(e))
#         return 


#     frappe.response["http_status_code"] = 200
#     frappe.response["message"] = _("Advance JL {} was Created Successfully").format(je.name)
#     frappe.response["jl"] = je.name
#     return 














def rename_all_employees():
    employees = frappe.get_all("Employee",['name','hr_id'])
    for emp in employees :
        print (emp.name , '  ' , emp.hr_id)
        if  emp.hr_id :
                merge = frappe.db.exists("Employee",emp.hr_id)
                rename_doc("Employee", emp.name, emp.hr_id, force=1, merge=merge)
                frappe.db.commit()