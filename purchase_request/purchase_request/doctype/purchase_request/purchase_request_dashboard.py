from frappe import _


def get_data():
	return {
		"fieldname": "purchase_request",
		'transactions': [
			{
				'label': _('Related'),
				'items': [
					"Purchase Order",
					"Material Request"
				]
			}
		]
	}
