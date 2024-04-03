// Copyright (c) 2022, Dynamic Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on("Integration Api Template", {
  refresh: function (frm) {
    cur_frm.fields_dict["attributes_mapping"].grid.get_field(
      "template"
    ).get_query = function (doc, cdt, cdn) {
      return {
        query:
          "dynamic_integrations.dynamic_integrations.doctype.integration_api_template.integration_api_template.get_item_template",
        filters: {
          document_type: frm.doc.document_type,
          profile: frm.doc.profile,
        },
      };
    };
  },
});
