
from frappe import _


def get_data():
	return {
		'fieldname': 'payroll_month',
		'non_standard_fieldnames': {
			'Employee Salary': 'payroll_month',
			'Journal Entry': 'reference_name',
		},
		'transactions': [
			{
				'label': _('Salaries'),
				'items': ['Employee Salary']
			},
			{
				'label': _('Employee Advances'),
				'items': ['HR Employee Advance' , 'HR Employee Advance Settlement' ]
			},
			{
				'label': _('Accounting'),
				'items': ['Journal Entry']
			},


		]
	}
