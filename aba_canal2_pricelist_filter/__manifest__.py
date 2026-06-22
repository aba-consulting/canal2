{
    "name": "ABA Canal 2 Pricelist Filter",
    "version": "19.0.1.2.0",
    "author": "ABA Consulting",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Filtra listas de precios según si el tipo de pedido es Canal 2",
    "depends": ["sale_order_type", "sale"],
    "data": [
        "views/sale_order_type_view.xml",
        "views/product_pricelist_view.xml",
        "views/sale_order_view.xml",
    ],
    "installable": True,
    "application": False,
}
