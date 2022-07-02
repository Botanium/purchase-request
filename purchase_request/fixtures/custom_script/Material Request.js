
frappe.ui.form.on('Material Request', {
	refresh(frm) {
		frm.add_custom_button("Purchase Request", ()=> {
			frappe.model.open_mapped_doc({
				method: "purchase_request.purchase_request.doctype.purchase_request.purchase_request.create_purchase_request",
				frm: cur_frm
			})
        },"Create")
	}
})