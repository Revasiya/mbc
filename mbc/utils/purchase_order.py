import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils.data import cint, flt



@frappe.whitelist()
def make_sales_order(doc, target_doc=None):
    # This function takes in a Purchase Order name as `source_name`, and an optional target document object `target_doc`

    # Call the `_make_sales_order` function and pass in the `source_name` and `target_doc` arguments
    return _make_sales_order(doc, target_doc)


def _make_sales_order(source_name, target_doc=None, ignore_permissions=False):
    # This is a helper function that creates a Sales Order from a Purchase Order
    
    po = source_name #frappe.get_doc('Purchase Order', source_name)
    customer = frappe.db.get_value('Company', {'name': po.company}, ['mbc_internal_customer'])
    customer_name = frappe.db.get_value('Customer', {'name': customer}, ['customer_name'])
    tax_category = frappe.db.get_value('Customer', {'name': customer}, ['tax_category'])

    # Sales Taxes and Charges Template
    tax_temp_name = frappe.db.get_value('Sales Taxes and Charges Template', {'tax_category': tax_category}, ['name'])

    # get value for mbc_internal_company and mbc_default_po_warehouse
    mbc_internal_company = frappe.db.get_value('Supplier', {'name': po.supplier}, ['mbc_internal_company'])
    mbc_default_po_warehouse = frappe.db.get_value('Supplier', {'name': po.supplier}, ['mbc_default_po_warehouse'])

    # get value for sales payment_terms
    payment_terms = frappe.db.get_value('Customer', {'name': customer}, ['payment_terms'])

    # Get Value for Terms and Conditions
    terms_name = frappe.db.get_value('Terms and Conditions', {'selling': 1, 'disabled': 0}, ['name'])
    terms_description = frappe.db.get_value('Terms and Conditions', {'name': terms_name}, ['terms'])

    #Check Customer outstanding amount against sales invoice status
    outstanding_amount = 0.0
    sales_invoice = frappe.get_all('Sales Invoice', filters={'customer': customer, 'docstatus': 1})
    
    for pe in sales_invoice:
        se = frappe.db.get_value('Sales Invoice', {'name': pe.name}, ['status','grand_total'], as_dict=True)
        if se.status == "Unpaid":
            frappe.msgprint("Customer {0} has an Sales Invoice outstanding amount of {1}. Please settle before creating a sales order.".format(customer_name,se.grand_total))
            return
        elif se.status == "Partly Paid":
            out_std = frappe.db.get_value('Payment Entry Reference', {'parent': pe.name}, ['outstanding_amount'])
            outstanding_amount += out_std
            
    if outstanding_amount > 0.0:
        frappe.msgprint(f"Customer {customer_name} has an outstanding amount of {outstanding_amount}. Please settle before creating a sales order.")
        return
    
    

    # set missing values
    so = frappe.new_doc('Sales Order')
    so.customer = customer
    so.customer_name = customer_name
    so.set_warehouse = mbc_default_po_warehouse
    so.po_no = po.name
    so.po_date = po.transaction_date
    so.company = mbc_internal_company
    so.payment_terms_template = payment_terms
    so.tax_category = tax_category
    so.taxes_and_charges = tax_temp_name
    so.tc_name = terms_name
    so.delivery_date = po.schedule_date
    so.docstatus = 0
    so.inter_company_order_reference = ""
    so.terms = terms_description
    so.flags.ignore_permissions = ignore_permissions
    so.run_method("set_missing_values")
    
    # set Items Table
    for item in po.items:
        if item.qty > 0:
            so_item = so.append('items', {})
            so_item.item_code = item.item_code
            so_item.item_name = item.item_name
            so_item.description = item.description
            so_item.qty = item.qty
            so_item.stock_uom = item.uom
            so_item.price_list_rate = item.rate
            so_item.rate = item.rate
            so_item.amount = flt(item.qty) * flt(item.rate)
            so_item.warehouse = mbc_default_po_warehouse
            so_item.delivery_date = po.schedule_date
            if item.against_blanket_order:
                so_item.against_blanket_order = item.against_blanket_order
                so_item.blanket_order = item.blanket_order
                so_item.blanket_order_rate = item.blanket_order_rate
    
    
    so.set_taxes()
    so.save(ignore_permissions=ignore_permissions)
    frappe.msgprint(msg='Sales Order Created Successfully',
                                title='Message',
                                indicator='green')
   
