{
    'name': 'Odoo 14 - Credit Limit Rules',
    'author': 'Norlan Ruiz',
    'category': 'Accounting/Accounting',
    'version': '14.0.1.0.0',
    'description': """Manage Customer Credit Limit Rules""",
    'summary': """Customer Credit Limit Rules""",
    'sequence': 11,
    'website': 'https://github.com/ruiznorlan/addons-ruiznorlan',
    'depends': ['base', 'account', 'sale', 'sale_management'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/credit_limit_rules.xml',
        'views/res_partner.xml',
        'views/sale_order.xml',
        'views/account_move.xml',
        'wizard/credit_limit_summary.xml'
    ],
    'installable': True,
}
