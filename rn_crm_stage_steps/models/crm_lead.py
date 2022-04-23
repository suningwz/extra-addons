# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from cgitb import html
import logging

from odoo import api, fields, models, tools, SUPERUSER_ID

_logger = logging.getLogger(__name__)


class Lead(models.Model):
    _inherit = 'crm.lead'

    def _compute_html(self):
        for record in self:
            if len(record.todo_ids) > 0:
                complete = 0
                not_complete = 0
                for todo_list in record.todo_ids:
                    if todo_list.ready:
                        complete += 1
                    else:
                        not_complete += 1
                
                total = complete + not_complete
                percent_ready = round(complete / total * 100, 2)
                html_string = ""
                html_string += '<div class="card">'
                html_string += '<div class="card-body">'
                
                html_string += f'<h1 class="card-title">STAGE: {record.stage_id.name}</h1>'
                html_string += f'<p class="card-text">{record.stage_id.html_stage_description}</p>'
                
                html_string += '<br/>'
    
                html_string += '<div class="progress">'
                html_string += f'<div class="progress-bar" role="progressbar" style="width: {percent_ready}%;" aria-valuenow="{percent_ready}" aria-valuemin="0" aria-valuemax="100">{percent_ready}%</div>'
                html_string += '</div>'

                html_string += '</div>'
                html_string += '</div>'
                record.html_progress_lead = html_string
            else:
                html_string = ""
                html_string += '<div class="card">'
                html_string += '<div class="card-body">'
                
                html_string += f'<h1 class="card-title">STAGE: {record.stage_id.name}</h1>'
                html_string += f'<p class="card-text">{record.stage_id.html_stage_description}</p>'
                
                html_string += '<br/>'
    
                html_string += '<div class="progress">'
                html_string += f'<div class="progress-bar" role="progressbar" style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>'
                html_string += '</div>'

                html_string += '</div>'
                html_string += '</div>'
                record.html_progress_lead = html_string

    html_progress_lead = fields.Html(string='CRM Lead Summary', compute=_compute_html)

    def _compute_progress(self):
        for record in self:
            if len(record.todo_ids) > 0:
                complete = 0
                not_complete = 0
                for todo_list in record.todo_ids:
                    if todo_list.ready:
                        complete += 1
                    else:
                        not_complete += 1
                total = complete + not_complete
                record.progress_calc = round(complete / total * 100, 2)
            else:
                record.progress_calc = 0.0
    progress_calc = fields.Float(string="Progress", compute=_compute_progress)

    todo_ids = fields.One2many('crm.lead.line', 'lead_id', string='TODO List')


    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        stages = self.env['crm.stage'].sudo().search([])

        todo_list = []
        for stage in stages:
            if len(stage.todo_ids) > 0:
                for todo in stage.todo_ids:
                    values = (0, 0, {
                        'lead_id': res.id,
                        'stage_id': stage.id,
                        'name': todo.name,
                        'description': todo.description
                    })
                    todo_list.append(values)
        res.sudo().write({'todo_ids': todo_list})
        return res

    def action_get_todo_list(self):
        for record in self:
            stages = self.env['crm.stage'].sudo().search([])

            todo_list = []
            for stage in stages:
                if len(stage.todo_ids) > 0:
                    for todo in stage.todo_ids:
                        values = (0, 0, {
                            'lead_id': record.id,
                            'stage_id': stage.id,
                            'name': todo.name,
                            'description': todo.description
                        })
                        todo_list.append(values)

            if len(record.todo_ids) > 0:
                body = ""
                body += "<h5>TODO List: Updated</h5>"
                body += "<br/>"
                body += '<table class="table table-striped">'
                body += '<thead>'
                body += '<tr>'
                body += '<th scope="col">Name</th>'
                body += '<th scope="col">Description</th>'
                body += ' <th scope="col">Status</th>'
                body += '</tr>'
                body += ' </thead>'
                body += '<tbody>'
                for todo in record.todo_ids:
                    body += '<tr>'
                    body += f'<td>{todo.name}</td>'
                    body += f'<td>{todo.description}</td>'
                    body += f'<td>{todo.task_state}</td>'
                    body += '</tr>'
                
                body += '</tbody>'
                body += '</table>'
                record.message_post(body=body)
                record.sudo().write({'todo_ids': False})
            record.sudo().write({'todo_ids': todo_list})

class LeadTodo(models.Model):
    _name = "crm.lead.line"
    _description = "TODO List"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    lead_id = fields.Many2one('crm.lead', string='CRM Lead')
    stage_id = fields.Many2one('crm.stage', string='Stage')
    name = fields.Char(required=True)
    description = fields.Char(required=True)
    ready = fields.Boolean('Ready', default=False)
    task_state = fields.Selection([('todo', 'TODO'),
                                   ('process', 'PROCESS'),
                                   ('done', 'DONE')], default='todo')

    @api.onchange('task_state')
    def _onchange_phone_validation(self):
        if self.task_state == 'done':
            self.ready = True
        else:
            self.ready = False

