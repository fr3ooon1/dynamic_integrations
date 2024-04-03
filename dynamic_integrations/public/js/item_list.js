frappe.listview_settings['Item'] = {

    onload: function(list_view) {
        list_view.page.add_menu_item('Get Updated', () =>
            frappe.call({
                method: 'dynamic_integrations.main_api.post_item',
                args: {
                    "api": "products",
                    "method": "post",
                    "doctype": "Item"
                },
                freeze: true,
                callback: function() {
                    list_view.refresh();
                }
            })



        );

    },

};