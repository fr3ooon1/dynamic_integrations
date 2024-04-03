import frappe
from frappe.model.naming import make_autoname
from frappe.model.naming import getseries


@frappe.whitelist()
def set_sales_order_date(self, *args, **kwargs):
    if getattr(self, 'remote_id', None):
        self.name = str(self.remote_id) + str(self.customer)
    else:
        date = str(self.transaction_date).split('-')
        prfix = 'SAL-ORD-{}'.format(str(date[1]))
        self.name = prfix + getseries(prfix, 4)
