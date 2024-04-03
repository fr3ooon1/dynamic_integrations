frappe.listview_settings['Customer'] = {

	onload: function(list_view) {
        list_view.page.add_menu_item('Get Updated', () => 
        frappe.call({
            method:'dynamic_integrations.main_api.get_customer',
            args :{
                "api":"customers"
              },
              freeze: true,
            callback: function() {
                list_view.refresh();
            }
        })
        
        
        
        );
		
	},

};