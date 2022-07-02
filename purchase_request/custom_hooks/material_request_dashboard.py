from frappe import _


def get_data(data=None):
	return {
		"fieldname": "material_request",
		"transactions": [
			{
				"label": _("Reference"),
				"items": ["Request for Quotation", "Supplier Quotation", "Purchase Request", "Purchase Order"],
			},
			{"label": _("Stock"), "items": ["Stock Entry", "Purchase Receipt", "Pick List"]},
			{"label": _("Manufacturing"), "items": ["Work Order"]},
		],
	}
