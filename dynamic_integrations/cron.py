from dynamic_integrations.hr_integration.doctype.payroll_month.payroll_month import get_employee_salaries
from dynamic_integrations.utils import create_error
import frappe



@frappe.whitelist()
def run_api_integration_schedule():
	doctype = "Api Integration"
	sql = f"""
	select row.name from `tab{doctype}` row where ifnull(row.enabled,0) <> 0
	and  ifnull(row.next_execution_date,CURRENT_TIMESTAMP()) <= CURRENT_TIMESTAMP()
	"""
	# frappe.msgprint(sql)
	doc_list = frappe.db.sql_list(sql)
	for docname in doc_list :
		try : 
			doc = frappe.get_doc(doctype,docname)
			doc.execute()
		except Exception as e:
			create_error(e)
		# doc.save()






@frappe.whitelist()
def get_open_employee_salaries():
	doctype = "Payroll Month"
	sql = f"""
	select row.name from `tab{doctype}` row where ifnull(row.open,0) <> 0
	"""
	# frappe.msgprint(sql)
	doc_list = frappe.db.sql_list(sql)
	for docname in doc_list :
		try :
			get_employee_salaries(docname)
		except Exception as e:
			create_error(e)
		# doc.save()








@frappe.whitelist()
def delete_logs():
	frappe.db.sql(f"""
		delete from `tabApi Integration Log`
		where creation < DATE_SUB(CURDATE(), INTERVAL 4 DAY)
	""")
	frappe.db.sql(f"""
		delete from `tabProfile Integration Log`
		where creation < DATE_SUB(CURDATE(), INTERVAL 4 DAY)
	""")
	frappe.db.commit()
