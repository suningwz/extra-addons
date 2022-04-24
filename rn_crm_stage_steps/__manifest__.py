{
    "name": "CRM Stage Steps",
    "summary": "CRM Stage Steps",
    "version": "15.0.1.0.1",
    'author': "Norlan Ruiz",
    'website': 'https://github.com/ruiznorlan/extra-addons',
    'license': "LGPL-3",
    "category": "Sales/CRM",
    'sequence': 15,
    'images': ['static/description/images/odoo_icon.png'],
    "depends": ["crm"],
    "data": [
        'security/ir.model.access.csv',
        'views/crm_lead_views.xml',
        'views/crm_stage_views.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
