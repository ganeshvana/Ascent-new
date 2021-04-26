# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class Stage(models.Model):
    _inherit = "crm.stage"

    @api.model
    def get_sequence(self, old_stage_id, new_stage_id):
        old_stage = self.browse(old_stage_id).sequence
        new_stage = self.browse(new_stage_id).sequence
        stages = self.search([]).mapped('sequence')
        last_stage = max(stages)
        scnd_last_stage = stages[-2]
        print("SEQQQQQ", old_stage, new_stage, last_stage, scnd_last_stage)
        move = False
        last = False
        if old_stage < new_stage:
            move = True
        if last_stage == new_stage or scnd_last_stage == new_stage:
            last = True
        return move, last
