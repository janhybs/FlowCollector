/*global Backbone, jQuery, _, ENTER_KEY */
var app = app || {};

(function ($) {
    'use strict';

    // The Application
    // ---------------

    app.JobPeekView = Backbone.View.extend ({
        // list tag
        tagName: 'li',

        jobTemplate: _.template ($ ('#job-peek-template').html ()),

        /**
         * Add listeners and auto render
         */
        initialize: function () {
            this.model.on ('change', this.render, this);
            this.render ();
        },

        events: {
        },

        /**
         * Rendering template
         * @returns {app.JobPeekView}
         */
        render: function () {
            this.$el.html (this.jobTemplate (this.model.toJSON ()));
            return this;
        }
    });
}) (jQuery);
