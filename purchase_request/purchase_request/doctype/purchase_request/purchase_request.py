# Copyright (c) 2022, Shiela and contributors
# For license information, please see license.txt

import json

import frappe
from frappe import _, msgprint
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cstr, flt, get_link_to_form, getdate, new_line_sep, nowdate
from six import string_types

from erpnext.buying.utils import check_on_hold_or_closed_status, validate_for_items
from erpnext.controllers.buying_controller import BuyingController
from erpnext.manufacturing.doctype.work_order.work_order import get_item_details
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.stock.stock_balance import get_indented_qty, update_bin_qty
from frappe.model.document import Document
from erpnext.stock.doctype.material_request.material_request import set_missing_values, update_item

from datetime import datetime


class PurchaseRequest(Document):
	# pass

	def validate(self):
		self.validate_required_date()

	def validate_required_date(self):
		
		for i in self.items:
			if datetime.strptime(i.schedule_date, "%Y-%m-%d") < datetime.now():
				frappe.throw("Row #{}: Reqd by Date cannot be before Transaction Date".format(i.idx))



	def on_submit(self):
		set_mr_status(self.material_request, 1, 0)



def set_mr_status(mr, has_pr=0, has_po=0):
	status = frappe.db.get_value("Material Request", mr, 'status')
	if has_pr == 1 and has_po == 0:
		status = 'Requested'
	elif has_pr == 1 and has_po == 1:
		status = 'Ordered'
	else: 
		status = frappe.db.get_value("Material Request", mr, 'status')


	frappe.db.set_value("Material Request", mr, "status", status)

@frappe.whitelist()
def create_purchase_order(source, target_doc=None):
	# target_doc = get_mapped_doc("Purchase Request", source,
	# 							{"Purchase Request": {
	# 								"doctype": "Purchase Order",
	# 								"field_map": {
	# 									"purchase_request": "name",
	# 								}
	# 							},
	# 							# "Purchase Order Item": {
	# 							# 	"doctype": "Purchase Order Item",
	# 							# 	"field_map": {
	# 							# 		"material_request_item": "material_request_item"
	# 							# 	}
	# 							# }
	# 							}, target_doc)
	mr = frappe.get_value("Purchase Request", source, "material_request")
	target_doc = create_purchase_request(mr, target_doctype='Purchase Order')

	return target_doc


@frappe.whitelist()
def create_purchase_request_old(source, target_doc=None):
	target_doc = get_mapped_doc("Material Request", source,
								{"Material Request": {
									"doctype": "Purchase Request",
									"field_map": {
										"material_request": "name",
										"transaction_date": "transaction_date",
									}
								},
								"Material Request Item": {
									"doctype": "Purchase Order Item",
									"field_map": {
										"material_request_item": "material_request_item"
									}
								}
								}, target_doc)

	print(target_doc.as_dict())

	return target_doc


@frappe.whitelist()
def create_purchase_request(source_name, target_doc=None, args=None, target_doctype='Purchase Request'):
	print(source_name, target_doc, args)
	if args is None:
		args = {}
	if isinstance(args, string_types):
		args = json.loads(args)

	def postprocess(source, target_doc):
		if frappe.flags.args and frappe.flags.args.default_supplier:
			# items only for given default supplier
			supplier_items = []
			for d in target_doc.items:
				default_supplier = get_item_defaults(d.item_code, target_doc.company).get("default_supplier")
				if frappe.flags.args.default_supplier == default_supplier:
					supplier_items.append(d)
			target_doc.items = supplier_items

		set_missing_values(source, target_doc)

	def select_item(d):
		filtered_items = args.get("filtered_children", [])
		child_filter = d.name in filtered_items if filtered_items else True

		return d.ordered_qty < d.stock_qty and child_filter

	doclist = get_mapped_doc(
		"Material Request",
		source_name,
		{
			"Material Request": {
				"doctype": target_doctype,
				"validation": {"docstatus": ["=", 1], "material_request_type": ["=", "Purchase"]},
			},
			"Material Request Item": {
				"doctype": "Purchase Order Item",
				"field_map": [
					["name", "material_request_item"],
					["parent", "material_request"],
					["uom", "stock_uom"],
					["uom", "uom"],
					["sales_order", "sales_order"],
					["sales_order_item", "sales_order_item"],
				],
				"postprocess": update_item,
				"condition": select_item,
			},
		},
		target_doc,
		postprocess,
	)

	return doclist