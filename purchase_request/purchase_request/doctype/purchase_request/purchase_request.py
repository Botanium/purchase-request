# Copyright (c) 2022, Shiela and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class PurchaseRequest(Document):
	pass

@frappe.whitelist()
def create_purchase_order(source, target_doc=None):
	target_doc = get_mapped_doc("Purchase Request", source,
								{"Purchase Request": {
									"doctype": "Purchase Order",
									"field_map": {
										"purchase_request": "name",
									}
								},
								}, target_doc)

	return target_doc