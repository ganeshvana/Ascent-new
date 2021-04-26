from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError,Warning
import time
from datetime import datetime
# from datetime import datetime
# from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class CReason(models.Model):
    _name = "crm.reason"
    _description = "Crm Reason Won"

    name = fields.Char('Won Reason', required=True, translate=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
        ]



class CrmLeadInherits(models.Model):
    _inherit = 'crm.lead'

    def copy(self,default=None):
        res = super(CrmLeadInherits, self).copy(default=None)
        flag = self.env['res.users'].has_group('oodu_bd_inherits.group_disable_action_menu')
        if flag:
            raise UserError('Your Not allowed to duplicate')
        return res
        
    partner_id = fields.Many2one('res.partner', string='Customer', tracking=10, index=True,
         help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")
    alias_name = fields.Char('Alias Name')
    won_reason_id = fields.Many2one('crm.reason','Won Reason',index=True, tracking=True)
    customer_id = fields.Char('Customer ID',compute='_customerref',readonly=True)
    oppurtunity = fields.Char(string='Oppurtunity ID')
    tenture_of_contract = fields.Integer('Tenure of contract')
    no_of_employees = fields.Integer('No.of Employees')
    no_of_locations = fields.Integer('No.of locations')
    contract_entity_id = fields.Many2one('crm.lead.contract.entity',string='Ascent Contract Entity')
    delivering_entity_id = fields.Many2one('crm.lead.delivering.entity',string='Ascent Delivering Unit')
    category_id = fields.Many2one('crm.category',string='Company Category')
    weighted_revenue = fields.Float('Weighted Value',currency_field='company_currency',compute='_compute_weighted',store=True)
    services_id = fields.Many2one('crm.services',string='Opportunity', required=True)

    drop_reason_id = fields.Many2one('crm.drop', string='Drop Reason', index=True, tracking=True)
    # won_reason_id = fields.Many2one('crm.reason.won', string='Won Reason', index=True, tracking=True)
    qualify_reason_id = fields.Many2one('crm.qualify', string='Qualify Reason', index=True, tracking=True)
    opportunity_type_id = fields.Many2one('crm.opportunity.type', string='Opportunity Type')
    industry_id = fields.Many2one('res.partner.industry', string='Industry/Sector',readonly=True)
    competition_primary_id = fields.Many2one('crm.competition', string='Competition')
    competition_secondary_id = fields.Many2one('crm.competition', string='Competition')
    competition_others_id = fields.Many2one('crm.competition', string='Competition')

    # customer_contracting_entity_id = fields.Many2one('res.partner', string="Customer Contracting Entity")
    customer_contracting_entity = fields.Char(string="Customer Contracting Entity")
    planned_revenue = fields.Monetary('Total Value', currency_field='company_currency', tracking=True)
    date_deadline = fields.Date('Expected Closing',help="Estimate of the date on which the opportunity will be won.")
    date_end = fields.Date('Date Closing',default=fields.Date.today())
    won_status = fields.Selection([
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('pending', 'Pending'),
        ('dropped', 'Dropped'),
        ('qualified', 'Qualified Out'),
    ], string='Is Won', compute='_compute_won_status', store=True)

    @api.depends('active', 'probability','lost_reason','drop_reason_id','qualify_reason_id')
    def _compute_won_status(self):
        for lead in self:
            if lead.active and lead.probability == 100:
                lead.won_status = 'won'
            elif not lead.active and lead.lost_reason:
                lead.won_status = 'lost'
            elif not lead.active and lead.drop_reason_id:
                lead.won_status = 'dropped'
            elif not lead.active and lead.qualify_reason_id:
                lead.won_status = 'qualified'
            else:
                lead.won_status = 'pending'


    def action_set_won(self, **additional_values):
        """ Won semantic: probability = 100 (active untouched) """
        for lead in self:
            stage_id = lead._stage_find(domain=[('is_won', '=', True)])
            lead.write({'stage_id': stage_id.id, 'probability': 100,  **additional_values})
        self._rebuild_pls_frequency_table_threshold()
        return True

    def action_set_dropped(self, **additional_values):
        """ Won semantic: probability = 100 (active untouched) """
        for lead in self:
            stage_id = lead._stage_find(domain=[('dropped', '=', True)])
            lead.write({'active': False, 'stage_id': stage_id.id, 'probability': 0,  **additional_values})
        self._rebuild_pls_frequency_table_threshold()
        return True

    def action_set_qualified_out(self, **additional_values):
        """ Won semantic: probability = 100 (active untouched) """
        for lead in self:
            stage_id = lead._stage_find(domain=[('dropped', '=', True)])
            lead.write({'active': False, 'stage_id': stage_id.id, 'probability': 0,  **additional_values})
        self._rebuild_pls_frequency_table_threshold()
        return True

    def action_set_lost(self, **additional_values):
        """ Lost semantic: probability = 0 or active = False """
        for lead in self:
            stage_id = lead._stage_find(domain=[('lost', '=', True)])
            lead.write({'active': False, 'stage_id': stage_id.id, 'probability': 0, **additional_values})
        self._rebuild_pls_frequency_table_threshold()
        return True

    # def action_set_lost(self, **additional_values):
    #     """ Lost semantic: probability = 0 or active = False """
    #     for lead in self:
    #         stage_id = lead._stage_find(domain=[('lost', '=', True)])
    #         result = lead.write({'active': False, 'stage_id': stage_id.id,'probability': 0, **additional_values})
    #     self._rebuild_pls_frequency_table_threshold()
    #     return result

    # def action_set_lost(self, **additional_values):
    #     """ Lost semantic: probability = 0 or active = False """
    #     for lead in self:
    #         stage_id = lead._stage_find(domain=[('lost', '=', True)])
    #         result = lead.write({'active': False, 'probability': 0, **additional_values})
    #     self._rebuild_pls_frequency_table_threshold()
    #     return result




    @api.depends('planned_revenue','probability')
    def _compute_weighted(self):
        for rec in self:
            rec.weighted_revenue = rec.planned_revenue * rec.probability / 100


    @api.onchange('stage_id')
    def _onchange(self):
        prob = 0.0
        prob_value = 0.0
        if self.stage_id:
            prob = self.probability
            prob_value = self.stage_id.probability_value
            # if prob > prob_value:
            #     raise UserError(_("You can't move backward."))
            if self.drop_reason_id:
                raise UserError(_("Pipeline is Dropped,you cannot move further!."))
            # if self.qualify_reason_id:
            #     raise UserError(_("Pipeline is Qualified Out,you cannot move further!."))
            self.probability = prob_value
            # if self.name:
            #     return {'warning': {
            #             'title': _("Warning"),
            #             'message': ('Are you sure you want to move to next stage')}}

    @api.onchange('probability')
    def _prob(self):
        if self.probability:
            self.prob = self.probability


    def _onchange_compute_probability(self, optional_field_name=None):
        """Recompute probability on onchange methods of :
            'stage_id', 'team_id', 'tag_ids'
            'country_id', 'state_id', 'phone_state', 'email_state', 'source_id' """
        if optional_field_name and optional_field_name not in self._pls_get_safe_fields():
            return
        lead_probabilities = self._pls_get_naive_bayes_probabilities()
        if self.id in lead_probabilities:
            self.automated_probability = lead_probabilities[self.id]
            # if self._origin.is_automated_probability:
                # self.probability = self.automated_probability


    @api.onchange('partner_id')
    def _customerref(self):
        if self.partner_id:
            self.customer_id = self.partner_id.ref
            self.industry_id = self.partner_id.industry_id
        if self.partner_id.company_name:
            self.alias_name = self.partner_id.company_name
        else:
            self.alias_name = ''

    @api.onchange('services_id')
    def _services(self):
        if self.services_id:
            self.name = self.services_id.name

    @api.onchange('date_deadline')
    def _onchange_date(self):
        if self.date_deadline:
            today = self.date_deadline
            if today < self.date_end:
                self.date_deadline = self.date_end


class ContractEntity(models.Model):
    _name = "crm.lead.contract.entity"
    _description = "Lead Contract Entity"

    name = fields.Char('Lead Contract Entity', required=True, translate=True)
    more_details = fields.Char('More Details')
    lead_ids = fields.One2many('crm.lead', 'contract_entity_id', string='Contract Entity')


    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]

class deliveringEntity(models.Model):
    _name = "crm.lead.delivering.entity"
    _description = "Lead delivering Entity"

    name = fields.Char('Lead Delivering Entity', required=True, translate=True)
    more_details = fields.Char('More Details')
    del_ids = fields.One2many('crm.lead', 'delivering_entity_id', string='delivering Entity')


    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]

class LeadCategory(models.Model):
    _name = "crm.category"
    _description = "Crm category"

    name = fields.Char('category', required=True, translate=True)
    more_details = fields.Char('More Details')
    category_ids = fields.One2many('crm.lead', 'category_id', string='category')


    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]

class Services(models.Model):
    _name = "crm.services"
    _description = "Crm Services"

    name = fields.Char('Services', required=True, translate=True)
    more_details = fields.Char('More Details')
    services_ids = fields.One2many('crm.lead', 'category_id', string='Services')


    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]


class CrmDrop(models.Model):
    _name = "crm.drop"
    _description = "Crm Drop"

    name = fields.Char('Drop', required=True, translate=True)
    # drop_ids = fields.One2many('crm.drop.wizard', 'reason_drop_id', string='Drop Reason')


    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]


class Crmqualify(models.Model):
    _name = "crm.qualify"
    _description = "Crm qualify"

    name = fields.Char('Qualify', required=True, translate=True)
    # qualify_ids = fields.One2many('crm.qualify.wizards','reason_qualify_id', string='Qualify Reason')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]


class CrmOpportunityType(models.Model):
    _name = "crm.opportunity.type"
    _description = "Crm Opportunity Type"

    name = fields.Char('Opportunity Type', required=True, translate=True)
    more_details = fields.Char('More Details')
    opportunity_ids = fields.One2many('crm.lead', 'opportunity_type_id', string='Opportunity')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
        ]


class CrmCompetition(models.Model):
    _name = "crm.competition"
    _description = "Crm Opportunity Type"

    name = fields.Char('Competition', required=True, translate=True)
    more_details = fields.Char('More Details')
    # competition_ids = fields.One2many('crm.lead', 'competition_id', string='Competition')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
        ]


class ResUsersInherit(models.Model):
    _inherit = "res.users"

    target_value = fields.Float("Target Value")


class ResPartner(models.Model):
    _inherit = "res.partner"

    team_id = fields.Many2one('crm.team','Sales Team')
    # alias_name = fields.Char('Alias Name')



class StageInherit(models.Model):
    _inherit = "crm.stage"

    probability_value = fields.Float('Probability Value')
    dropped = fields.Boolean('Dropped')
    qualified_out = fields.Boolean('Qualified Out')
    lost = fields.Boolean('Lost')


class MergeOpportunityCC(models.TransientModel):
    
    _inherit = 'crm.merge.opportunity'

    def action_merge(self):
        res = super(MergeOpportunityCC, self).action_merge()

        flag = self.env['res.users'].has_group('oodu_bd_inherits.group_disable_action_menu')
        if flag:
            raise UserError('Your Not allowed to Merge')

        return res


class Lead2OpportunityMassConvertInherit(models.TransientModel):

    _inherit = 'crm.lead2opportunity.partner.mass'

    def  mass_convert(self):
        res = super(Lead2OpportunityMassConvertInherit, self).mass_convert()
        user = self.env['res.users'].has_group('oodu_bd_inherits.group_disable_action_menu')
        if user:
            raise UserError('Your Not allowed to Convert')
        return res

class MailComposerInherit(models.TransientModel):
   
    _inherit = 'mail.compose.message'

    def  action_send_mail(self):
        res = super(MailComposerInherit, self).action_send_mail()
        flag = self.env['res.users'].has_group('oodu_bd_inherits.group_disable_action_menu')
        if flag:
            raise UserError('Your Not allowed to send mail')
        return res


class SendSMSInherit(models.TransientModel):
    _inherit = 'sms.composer'

    def  action_send_sms(self):
        res = super(SendSMSInherit, self).action_send_sms()
        flag = self.env['res.users'].has_group('oodu_bd_inherits.group_disable_action_menu')
        if flag:
            raise UserError('Your Not allowed to send sms')
        return res


    def  action_send_sms_mass_now(self):
        res = super(SendSMSInherit, self).action_send_sms_mass_now()
        flag = self.env['res.users'].has_group('oodu_bd_inherits.group_disable_action_menu')
        if flag:
            raise UserError('Your Not allowed to send sms')
        return res
        

class ResPartnerInherits(models.Model):
    _inherit = 'res.partner'

    ref = fields.Char(string='Reference', index=True, default=lambda self: _('#'))

    @api.model
    def create(self, vals):
        if vals.get('company_type') == 'company':
            if vals.get('ref', _('#')) == _('#'):
                vals['ref'] = self.env['ir.sequence'].next_by_code('res.partner')
        if vals.get('is_company') == True:
            if vals.get('ref', _('#')) == _('#'):
                vals['ref'] = self.env['ir.sequence'].next_by_code('res.partner')
        return super(ResPartnerInherits, self).create(vals)






