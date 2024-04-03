frappe.listview_settings['Courier'] = {

    onload: function(list_view) {
        list_view.page.add_menu_item('Get Updated', () =>
            frappe.call({
                method: 'dynamic_integrations.main_api.get_courier',
                freeze: true,
                callback: function() {
                    list_view.refresh();
                }
            })



        );

    },

};