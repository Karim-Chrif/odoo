{
    'name': 'Support',
    'version': '1.0',
    'summary': 'Support System for Odoo',
    'description': """
        The Support Ticket System module provides a solution for managing support tickets in Odoo.
    """,
    'author': 'Carim',
    'category': 'Tools',
    'depends': ['base','contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/support_ticket_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}