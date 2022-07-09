import frappe 


def set_material_request_item(doc, method): 
    for i in doc.items:
        i.material_request_item = i.name