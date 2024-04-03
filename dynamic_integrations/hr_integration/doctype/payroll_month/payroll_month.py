# Copyright (c) 2022, Dynamic Technology and contributors
# For license information, please see license.txt

from dynamic_integrations.hr_integration.doctype.hr_employee_advance.hr_employee_advance import create_employee_advance, get_employee_advance
from dynamic_integrations.hr_integration.doctype.hr_employee_advance_settlement.hr_employee_advance_settlement import create_employee_advance_settlement, get_employee_advance_settlement
from dynamic_integrations.utils import fetch_request_json, save_doc
from dynamic_integrations.hr_integration.apis import get_hr_auth_token
from erpnext import get_default_company
import frappe
from frappe.model.document import Document
from frappe.utils.data import flt, get_link_to_form, nowdate
import requests
from frappe import _
from dateutil.parser import parse
class PayrollMonth(Document):
	# def validate (self):
	# 	if not self.open :
	# 		frappe.throw(_("Can't Edit Closed Month"))

	@frappe.whitelist()
	def create_salaries_jl(self):
		salary_query = f"""
				select 
					SUM(IFNULL(net_salary,0)) as net_salary ,
					SUM(IFNULL(insurance ,0)) as insurance ,
					SUM(IFNULL(advance ,0)) as advance ,
					SUM(IFNULL(company_insurance ,0)) as company_insurance ,
					SUM(IFNULL(taxes ,0)) as taxes 
				from `tabEmployee Salary`
				where payroll_month = '{self.name}'
		"""
		salaries = frappe.db.sql(salary_query,as_dict=1)

		employee_salaries_query = f"""
				select 
					employee,
					IFNULL(net_salary,0) as net_salary ,
					IFNULL(insurance ,0) as insurance ,
					IFNULL(advance ,0) as advance ,
					IFNULL(company_insurance ,0) as company_insurance ,
					IFNULL(taxes ,0) as taxes 
				from `tabEmployee Salary`
				where payroll_month = '{self.name}'

		"""
		employee_salaries = frappe.db.sql(employee_salaries_query,as_dict=1)

		if not salaries :
			frappe.throw(_("Theres is no Salaries to Post"))
		salaries = salaries[0]
		if not (salaries.net_salary or salaries.insurance or salaries.taxes):
			frappe.throw(_("Theres is no Salaries to Post"))


		company_settings = self.get_company_settings()
		company = frappe.get_doc("Company",company_settings.company)
		je = frappe.new_doc("Journal Entry")
		je.posting_date = nowdate()
		je.voucher_type = 'Journal Entry'
		je.company = company.name
		je.remark = f'Journal Entry against {self.doctype} : {self.name}'
		je.user_remark = _('Accrual Journal Entry for salaries from {0} to {1}') \
            .format(self.from_date, self.to_date)
		
		#Detailed Salary
		for employee_Salary in employee_salaries :

			# Net Salary 
			if employee_Salary.net_salary :
				je.append("accounts", {
					"account":  company_settings.payroll_salary_account,
					"credit_in_account_currency": flt(employee_Salary.net_salary),
					"reference_type": self.doctype,
					"reference_name": self.name,
					"party_type":'Employee',
					"party":employee_Salary.employee,
					"cost_center": company_settings.cost_center,
				})

			# Advance
			if employee_Salary.advance :

				je.append("accounts", {
					"account":  company_settings.employee_advance_account,
					"credit_in_account_currency": flt(employee_Salary.advance),
					"reference_type": self.doctype,
					"reference_name": self.name,
					"party_type":'Employee',
					"party":employee_Salary.employee,
					"cost_center": company_settings.cost_center,
				})
				# je.append("accounts", {
				# 	"account":   company_settings.payroll_salary_account,
				# 	"debit_in_account_currency": flt(employee_Salary.advance),
				# 	"party_type":'Employee',
				# 	"party":employee_Salary.employee,
				# 	"reference_type": self.doctype,
				# 	"reference_name": self.name
				# })


		if salaries.net_salary or salaries.advance:

			je.append("accounts", {
				"account":   company_settings.salary_account,
				"debit_in_account_currency": flt(salaries.net_salary or 0) + flt(salaries.advance or 0),
				"reference_type": self.doctype,
				"reference_name": self.name
			})

		
		if salaries.insurance :
			je.append("accounts", {
				"account":  company_settings.payroll_insurance_account,
				"credit_in_account_currency": flt(salaries.insurance),
				"reference_type": self.doctype,
				"reference_name": self.name,
				"cost_center": company_settings.cost_center,
			})

			je.append("accounts", {
				"account":   company_settings.insurance_account,
				"debit_in_account_currency": flt(salaries.insurance),
				"reference_type": self.doctype,
				"reference_name": self.name
			})

		
		if salaries.taxes :
			je.append("accounts", {
				"account":  company_settings.payroll_tax_account,
				"credit_in_account_currency": flt(salaries.taxes),
				"reference_type": self.doctype,
				"reference_name": self.name,
				"cost_center": company_settings.cost_center,
			})

			je.append("accounts", {
				"account":   company_settings.tax_account,
				"debit_in_account_currency": flt(salaries.taxes),
				"reference_type": self.doctype,
				"reference_name": self.name
			})

		

			
		if salaries.company_insurance :
			je.append("accounts", {
				"account":  company_settings.company_insurances_account,
				"credit_in_account_currency": flt(salaries.company_insurance),
				"reference_type": self.doctype,
				"reference_name": self.name,
				"cost_center": company_settings.cost_center,
			})

			je.append("accounts", {
				"account":   company_settings.company_insurances_expense_account,
				"debit_in_account_currency": flt(salaries.company_insurance),
				"reference_type": self.doctype,
				"reference_name": self.name
			})

		# for i in je.accounts :
		# 	frappe.msgprint(f"account : {i.account} | account_currency : {i.account_currency} | debit_in_account_currency : {i.debit_in_account_currency} | credit_in_account_currency : {i.credit_in_account_currency}")
		je.submit()

		lnk = get_link_to_form(je.doctype, je.name)
		frappe.msgprint(_("{} {} was created").format(je.doctype,lnk))



	@frappe.whitelist()
	def has_jl_entries (self) :
		sql = """
		select jl.name from `tabJournal Entry Account` log inner join `tabJournal Entry` jl on jl.name = log.parent
		where jl.docstatus < 2 
		and reference_type ='Payroll Month'
		and reference_name ='{0}' and jl.voucher_type = '{1}'

		GROUP BY jl.name
		"""
		has_journal_entry = frappe.db.sql(sql.format(self.name,"Journal Entry"))
		has_cash_entry = frappe.db.sql(sql.format(self.name,"Cash Entry"))
		has_bank_entry = frappe.db.sql(sql.format(self.name,"Bank Entry"))

		return frappe._dict({
			"has_journal_entry" : 1 if has_journal_entry else 0,
			"has_cash_entry" : 1 if has_cash_entry else 0,
			"has_bank_entry" : 1 if has_bank_entry else 0,
		})
	

	@frappe.whitelist()
	def make_cash_bank_entry(self):
		self.make_bank_entry("Cash")
		self.make_bank_entry("Bank")
		
	@frappe.whitelist()
	def make_bank_entry(self,jl_type="Cash"):
		conditions = f"where payroll_month = '{self.name}' "
		if jl_type == "Bank" :
			conditions += " and bank_transfer = 1"
		
		if jl_type == "Cash" :
			conditions += " and ifnull(bank_transfer,0) = 0"
		
		salary_query = f"""
						select      
							employee,
							SUM(IFNULL(net_salary,0)) as net_salary ,
							SUM(IFNULL(insurance ,0)) as insurance ,
							SUM(IFNULL(taxes ,0)) as taxes 
						from `tabEmployee Salary`
						{conditions}
						group by employee
					"""
		# frappe.msgprint(salary_query)
		salaries = frappe.db.sql(salary_query,as_dict=1) or []
		if not len(salaries) :
			frappe.msgprint(_(f"Theres is no Salaries to Post {jl_type}"))
			return
		


		company_settings = self.get_company_settings()
		company = frappe.get_doc("Company",company_settings.company)
		je = frappe.new_doc("Journal Entry")
		je.posting_date = nowdate()
		je.voucher_type = f'{jl_type} Entry'
		je.company = company.name
		je.remark = f'Journal Entry against {self.doctype} : {self.name}'
		je.user_remark = _('Bank Entry for salaries from {0} to {1}') \
            .format(self.from_date, self.to_date)
		total_salaries = sum([( salary.net_salary or 0) for salary in salaries])
		# total_insurance = sum([( salary.insurance or 0) for salary in salaries])
		# total_taxes = sum([( salary.taxes or 0) for salary in salaries])
		
		je.append("accounts", {
				"account":  company_settings.cash_payable_account if jl_type != "Bank" else company_settings.bank_payable_account,
				"credit_in_account_currency": flt(total_salaries),
				"reference_type": self.doctype,
				"reference_name": self.name
			})
		

		# if total_insurance :
		# 	je.append("accounts", {
		# 		"account":  company_settings.payroll_insurance_account,
		# 		"debit_in_account_currency": flt(total_insurance),
		# 		"reference_type": self.doctype,
		# 		"reference_name": self.name,
		# 	})


		# if total_taxes :
		# 	je.append("accounts", {
		# 		"account":  company_settings.payroll_tax_account,
		# 		"debit_in_account_currency": flt(total_taxes),
		# 		"reference_type": self.doctype,
		# 		"reference_name": self.name,
		# 	})
		
		for salary in salaries :
			if salary.net_salary :
				je.append("accounts", {
					"account":  company_settings.payroll_salary_account,
					"debit_in_account_currency": flt(salary.net_salary),
					"party_type":"Employee",
					"party":salary.employee,
					"reference_type": self.doctype,
					"reference_name": self.name,
				})

			# if salary.insurance :
			# 	je.append("accounts", {
			# 		"account":  company_settings.payroll_insurance_account,
			# 		"debit_in_account_currency": flt(salary.insurance),
			# 		"party_type":"Employee",
			# 		"party":salary.employee,
			# 		"reference_type": self.doctype,
			# 		"reference_name": self.name,
			# 	})


			# if salary.taxes :
			# 	je.append("accounts", {
			# 		"account":  company_settings.payroll_tax_account,
			# 		"debit_in_account_currency": flt(salary.taxes),
			# 		"party_type":"Employee",
			# 		"party":salary.employee,
			# 		"reference_type": self.doctype,
			# 		"reference_name": self.name,
			# 	})
			# total_salaries += ( salary.net_salary or 0)+ ( salary.insurance or 0)+ ( salary.taxes or 0)






		

		# for i in je.accounts :
		# 	frappe.msgprint(f"account : {i.account} | account_currency : {i.account_currency} | debit_in_account_currency : {i.debit_in_account_currency} | credit_in_account_currency : {i.credit_in_account_currency}")
		je.save()

		lnk = get_link_to_form(je.doctype, je.name)
		frappe.msgprint(_("{} {} was created").format(je.doctype,lnk))
	def get_company_settings(self,company=None):
		company = company or get_default_company()
		
		return frappe.get_doc("Company Accounts",company)


@frappe.whitelist()
def get_employee_salaries(payroll_month):
	payroll_month = frappe.get_doc("Payroll Month" , payroll_month)
	token = get_hr_auth_token()
	server_url = frappe.db.get_single_value("HR Integration Setting","server_url")
	method_url = "/api/ERPsalary"
	url = server_url+method_url
	method = "GET"
	parameters = {
		"YEARID":payroll_month.year_id,
		"MONTHID":payroll_month.month_id,
		"BRCODE":payroll_month.branch_code
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
	salaries_count = 0
	employee_count = 0
	if isinstance(json_response,list):
		# salaries_count = len(json_response)
		for row in json_response :
			doc_props = {
				"doctype" : "Employee Salary",
				"payroll_month":payroll_month.name,
				"month":payroll_month.month,
				"month_id":payroll_month.month_id,
				"year":payroll_month.year,
				"year_id":payroll_month.year_id,
				"employee_code":row.get("Staff_ID"),
				"net_salary":row.get("NetSal") or 0,
				"taxes":row.get("TaxVal") or 0,
				"insurance":row.get("Insurance") or 0,
				"advance":row.get("solfa") or 0,
				"bank_transfer":row.get("BnkTransfer") or 0,
				"bank_account":row.get("Bnk_Acc"),
				"insured":row.get("Insured") or 0,
				"taxable":row.get("Taxable") or 0,
				"bank_name":row.get("Bnk_name") or "",
				"currency":row.get("Cur_name") or "",
				"company_insurance":row.get("InsuranceCompany") or 0,
				"pay_template":str(row.get("PayTemplate_ID") or ""),
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
			
			
			pay_template = doc_props ["pay_template"]
			doc_props ["employee"] = employee
			doc_props ["employee_name"] = employee_name

			document_name = f"{payroll_month.name}-{employee_name}-{pay_template}"
			print("docprops {payment template} => ", doc_props["pay_template"])
			doc = save_doc(doc_props)
			print (" doc. pay_template  " , doc.pay_template)
			print (" doc. name  " , doc.name)
			salaries_count += 1

	frappe.msgprint(_("{} Salaries is Synced , {} Employees is not Found").format(salaries_count,employee_count),_("Done"))




@frappe.whitelist()
def get_month_advance(payroll_month):
	try :
		get_employee_advance(payroll_month)
	except Exception as e:
		frappe.msgprint(f"Employee Advance Error => " + str(e),indicator='red')

	# try :
	get_employee_advance_settlement(payroll_month)
	# except Exception as e:
		# frappe.msgprint(f"Employee Advance Settlement Error => " + str(e),indicator='red')













