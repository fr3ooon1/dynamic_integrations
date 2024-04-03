# Copyright (c) 2022, Dynamic Technology and contributors
# For license information, please see license.txt

# import frappe
from dynamic_integrations.hr_integration.apis import get_hr_auth_token, post_unposted_advances
from dynamic_integrations.utils import fetch_request_json, save_doc
from frappe.model.document import Document
from erpnext import get_default_company
import frappe
from frappe.model.document import Document
from frappe.utils.data import flt, get_link_to_form, nowdate
from frappe import _
from dateutil.parser import parse
import requests


class HREmployeeAdvanceSettlement(Document):
	pass





@frappe.whitelist()
def get_employee_advance_settlement(payroll_month):
	payroll_month = frappe.get_doc("Payroll Month" , payroll_month)
	token = get_hr_auth_token()
	server_url = frappe.db.get_single_value("HR Integration Setting","server_url")
	method_url = "/api/ERPAdvanceSettlement"
	url = server_url+method_url
	method = "GET"
	parameters = {
		# "YEARID":payroll_month.year_id,
		# "MONTHID":payroll_month.month_id,
		"brcode":payroll_month.branch_code
	}
	headers = {
		"Authorization":f"Bearer {token}"
	}
	result = requests.request(method,url,params=parameters,headers=headers)
	json_response = fetch_request_json(result) or []
	if result.status_code != 200 :
		frappe.throw(str(json_response))
	print (" json_response => ",json_response)
	print (" result.url => ",result.url)
	advance_count = 0
	employee_count = 0
	error_list = []
	doc = None
	if isinstance(json_response,list):
		# salaries_count = len(json_response)
		for row in json_response :
			# payroll_month = frappe.db.get_value("Payroll Month",{
			# 		"year_id" : row.get("Year_ID") ,
			# 		"month_id" : row.get("Month_ID") ,
			# 		"company_code" : row.get("cmp_code")
			# },['*'],as_dict=1)

			doc_props = {
				"doctype" : "HR Employee Advance Settlement",
				"payroll_month":payroll_month.name if payroll_month else '',
				"month":payroll_month.month if payroll_month else '',
				"year":payroll_month.year if payroll_month else '',
				"month_id":payroll_month.month_id if payroll_month else row.get("Month_ID"),
				"year_id":payroll_month.year_id if payroll_month else row.get("Year_ID"),
				"hr_id":row.get("RecSer"),
				"employee":row.get("Staff_ID"),
				"hr_employee_advance":row.get("Trx_ser"),
				"advance_settlement_amount":row.get("DiffValue") or 0,
				"total_amount":row.get("TOTALvalue") or 0,
				"posting_date":row.get("ActionDate") or nowdate(),
			}
			employee = ""
			employee_name = ""
			# employee,employee_name = frappe.db.get_value("Employee",{"hr_id":row.get("Staff_ID")} ,["name","employee_name"] ) 
			employee_doc= frappe.db.get_value("Employee",{"hr_id":row.get("Staff_ID")} ,["name","employee_name"] , as_dict=1 ) 
			if not employee_doc :
				employee_count += 1
				continue 
			if employee_doc :
				employee = employee_doc.name
				employee_name = employee_doc.employee_name
			
			
			# employee,employee_name = frappe.db.get_value("Employee",{"hr_id":row.get("Staff_ID")} ,["name","employee_name"] , as_dict=1 ) 
			doc_props ["employee"] = employee
			doc_props ["employee_name"] = employee_name

			doc = save_doc(doc_props)

			# print (" doc. name  " , doc.name)
			advance_count += 1

			try :
				create_employee_advance_settlement(doc.name)
			except Exception as e :
				frappe.msgprint(f"{doc.name} Error => " + str(e),indicator='red')
				error_list.append(row.get("RecSer"))
				if doc :
					doc.delete()


	if error_list :
		post_unposted_advances(error_list)


	frappe.msgprint(_("{} Advances is Synced , {} Employees is not Found").format(advance_count,employee_count),_("Done"))





@frappe.whitelist()
def create_employee_advance_settlement(hr_employee_advance_settlement):  
	doc =  frappe.get_doc("HR Employee Advance Settlement",hr_employee_advance_settlement)    
	advance_amount = doc.advance_settlement_amount
	employee_no = doc.employee
	posting_date = doc.posting_date
	company = frappe.get_doc("Company",get_default_company())
	if not frappe.db.exists("Company Accounts",company.name):
		frappe.throw(_("Please Set Company Accounts"))
		frappe.response["http_status_code"] = 400
		frappe.response["message"] = _("Please Set Company Accounts")
		return 


	company_settings = frappe.get_doc("Company Accounts",company.name)

	if not (company_settings.advance_payment_account and company_settings.employee_advance_account) :
		frappe.throw(_("Please Set Employee Advance Company Accounts"))
		frappe.response["http_status_code"] = 400
		frappe.response["message"] = _("Please Set Employee Advance Company Accounts")
		return 

	if posting_date :
		posting_date = parse(str(posting_date)).date()

	if not frappe.db.exists("Employee",employee_no):
		frappe.throw(_("Invalid Employee"))
		frappe.response["http_status_code"] = 400
		frappe.response["message"] = _("Invalid Employee")
		return 

	if not advance_amount :
		frappe.throw(_("Invalid Advance Amount"))
		frappe.response["http_status_code"] = 400
		frappe.response["message"] = _("Invalid Advance Amount")
		return 

	employee = frappe.get_doc("Employee",employee_no)

	je = frappe.new_doc("Journal Entry")
	je.posting_date = posting_date
	je.voucher_type = 'Journal Entry'
	je.company = company.name
	je.remark = f'Journal Entry against Employee Advance Settlement for {employee.name} : {employee.employee_name} => {advance_amount}'
	je.user_remark = f'Journal Entry against Employee Advance Settlement for {employee.name} : {employee.employee_name} => {advance_amount}'

	je.append("accounts", {
		"account":   company_settings.employee_advance_account,
		"credit_in_account_currency": flt(advance_amount),
		"cost_center": company_settings.advance_cost_center,
		"party_type" :"Employee",
		"party":employee_no,
		"reference_type":doc.doctype,
		"reference_name":doc.name,
	})

	je.append("accounts", {
		"account":   company_settings.employee_advance_adjustment,
		"debit_in_account_currency": flt(advance_amount),
		"party_type" :"Employee",
		"party":employee_no,
		"reference_type":doc.doctype,
		"reference_name":doc.name,
	})


	# for i in je.accounts :
	# 	frappe.msgprint(f"account : {i.account} | account_currency : {i.account_currency} | debit_in_account_currency : {i.debit_in_account_currency} | credit_in_account_currency : {i.credit_in_account_currency}")
	try :
		if company_settings.submit_payment_jv :
			je.submit()
		else :
			je.save()
	except Exception as e :
		frappe.throw(_(str(e)))
		frappe.response["http_status_code"] = 400
		frappe.response["message"] = _(str(e))
		return 


	frappe.response["http_status_code"] = 200
	frappe.response["message"] = _("Advance Settlement JL {} was Created Successfully").format(je.name)
	frappe.response["jl"] = je.name
	return je.name




