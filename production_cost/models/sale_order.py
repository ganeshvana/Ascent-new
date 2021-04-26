# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    entry_count = fields.Integer(string='Entry Count', compute='count_entry')

    @api.model
    def create(self, vals):
        Entry = self.env['product.entry']
        order = super(SaleOrder, self).create(vals)
        entry = Entry.search([('sale_order_id', '=', order.id)], limit=1)
        if not entry:
            Entry.create({'partner_id': order.partner_id.id, 'sale_order_id': order.id})
        return order

    def count_entry(self):
        for order in self:
            entry_ids = self.env['product.entry'].search([('sale_order_id', '=', order.id)])
            order.entry_count = len(entry_ids) if entry_ids else 0

    def view_product_entry(self):
        entry_ids = self.env['product.entry'].search([('sale_order_id', 'in', self.ids)])
        return {
            'name': _('Product Entry'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'product.entry',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', entry_ids.ids)],
        }
