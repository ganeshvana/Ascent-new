# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.translate import _


class Crmtarget(models.Model):

    _name = 'crm.target'
    _description = 'Crm'
    _inherit = ['mail.thread','mail.activity.mixin']

    name = fields.Char(string='Name')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirm', 'Inprogress'),
            ('done', 'Done'),
            ('cancel','Cancelled'),
            ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    from_dates = fields.Date(string='From Date',required=True)
    to_date = fields.Date(string='To Date', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency')
    target_line = fields.One2many('crm.target_line', 'sales_target_id', string="Targets")


   
   

    @api.constrains('target_line')
    def _check_exist_user_in_line(self):
        for target in self:
            exist_user = []
            for line in target.target_line:
                if line.user_id.id in exist_user:
                    raise UserError(_('User should be one per line.'))
                exist_user.append(line.user_id.id)


    def unlink(self):
        for rec in self:
            if self.target_line:
                self.target_line.unlink()
        return super(Crmtarget, self).unlink()


    def action_confirm_transfer(self):
        return self.write({'state': 'done'})



  
class productline(models.Model):
    _name = 'crm.target_line'
    _description = 'Crm'

    

    name = fields.Text(string='Description')
    target = fields.Float(string='Target',store=True)
    target_pass = fields.Char(string='Target Val',store=True)
    actual = fields.Float(string='Actual',compute='_compute_actualvalue')
    percentage = fields.Float(string='Percentage',compute='_compute_percentagesvalue')
    percentage_pass = fields.Float(string='Percentage',compute='_compute_percentagesvalue',store=True,group_operator="avg")

    team_id = fields.Many2one('crm.team','Sales Team')
    actual_pass = fields.Float(string='Actuals',compute='_compute_actualvalue',store=True)
    pending = fields.Float(string='Pending',compute='_compute_actualvalue')
    pending_pass = fields.Float(string='Pending',compute='_compute_actualvalue',store=True)
    sales_target_id = fields.Many2one('crm.target','Targets ')
    user_id = fields.Many2one('res.users', string='Sales Person')
    from_dates_date = fields.Date(string='From Date',compute='_targetvalue_fdate',store=True)
    to_date_dates = fields.Date(string='To Date',compute='_targetvalue_tdate',store=True)




    @api.onchange('user_id')
    def _targetvalue(self):
        for rec in self:
            if rec.user_id:
                rec.team_id = ''
                team_obj = self.env['crm.team'].search([])
                for each in team_obj:
                    for line in each.member_ids:
                        if rec.user_id in line:
                            rec.team_id = each.id                        
            if rec.user_id.target_value:
                rec.target = rec.user_id.target_value
            else:
                rec.target = 0.00


    @api.depends('sales_target_id')
    def _targetvalue_fdate(self):
        for record in self:
            if record.sales_target_id:
                record.from_dates_date = record.sales_target_id.from_dates

    @api.depends('sales_target_id')
    def _targetvalue_tdate(self):
        for record in self:
            if record.sales_target_id:
                record.to_date_dates = record.sales_target_id.to_date

    @api.depends('actual','target')
    def _compute_percentagesvalue(self):
        percentage = 0
        for per in self:
            if per.actual and per.target != 0:
                percentage = (per.actual * 100)/ per.target or 0.00
                per.percentage = percentage
                per.percentage_pass = percentage
            if per.actual == 0:
                per.percentage = 0.00
                per.percentage_pass = 0.00
            if per.target == 0:
                per.percentage = 0.00
                per.percentage_pass = 0.00



    @api.depends('user_id')
    def _compute_actualvalue(self):
        for line in self:
            line.actual = 0
            line.pending = 0
            if line.user_id:
                prob_value = self.env['crm.lead'].search([('user_id', '=', line.user_id.id),('probability', '=',100),('date_closed', '>=',line.sales_target_id.from_dates),('date_closed', '<=',line.sales_target_id.to_date)])
                for rec in prob_value:
                    line.actual += rec.planned_revenue
                    line.actual_pass = line.actual
                if line.actual != 0:
                    line.pending = line.actual - line.target
                    line.pending_pass = line.pending
                else:
                    line.pending = line.pending - line.target
                    line.pending_pass = line.pending




