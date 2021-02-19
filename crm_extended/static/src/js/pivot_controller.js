odoo.define('crm_extended.PivotController', function (require) {
'use strict';

    var PivotController = require('web.PivotController');

    PivotController.include({
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * Remove pseudo css class from HTMLElement (like :hover)
         *
         * @private
         * @param {HTMLElement} node
         */

        /**
         * @override
         * @private
         */
        _updateButtons: function (){
        	var self = this;
            this._super.apply(this);
             if (!this.$buttons) {
            	return;
            }
           if (this.modelName == "crm.lead") {
            	this.$buttons.find('.o_pivot_download').prop('disabled', true);
            	this.getSession().user_has_group('crm_extended.group_show_pivot').then(function(has_group){
            		if (has_group) {
            			self.$buttons.find('.o_pivot_download').prop('disabled', false);

            		}
            	});
            }
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @override
         * @private
         * @param {MouseEvent} ev
         */

    });

});

odoo.define('crm_extended.CohortController', function (require) {
'use strict';

    var CohortController = require('web_cohort.CohortController');
    CohortController.include({
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * Remove pseudo css class from HTMLElement (like :hover)
         *
         * @private
         * @param {HTMLElement} node
         */
         
        _updateButtons: function (){
        	var self = this;
            this._super.apply(this);
            if (!this.$buttons) {
            	return;
            }
            if (this.modelName == "crm.lead") 
            {
                this.$buttons.find('.o_cohort_download_button').toggleClass(
                'd-none', true);
				this.getSession().user_has_group('crm_extended.group_show_cohort').then(function(has_group){
            		if (has_group) {
            			self.$buttons.find('.o_cohort_download_button').toggleClass('d-none', false);

            		}
            	});
            }
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @override
         * @private
         * @param {MouseEvent} ev
         */

    });
});

odoo.define('crm_extended.ListController', function (require) {
'use strict';
    var ListController = require('web.ListController');
    
    ListController.include({

        _updateButtons: function (mode) {
            var self = this;
            this._super.apply(mode);
            if (!this.$buttons) {
                return;
            }
            if (this.modelName == "crm.lead") {
                this.$buttons.find('.o_list_export_xlsx').toggleClass(
                'd-none', true);
                this.getSession().user_has_group('crm_extended.group_show_pivot').then(function(has_group){
                    if (has_group) {
                        self.$buttons.find('.o_list_export_xlsx').toggleClass('d-none', false);
                    }
                });
            }
        },
    });

});