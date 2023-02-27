import datetime
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils.data import cint, flt


@frappe.whitelist()
def make_sales_order(source_name, target_doc=None):
    return _make_sales_order(source_name, target_doc)


def _make_sales_order(source_name, target_doc=None, ignore_permissions=False):
    doc = frappe.get_doc('Purchase Order', source_name)
    customer = frappe.db.get_value('Company', {'name': doc.company}, ['mbc_internal_customer'])
    customer_name = frappe.db.get_value('Customer', {'name': customer}, ['customer_name'])
    tax_category = frappe.db.get_value('Customer', {'name': customer}, ['tax_category'])

    # Sales Taxes and Charges Template
    tax_temp_name = frappe.db.get_value('Sales Taxes and Charges Template', {'tax_category': tax_category}, ['name'])

    # get value for mbc_internal_company and mbc_default_po_warehouse
    mbc_internal_company = frappe.db.get_value('Supplier', {'name': doc.supplier}, ['mbc_internal_company'])
    mbc_default_po_warehouse = frappe.db.get_value('Supplier', {'name': doc.supplier}, ['mbc_default_po_warehouse'])

    # get value for sales payment_terms
    payment_terms = frappe.db.get_value('Customer', {'name': customer}, ['payment_terms'])

    # Get Value for Terms and Conditions
    terms_name = frappe.db.get_value('Terms and Conditions', {'selling': 1, 'disabled': 0}, ['name'])
    terms_description = frappe.db.get_value('Terms and Conditions', {'name': terms_name}, ['terms'])

    # set missing values
    def set_missing_values(source, target):
        if customer:
            target.customer = customer
            target.customer_name = customer_name

        target.set_warehouse = mbc_default_po_warehouse
        target.po_no = doc.name
        target.po_date = doc.transaction_date
        target.company = mbc_internal_company
        target.payment_terms_template = payment_terms
        target.tax_category = tax_category
        target.taxes_and_charges = tax_temp_name
        target.tc_name = terms_name
        target.inter_company_order_reference = ""
        target.terms = terms_description
        target.flags.ignore_permissions = ignore_permissions
        target.run_method("set_missing_values")
        target.run_method("calculate_taxes_and_totals")

    # set Items Table
    def update_item(obj, target, source_parent):
        target.warehouse = mbc_default_po_warehouse
        if obj.against_blanket_order:
            target.against_blanket_order = obj.against_blanket_order
            target.blanket_order = obj.blanket_order
            target.blanket_order_rate = obj.blanket_order_rate

    # Doc Data mapped
    doclist = get_mapped_doc(
        "Purchase Order",
        source_name,
        {
            "Purchase Order": {"doctype": "Sales Order", "validation": {"docstatus": ["=", 1]}},
            "Purchase Order Item": {
                "doctype": "Sales Order Item",
                "postprocess": update_item,
                "condition": lambda doc: doc.qty > 0,
            },
            "Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
        },
        target_doc,
        set_missing_values,
        ignore_permissions=ignore_permissions,
    )
    doclist.set_payment_schedule()
    doclist.set_taxes()
    # postprocess: fetch shipping address, set missing values
    doclist.set_onload("ignore_price_list", True)

    return doclist
