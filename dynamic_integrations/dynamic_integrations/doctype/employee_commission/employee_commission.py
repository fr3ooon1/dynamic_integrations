# Copyright (c) 2022, Dynamic Technology and contributors
# For license information, please see license.txt

from email import header
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import today
import json
import requests
# import token
from dynamic_integrations.hr_integration.apis import get_hr_auth_token




def get_settings_data():
	token = get_hr_auth_token()
	if token :
		return token
	else :
		return False

class EmployeeCommission(Document):
	def __init__(self ,*args , **kwargs):
		super().__init__(*args , **kwargs)
		self.branch = 0
		
		#self.sales_person = False 
	def validate(self):
		# this validation is not work now 
		self.validate_open_month()
		self.get_sales_employee()
		valid_date = self.validate_to_date()
		if not valid_date :
			frappe.throw("Date Errro")
		#self.post_to_hr()
		if self.posted_date :
			self.posted_to_hr = 1
	@frappe.whitelist()	
	def validate_to_date(self):
		if self.start_date > self.end_date :
			self.start_date ,self.end_date = None , None
			frappe.msgprint(f"""Date Erro start Date {self.start_date} Can
			  not be Grater than End Date {self.end_date}""")
			return False
		if self.end_date > frappe.utils.nowdate() :
			frappe.msgprint(f"Date Erro End Date Can not be Greater that {frappe.utils.nowdate()}")
			return False
		return True
	@frappe.whitelist()	
	def post_to_hr(self):
		#self.validate_open_month()
		token = get_settings_data()
		hr_integration_setting = frappe.get_single("HR Integration Setting")
		url = hr_integration_setting.server_url
		#frappe.throw(str(token))
		end_point = url+ "api/ERPAddPayval"
		header = {
			"Authorization" : f"Bearer {token}" ,
			"Content-Type" : "application/json"
		}
		body = 	[]

		open_month = frappe.get_doc("Payroll Month" , self.open_month)
		# Get body data From child table 
		if self.open_month :
			for employee in self.items :
				data = {
					"staff_ID": str(employee.hr_id) ,
					"elemVal" : employee.commission ,
					"actionUser": "1038",
					"cmp_code": open_month.company_code,
					"br_code": open_month.branch_code,
					"openMonth_ser": open_month.hr_id

				}
				body.append(data)
		
			req = requests.post(end_point, headers=header ,data=json.dumps(body))
			self.posted_to_hr = 1
			
			#frappe.throw(str(end_point))
			if req.status_code == 200 :
				self.posted_to_hr = 1
				self.posted_date = today()
				self.save()
				respons = req.json()
				if respons.get("errormsg") and len(respons.get("errormsg")) > 4 :
					error_message = f"""{respons.get("errormsg")} {respons.get("emplst")}"""
					# frappe.throw(error_message)
				return respons
			if req.status_code != 200 :
				error = req.text
				# frappe.throw( str(req.status_code))
				# frappe.throw("Error")
	@frappe.whitelist()
	def validate_ui_data(self):
		# 1 validate Month Is Open
		self.validate_open_month()
		employees =self.get_sales_employee()
		return employees
		# validate Previous periods Check if Employee as the same period 
	
	def validate_open_month(self):
		#validate if month is open
		
		month = frappe.get_doc("Payroll Month" , self.open_month)
		#self.open_month = month
		open_month = month.open
		#Set Obj Branch 
		self.branch = month.branch
		
		#Stop validation 

		# if not open_month :
		# 	frappe.throw(_("""Please Select Open Month  """))
	def filetr_employee (self ,employees):
		filetr_employee = []
		for employee in employees :
			
			strin = f""" SELECT name FROM `tabEmployee Commission Items` 
					WHERE employee = "{employee.get('employee')}"  and
					start_date BETWEEN  '{self.start_date}'  and '{self.end_date}' 
					OR
					end_date  BETWEEN  '{self.start_date}'  and '{self.end_date}'"""
			if self.name :
				strin = strin + f"""and parent != '{self.name}'"""
			#frappe.throw(strin)
			old_grant = frappe.db.sql(strin,as_dict =1)
			if len(old_grant) > 0  and old_grant[0].get("name"):
				pass
	
			else :
				# calculate_employee Commision From 2 Dates 
				employee_name = employee.get('employee')
				sales_person =  employee.get('person')

				#get Sales Person sales Invocies 
				sum_incentives = frappe.db.sql(f""" 
					SELECT SUM(b.incentives) as commission FROM `tabSales Team` b 
					INNER Join `tabSales Invoice` a ON
					b.parent = a.name
					WHERE b.sales_person ='{sales_person}'
					AND a.docstatus=1 AND a.posting_date  BETWEEN  '{self.start_date}'  
					and '{self.end_date}'
				""" ,as_dict =1)
				line = {
					"employee" :employee_name ,
					"start_date" : self.start_date ,
					"end_date" : self.end_date ,
					"commission" : 0
				} 
				if len(sum_incentives) > 0 and sum_incentives[0].get("commission") :
					line["commission"] = sum_incentives[0].get("commission")
				filetr_employee.append(line)
		if len(filetr_employee) > 0 :
			return filetr_employee
		else :
			pass
	def get_sales_employee(self):
	
		employee = frappe.db.sql(f""" SELECT a.employee as employee  ,a.name as person
			FROM `tabSales Person` a 
			INNER join `tabEmployee` b 
			ON a.employee = b.name 
		  	WHERE a.employee is not null and b.branch ='{self.branch}' 
		  """ , as_dict =1 ) 
		#filetr Employee
		# frappe.throw(str(employee))

		filer_employees = self.filetr_employee(employee)
		# frappe.throw(str(filer_employees))
		return filer_employees
		#Caculate Commetion 

	
	def validate_previous_periods(self):
		pass