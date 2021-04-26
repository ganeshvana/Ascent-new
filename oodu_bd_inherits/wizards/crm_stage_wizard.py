# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CrmDropWizard(models.TransientModel):
    _name = 'crm.drop.wizard'
    _description = "Crm drop Wizard"


    reason_drop_id = fields.Many2one('crm.drop', string='Dropped')

    # def action_drop_reason_apply(self):
    #     leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
    #     leads.write({'drop_reason_id' : self.reason_drop_id.id})

    def action_drop_reason_apply(self):
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        return leads.action_set_dropped(drop_reason_id=self.reason_drop_id.id)


class QualifyWizards(models.TransientModel):
    _name = 'crm.qualify.wizards'
    _description = "Crm Qualify Wizards"


    reason_qualify_id = fields.Many2one('crm.qualify', string='Qualified OUT')

    # def action_qualify_reason_apply(self):
    #     if self.reason_qualify_id:
    #         leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
    #         leads.write({'qualify_reason_id' :self.reason_qualify_id.id})

    def action_qualify_reason_apply(self):
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        return leads.action_set_qualified_out(qualify_reason_id=self.reason_qualify_id.id)



class WonWizard(models.TransientModel):
    _name = 'crm.won.wizard'
    _description = "Crm Won Wizard"


    won_id = fields.Many2one('crm.reason', string='Reason For Won')


    def action_won_reason_apply(self):
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        return leads.action_set_won(won_reason_id=self.won_id.id)

class CrmLeadLostInherit(models.TransientModel):
    _inherit = "crm.lead.lost"

    def action_lost_reason_apply(self):
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        return leads.action_set_lost(lost_reason=self.lost_reason_id.id)


    


