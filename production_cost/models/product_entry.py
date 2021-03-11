# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError

class ProductEntry(models.Model):
    _name = 'product.entry'
    _description = "Product Entry"

    @api.depends('cost_lines', 'order_line')
    def final_material_cost(self):
        for entry in self:
            entry.final_cost = entry.total_material_cost + sum(entry.mapped('cost_lines').mapped('total'))

    @api.depends('order_line')
    def all_material_cost(self):
        for entry in self:
            entry.total_material_cost = sum(entry.mapped('order_line').mapped('material_cost'))

    name = fields.Char('Name', default='New')
    partner_id =  fields.Many2one('res.partner')
    product_id =  fields.Many2one('product.product')
    product_uom_qty =  fields.Float(string='Quantity', digits='Product Unit of Measure', default=1.0)
    product_uom_id =  fields.Many2one('uom.uom', related='product_id.uom_id')
    total_material_cost = fields.Float(string='Total Material Cost', digits='Product Price', default=0.0, compute='all_material_cost', store=True)
    final_cost = fields.Float(string='Final Cost', digits='Product Price', default=0.0, compute='final_material_cost')
    order_line = fields.One2many('product.entry.line', 'entry_id')
    cost_lines = fields.One2many('product.entry.cost', 'entry_cost_id')
    sale_order_id = fields.Many2one('sale.order')
    state = fields.Selection([('draft', 'Draft'), ('validate', 'Validated'), ('compute', 'Computed'),('cancel', 'Cancelled')], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3, default='draft')

    def action_validate(self):
        for order in self:
            order.state = 'validate'

    def action_cancel(self):
        for order in self:
            order.state = 'cancel'

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('product_entry') or '/'
        vals['name'] = name
        return super(ProductEntry, self).create(vals)

    def compute_amount(self):
        for entry in self.filtered(lambda x:x.sale_order_id):
            lines = entry.sale_order_id.mapped('order_line').filtered(lambda x:x.product_id == entry.product_id)
            if not lines:
                raise UserError(_('No such product find in order lines'))
            if not all(lines.filtered(lambda x: x.state == 'draft')):
                raise UserError(_('You can not update price of order in confirm state'))
            lines.write({'price_unit': entry.final_cost})
            entry.state = 'compute'

class ProductEntryLine(models.Model):
    _name = 'product.entry.line'
    _description = "Product Entry Line"

    @api.depends('price_unit', 'product_uom_qty', 'weight')
    def get_material_cost(self):
        for line in self:
            line.material_cost = line.price_unit * line.product_uom_qty * line.weight

    @api.onchange('product_id')
    def onchange_unit_cost(self):
        if self.product_id:
            self.weight = self.product_id.weight if self.product_id.weight else 1.0
            self.price_unit = self.product_id.standard_price if self.product_id.standard_price else 0.0

    sequence = fields.Integer(string='Sequence', default=10)
    entry_id = fields.Many2one('product.entry')
    product_id = fields.Many2one('product.product')
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', default=1.0)
    product_uom_id =  fields.Many2one('uom.uom', related='product_id.uom_id')
    cost = fields.Float(string='Cost', related='product_id.standard_price')
    weight = fields.Float(digits='Product Unit of Measure', default=1.0)
    price_unit = fields.Float(string='Unit Price', digits='Product Price', default=0.0)
    material_cost = fields.Float(string='Material Cost', digits='Product Price', default=0.0, compute='get_material_cost')
    remarks = fields.Char(string='Remarks', size=70)

class ProductEntryCost(models.Model):
    _name = 'product.entry.cost'
    _description = "Product Entry Cost"

    @api.depends('percentage','entry_cost_id.order_line')
    def get_per_value(self):
        for line in self.filtered(lambda x:x.entry_cost_id):
            line.total = line.entry_cost_id.total_material_cost * line.percentage/100

    name = fields.Char('List')
    percentage = fields.Float(string='Percentage', digits='Product Price', default=0.0)
    total = fields.Float(string='Subtotal', digits='Product Price', default=0.0, compute='get_per_value')
    entry_cost_id = fields.Many2one('product.entry')