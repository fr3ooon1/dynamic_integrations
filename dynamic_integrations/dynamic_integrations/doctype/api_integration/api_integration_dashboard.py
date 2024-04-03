from __future__ import unicode_literals

from frappe import _


def get_data():
	return {
		'fieldname': 'api_integration',
		'non_standard_fieldnames': {
			'Api Integration Log': 'api',
			'Profile Integration Log': 'api',
		},

		'transactions': [
			{
				'label': _('Logs'),
				'items': ['Api Integration Log']
			},
			{
				'label': _('Profile Logs'),
				'items': ['Profile Integration Log']
			},
		]
	}
