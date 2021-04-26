odoo.define('crm_custom.crm_custom', function (require) {
    "use strict";
 
    var relational_fields = require('web.relational_fields');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var KanbanController = require('web.KanbanController');
 
    var _t = core._t;
 
    relational_fields.FieldStatus.include({
        _onClickStage: function (e) {
            var self = this;
            var old_stage_id = this.record['data'].stage_id.res_id;
            var new_stage_id = $(e.currentTarget).data("value");
            if (this.model === 'crm.lead'){
                this._rpc({
                    model: 'crm.stage',
                    method: 'get_sequence',
                    args: [old_stage_id, new_stage_id],
                    }).then(function (output) {
                        if (output[1]){
                            self._setValue(old_stage_id);
                        }
                        if (!output[1] && output[0]) {
                            Dialog.confirm(this, _t("Do you want to change the stage?"), {
                                confirm_callback: function () {
                                    self._setValue(new_stage_id);
                                },
                            });
                        }
                        if (!output[1] && !output[0]) {
                            Dialog.confirm(this, _t("You can not move back"), {
                                confirm_callback: function () {
                                    return false;
                                },
                            });   
                        }
                });
            }
            else {
                self._setValue(new_stage_id);
            }
        },
    });
});
