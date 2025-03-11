{
    "name": "Sales Order Approval and Discounts",
    "version": "16.0.1.0.0",
    "depends": ["sale", "account","sale_management","contacts"],
    "author": "Bhargav Bharadiya",
    "category": "Sales",
    "summary": "Extends Sales module with order multi approval workflows and discount logic with the report",
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/sale_order_views.xml",
        "views/loyalty_discount_rule_views.xml",
        "views/res_config_settings_view.xml",
        "wizards/sale_order_reject_wizard.xml",
    ],
    "installable": True,
    "application": True
}