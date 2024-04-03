// Copyright (c) 2022, Dynamic Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on("Company Accounts", {
  // refresh: function(frm) {

  // }
  setup: function (frm) {
    frm.set_query("salary_account", function () {
      return {
        filters: [
          ["company", "=", frm.doc.company],
          ["is_group", "=", 0],
        ],
      };
    });
    frm.set_query("payroll_salary_account", function () {
      return {
        filters: [
          ["company", "=", frm.doc.company],
          ["is_group", "=", 0],
        ],
      };
    });
    frm.set_query("advance_payment_account", function () {
      return {
        filters: [
          ["company", "=", frm.doc.company],
          ["is_group", "=", 0],
        ],
      };
    });
    frm.set_query("employee_advance_account", function () {
      return {
        filters: [
          ["company", "=", frm.doc.company],
          ["is_group", "=", 0],
        ],
      };
    });
    frm.set_query("tax_account", function () {
      return {
        filters: [
          ["company", "=", frm.doc.company],
          ["is_group", "=", 0],
        ],
      };
    });
    frm.set_query("payroll_tax_account", function () {
      return {
        filters: [
          ["company", "=", frm.doc.company],
          ["is_group", "=", 0],
        ],
      };
    });
    frm.set_query("insurance_account", function () {
      return {
        filters: [
          ["company", "=", frm.doc.company],
          ["is_group", "=", 0],
        ],
      };
    });
    frm.set_query("payroll_insurance_account", function () {
      return {
        filters: [
          ["company", "=", frm.doc.company],
          ["is_group", "=", 0],
        ],
      };
    });
    frm.set_query("company_insurances_account", function () {
      return {
        filters: [
          ["company", "=", frm.doc.company],
          ["is_group", "=", 0],
        ],
      };
    });
    frm.set_query("employee_advance_adjustment", function () {
      return {
        filters: [
          ["company", "=", frm.doc.company],
          ["is_group", "=", 0],
        ],
      };
    });
    
    frm.set_query("company_insurances_expense_account", function () {
      return {
        filters: [
          ["company", "=", frm.doc.company],
          ["is_group", "=", 0],
        ],
      };
    });
    frm.set_query("cash_payable_account", function () {
      return {
        filters: [
          ["company", "=", frm.doc.company],
          ["is_group", "=", 0],
        ],
      };
    });

    frm.set_query("bank_payable_account", function () {
      return {
        filters: [
          ["company", "=", frm.doc.company],
          ["is_group", "=", 0],
        ],
      };
    });

    frm.set_query("cost_center", function () {
      return {
        filters: [
          ["company", "=", frm.doc.company],
          ["is_group", "=", 0],
        ],
      };
    });

    frm.set_query("advance_cost_center", function () {
      return {
        filters: [
          ["company", "=", frm.doc.company],
          ["is_group", "=", 0],
        ],
      };
    });
  },

  advance_mode_of_payment: function (frm) {
    get_payment_mode_account(
      frm,
      frm.doc.advance_mode_of_payment,
      function (account) {
        frm.set_value("advance_payment_account", account);
      }
    );
  },
});

var get_payment_mode_account = function (frm, mode_of_payment, callback) {
  if (!frm.doc.company) {
    frappe.throw({
      message: __("Please select a Company first."),
      title: __("Mandatory"),
    });
  }

  if (!mode_of_payment) {
    return;
  }

  return frappe.call({
    method:
      "erpnext.accounts.doctype.sales_invoice.sales_invoice.get_bank_cash_account",
    args: {
      mode_of_payment: mode_of_payment,
      company: frm.doc.company,
    },
    callback: function (r, rt) {
      if (r.message) {
        callback(r.message.account);
      }
    },
  });
};
