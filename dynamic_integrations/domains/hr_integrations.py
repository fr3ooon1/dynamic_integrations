from __future__ import unicode_literals

data = {

    'custom_fields': {
          "Target Detail" :[
             {
                "fieldname": "commission_template",
                "fieldtype": "Link",
                "insert_after": "distribution_id",
                "label": "Commission Template",
                "in_global_search": 1,
                "in_standard_filter": 1,
                "options" :"Commission Template" , 
                "in_preview": 1,
            },
        ]
        # 'Company': [
        #     {
        #         "fieldname": "device_log",
        #         "fieldtype": "Link",
        #         "insert_after": "log_type",
        #         "label": "Log",
        #         "options": "Device Log",
        #         "read_only":1
        #     }
        # ]


    },
    "properties": [{
        "doctype": "Cost Center",
        "doctype_or_field": "DocField",
        "fieldname": "parent_cost_center",
        "property": "reqd",
        "property_type": "Check",
        "value": "0"
    },
    {
        "doctype": "Journal Entry Account",
        "doctype_or_field": "DocField",
        "fieldname": "reference_type",
        "property": "options",
        "property_type": "Text",
        "value": "\nSales Invoice\nPurchase Invoice\nJournal Entry\nSales Order\nPurchase Order\nExpense Claim\nAsset\nLoan\nPayroll Entry\nEmployee Advance\nExchange Rate Revaluation\nInvoice Discounting\nFees\nPay and Receipt Document\nComparison\nClearance\nTender\nPayroll Month\nHR Employee Advance\nHR Employee Advance Settlement"
    }],
    "property_setters": [

    ],
    'on_setup': 'dynamic_integrations.hr_integration.setup.setup'
}
