
frappe.ui.form.on('Material Request', {
	refresh(frm) {
	    console.log("sadsa")
		frm.add_custom_button("Purchase Request", ()=> {

        },"Create")
	}
})