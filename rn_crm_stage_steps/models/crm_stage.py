# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Stage(models.Model):
    _inherit = 'crm.stage'

    html_stage_description = fields.Html(string='CRM Lead Summary')
    todo_ids = fields.One2many('crm.stage.line', 'stage_id', string='TODO List')


class StageTodo(models.Model):
    _name = "crm.stage.line"
    _description = "TODO List"
    _order = "sequence, id"
    _check_company_auto = True

    sequence = fields.Integer(default=10)
    stage_id = fields.Many2one('crm.stage',
                               string='CRM Stage',
                               index=True,
                               required=True,
                               readonly=True,
                               auto_join=True,
                               ondelete="cascade",
                               check_company=True)
    name = fields.Char(required=True)
    description = fields.Char(required=True)
