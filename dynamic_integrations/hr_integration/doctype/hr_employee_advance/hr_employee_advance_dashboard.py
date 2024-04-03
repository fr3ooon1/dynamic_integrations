
from frappe import _


def get_data():
    return {
        'fieldname': 'hr_employee_advance',
        'non_standard_fieldnames': {
            'Journal Entry': 'reference_name',
        },
        'transactions': [
            {
                'label': _('Settlements'),
                'items': ['HR Employee Advance Settlement']
            },
            {
                'label': _('Accounting'),
                'items': ['Journal Entry']
            },


        ]
    }
