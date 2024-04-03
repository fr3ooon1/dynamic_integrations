// Copyright (c) 2022, Dynamic Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Commission', {
	refresh:function(frm){
		if (frm.doc.posted_to_hr ) {
			console.log("Posted")
			frm.set_df_property("open_month", "read_only", 1);
			frm.refresh_fields("open_month")
			frm.set_df_property("start_date", "read_only", 1);
			frm.refresh_fields("start_date")
			frm.set_df_property("end_date", "read_only", 1);
			frm.refresh_fields("end_date")
			frm.set_df_property("get_employee", "read_only", 1);
			frm.refresh_fields("get_employee")
		}
		
		if(! frm.doc.posted_to_hr){
		frm.add_custom_button(
			__("Post"),
			function () {
				frappe.call({
					doc: frm.doc,
					method:"post_to_hr" ,
					//freeze: true,
					callback: function (r) {
						console.log("Sent")
						frappe.msgprint(r.message);
						frm.refresh();
					  },

				})
			}
		)
		}

	},

	validate_dates:function(frm){
		if (frm.doc.start_date && frm.doc.end_date){
			frappe.call({
				doc: frm.doc ,
				method :  "validate_to_date", 
				callback:function(r){
					frm.refresh_fields("start_date")
					frm.refresh_fields("end_date")
				}
			} ,)
		}
	} ,
	start_date :function(frm){
		frm.events.validate_dates(frm)
	},
	end_date :function(frm){
		frm.events.validate_dates(frm)
	},
	validate_input:function(frm){
	// validate  user input required to get Employees 
	frm.clear_table("items")
				frm.refresh_fields("items")
		if(!frm.doc.company){
			frappe.throw("Please Set Company")
		} 
		if (!frm.doc.open_month) {
			frappe.throw("Please Set Open Month")
		}
		if(!frm.doc.start_date || !frm.doc.end_date){
			frappe.throw("Please Set Start and End Date")
		}
		// validate Form Data 
		frappe.call({
			doc: frm.doc ,
			method :  "validate_ui_data",
		
		callback:function(r){
			
			if(r.message) {
				
				console.log(r.message)
				r.message.forEach(element => {
					var row = frm.add_child("items")
					row.employee = element.employee 
					row.start_date = element.start_date
					row.end_date = element.end_date
					row.commission = element.commission
				
				
				}) ;
				frm.refresh_fields("items")

				
			}
		} })
	},

	get_employee: function(frm) {
		frm.events.validate_input(frm)

	}
});
