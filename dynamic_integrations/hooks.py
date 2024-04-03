from . import __version__ as app_version

app_name = "dynamic_integrations"
app_title = "Dynamic Integrations"
app_publisher = "Dynamic Technology"
app_description = "Dynamic Integrations"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@dynamiceg.com"
app_license = "MIT"
app_logo_url = "/assets/dynamic_integrations/images/dynamic-logo.png"
# Includes in <head>
# ------------------

app_include_css = "/assets/dynamic_integrations/css/dynamic.css"

# include js, css files in header of desk.html
# app_include_css = "/assets/dynamic_integrations/css/dynamic_integrations.css"
# app_include_js = "/assets/dynamic_integrations/js/dynamic_integrations.js"

# include js, css files in header of web template
# web_include_css = "/assets/dynamic_integrations/css/dynamic_integrations.css"
# web_include_js = "/assets/dynamic_integrations/js/dynamic_integrations.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "dynamic_integrations/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "dynamic_integrations.install.before_install"
# after_install = "dynamic_integrations.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "dynamic_integrations.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Cost Center": {
		"on_update": "dynamic_integrations.hr_integration.doc_events.create_cost_center",
		"on_update": "dynamic_integrations.hr_integration.doc_events.update_cost_center"
	},
	"Asset": {
		"on_submit": "dynamic_integrations.hr_integration.doc_events.submit_asset",
	},
	"Asset Movement": {
		"on_submit": "dynamic_integrations.hr_integration.doc_events.submit_asset_movements",
	} ,
	# "Item" :{
	# 	"validate" :"dynamic_integrations.dynamic_integrations.order.validate"
	# },
	# 'Item Price' :{
	# 		"validate" :"dynamic_integrations.dynamic_integrations.order.validate_price"
	# }
	'Sales Order' :{
		# "autoname":"dynamic_integrations.naming.set_sales_order_date"
	}
		 
	
}

# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"dynamic_integrations.tasks.all"
# 	],
	"daily": [
		"dynamic_integrations.cron.delete_logs"
	],
	
# 	"weekly": [
# 		"dynamic_integrations.tasks.weekly"
# 	]
# 	"monthly": [
# 		"dynamic_integrations.tasks.monthly"
# 	]
	"cron": {
		"*/1 * * * *" : [
				"dynamic_integrations.cron.run_api_integration_schedule" 
			],
		# "* */1 * * *" : [
		# 	"dynamic_integrations.cron.get_open_employee_salaries" 
		# ]
	}
}

# Testing
# -------

# before_tests = "dynamic_integrations.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "dynamic_integrations.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "dynamic_integrations.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"dynamic_integrations.auth.validate"
# ]

doctype_list_js = {"Customer" : "public/js/customer_list.js" ,
				   "Item Attribute" : "public/js/item_attribute_list.js" ,
				   "Item" : "public/js/item_list.js" ,
				 	}
domains = {
	'HR Integration':'dynamic_integrations.domains.hr_integrations'
}