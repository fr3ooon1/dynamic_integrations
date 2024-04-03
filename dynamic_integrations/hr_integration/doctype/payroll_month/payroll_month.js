// Copyright (c) 2022, Dynamic Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payroll Month", {
  refresh: function (frm) {
    frm.clear_custom_buttons();
    if (!frm.doc.open) {
      frappe.call({
        method: "has_jl_entries",
        doc: frm.doc,
        callback: function (r) {
          if (r.message) {
            if (!r.message.has_journal_entry) {
              frm.add_custom_button(
                __("Get Employee Salaries"),
                function () {
                  frm.events.get_employees_salaries(frm);
                },
                __("Actions")
              );
              frm.add_custom_button(
                __("Get Employee Advance"),
                function () {
                  frm.events.get_month_advance(frm);
                },
                __("Actions")
              );
              

              frm.add_custom_button(
                __("POST Salaries"),
                function () {
                  frm.events.create_salaries_jl(frm);
                },
                __("Actions")
              );
            } else {
              if (!(r.message.has_bank_entry || r.message.has_cash_entry)) {
                frm.add_custom_button(
                  __("Make Cash and Bank Entry"),
                  function () {
                    frm.events.make_cash_bank_entry(frm);
                  },
                  __("Actions")
                );
              } else if (!r.message.has_cash_entry) {
                frm.add_custom_button(
                  __("Make Cash Entry"),
                  function () {
                    frm.events.create_cash_entry(frm);
                  },
                  __("Actions")
                );
              } else if (!r.message.has_bank_entry) {
                frm.add_custom_button(
                  __("Make Bank Entry"),
                  function () {
                    frm.events.create_bank_entry(frm);
                  },
                  __("Actions")
                );
              }
            }
          }
        },
      });
    }
  },
  create_bank_entry(frm) {
    frappe.call({
      method: "make_bank_entry",
      doc: frm.doc,
      args: {
        jl_type: "Bank",
      },
      freeze: true,
      callback: function (r) {
        frm.refresh();
      },
    });
  },
  create_cash_entry(frm) {
    frappe.call({
      method: "make_bank_entry",
      doc: frm.doc,
      args: {
        jl_type: "Cash",
      },
      freeze: true,
      callback: function (r) {
        frm.refresh();
      },
    });
  },
  make_cash_bank_entry(frm) {
    frappe.call({
      method: "make_cash_bank_entry",
      doc: frm.doc,
      freeze: true,
      callback: function (r) {
        frm.refresh();
      },
    });
  },

  get_employees_salaries(frm) {
    frappe.call({
      method:
        "dynamic_integrations.hr_integration.doctype.payroll_month.payroll_month.get_employee_salaries",
      args: {
        payroll_month: frm.doc.name,
      },
      freeze: true,
      callback: function (r) {
        frm.refresh();
      },
    });
  },

  get_month_advance(frm) {
    frappe.call({
      method:
        "dynamic_integrations.hr_integration.doctype.payroll_month.payroll_month.get_month_advance",
      args: {
        payroll_month: frm.doc.name,
      },
      freeze: true,
      callback: function (r) {
        frm.refresh();
      },
    });
  },
  
  create_salaries_jl(frm) {
    frappe.call({
      method: "create_salaries_jl",
      doc: frm.doc,
      freeze: true,
      callback: function (r) {
        frm.refresh();
      },
    });
  },
});
