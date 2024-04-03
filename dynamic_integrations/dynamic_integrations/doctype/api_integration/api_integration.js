// Copyright (c) 2022, Dynamic Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on("Api Integration", {
  setup: function (frm) {
    frm.set_query("profile", function () {
      return {
        filters: {
          active: 1,
        },
      };
    });
    
    frm.set_query("integration_api_template", function () {
      return {
        filters: {
          profile: frm.doc.profile,
          document_type:frm.doc.webhook_doctype
        },
      };
    });
  },
  refresh: function (frm) {
    if (!frm.doc.__islocal) {
      frm.add_custom_button(
        __("Execute"),
        function () {
          frappe.call({
            doc: frm.doc,
            method: "execute",
            freeze: true,
            callback: function (r) {
              // frappe.hide_progress();
              // frappe.msgprint(__("Done"));
              frm.refresh();
            },
          });
        },
        __("Actions")
      );
      frm.add_custom_button(
        __("test hook"),
        function () {
          frappe.call({
            // doc: frm.doc,
            method: "dynamic_integrations.dynamic_integrations.magento.api.post_item_attr",
            args :{
              "api":"customers",
              "parm1":55
            },
            freeze: true,
            callback: function (r) {
              console.log(r)
              // frappe.hide_progress();
              // frappe.msgprint(__("Done"));
              frm.refresh();
            },
          });
        },
        __("Actions")
      );

      
    }
  },
});
