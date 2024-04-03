frappe.listview_settings['Item Attribute'] = {

	onload: function(list_view) {
        list_view.page.add_menu_item('Get Updated', () => 
        frappe.call({
            method:"dynamic_integrations.main_api.item_attribute_sync" ,
            args :{
                "api":"attributes" ,
                "method" :"post" , 
                "doctype" : "Item Attribute"
              },
              freeze: true,
            callback: function() {
                list_view.refresh();
            }
        })
        
        
        
        );
		
	},

};

// "dynamic_integrations.dynamic_integrations.main_api.item_attribute_sync" 
// 'dynamic_integrations.dynamic_integrations.magento.api.post_item_attr'