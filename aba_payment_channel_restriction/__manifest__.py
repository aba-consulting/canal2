{
    "name": "ABA Payment Channel Restriction",
    "version": "18.0.1.0.0",
    "author": "ABA Consulting",
    "license": "LGPL-3",
    "category": "Accounting",
    "summary": "Restringe diarios de cobro según diario de facturación CANAL2",
    "depends": ["account", "account_payment_pro", "sale_order_type", "account_payment_pro_receiptbook"],
    "data": [
        "views/account_journal_view.xml",
        "views/account_move_view.xml",
        "views/account_payment_receiptbook_view.xml",
        "views/account_payment_view.xml",
    ],
    "installable": True,
    "application": False,
}
