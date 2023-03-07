frappe.ui.form.on('Purchase Order', {
    before_save:function (frm) {
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                'doctype': 'Supplier',
                'filters': { 'name': frm.doc.supplier },
                'fieldname': [
                    'mbc_internal_company'
                ]
            },
            callback: function (s) {
                if (!s.message.mbc_internal_company) {
                    msgprint('MBC Internal Company is not found in Supplier');
                    // frappe.validated = false;
                }
            }
        });
    }
});

frappe.ui.form.on('Purchase Order',{
    before_save:function (frm) {
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                'doctype': 'Supplier',
                'filters': { 'name': frm.doc.supplier },
                'fieldname': [
                    'mbc_default_po_warehouse'
                ]
            },
            callback: function (s) {
                if (!s.message.mbc_default_po_warehouse) {
                    msgprint('MBC Default PO Warehouse is not found in Supplier');
                    // frappe.validated = false;
                }
            }
        });
    }
});

frappe.ui.form.on('Purchase Order',{
    before_save:function (frm) {
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                'doctype': 'Company',
                'filters': { 'name': frm.doc.company },
                'fieldname': [
                    'mbc_internal_customer'
                ]
            },
            callback: function (s) {
                if (!s.message.mbc_internal_customer) {
                    msgprint('MBC Internal Customer is not found in Company');
                    // frappe.validated = false;
                }
            }
        });
    }
});
