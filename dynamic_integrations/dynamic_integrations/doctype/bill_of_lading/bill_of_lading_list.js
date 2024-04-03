frappe.listview_settings['Bill of lading'] = {

    onload: function(list_view) {

        list_view.page.add_menu_item('Get Updated', () =>
            console.log("hello")
            // frappe.call({
            //     method: 'dynamic_integrations.main_api.get_courier',
            //     freeze: true,
            //     callback: function() {
            //         list_view.refresh();
            //     }
            // })



        );

    },

};