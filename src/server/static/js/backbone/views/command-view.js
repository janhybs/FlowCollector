/*global Backbone, jQuery, _, ENTER_KEY */
var app = app || {};

(function ($) {
    'use strict';

    /**
     * Command view class which renders one command and ots details
     * @type {void|*}
     */
    app.CommandView = Backbone.View.extend ({
        tagName: 'div',

        jobTemplate: _.template ($ ('#command-template').html ()),


        initialize: function () {
            //this.model.on ('change', this.render, this); // too op

            this.listenTo (app.appSocket, 'command-start:' + this.model.id, this.onCommandStart);
            this.listenTo (app.appSocket, 'command-output:' + this.model.id, this.onCommandOutput);
            this.listenTo (app.appSocket, 'command-end:' + this.model.id, this.onCommandEnd);
            this.model.on ('change:duration', this.onDurationChange, this);
            window.cmd = this;

            this.interval_id = -1;
            this.interval_end = false;
            this.interval_start = -1;
        },

        /**
         * Method which destroys whole view and its children if any
         */
        destroy: function () {
            this.remove ();
        },

        events: {
            'click .collapsible-command': 'collapsibleClicked'
        },

        /**
         * Rendering this command
         * @returns {app.CommandView}
         */
        render: function () {
            this.$el.html (this.jobTemplate (this.model.toJSON ()));
            return this;
        },


        /**
         * Method starts timer to update duration real-time
         */
        startClock: function () {
            this.interval_id = setInterval (this.updateDurationValue, 100, this);
            this.interval_start = new Date ().getTime ();
        },

        /**
         * Method which stops and removes timer
         */
        stopClock: function () {
            clearInterval (this.interval_id);
        },

        /**
         * After each timer tick update duration
         */
        updateDurationValue: function (that) {
            if (that.interval_end) {
                clearInterval (that.interval_id);
                return;
            }

            // update model duration
            that.model.set ('duration', new Date ().getTime () - that.interval_start);
        },

        /**
         * Method for opening closing commands output
         * @param e
         */
        collapsibleClicked: function (e) {
            this.$ ('.stdout-stderr').toggleClass ('collapsible-closed');
        },

        /**
         * When model's duration has been changed we will update timer
         * @param e
         */
        onDurationChange: function (e) {
            this.$ ('.duration-info').visible ();
            this.$ ('.duration-info').html (this.model.get ('duration').toString ().concat (' ms'));
        },

        /**
         * socket callback method which prepares command gui for run
         * @param data socket event data
         */
        onCommandStart: function (data) {
            // remove queue flag from code element
            this.$ ('.source').removeClass ('queued');
            // add running flag to li element
            this.$ ('.command').addClass ('running');
            // clear output
            this.$ ('.command-output').html ('');

            this.startClock();
            this.model.set ({start_at: data.start_at});
        },

        /**
         * socket callback method which completes command gui after execution is over
         * @param data socket event data
         */
        onCommandEnd: function (data) {
            var $li = this.$ ('.command');

            $li.removeClass ('running');

            var duration = data.end_at - data.start_at;
            if (duration >= 200)
                $li.find ('.duration-info').removeClass ('hidden').html (duration.toString ().concat (' ms'));

            var exit_code = data.exit_code;
            if (exit_code != 0)
                $li.find ('.exit-info').removeClass ('hidden').html ('exit: '.concat (exit_code.toString ()));

            this.stopClock();
            this.model.set ({exit_code: data.exit_code, duration: data.duration});
        },

        /**
         * socket callback method which adds output lines when execution is in progress
         * @param data socket event data
         */
        onCommandOutput: function (data) {
            var $li = this.$ ('.command');

            $li.removeClass ('non-collapsible-command');
            $li.addClass ('collapsible-command');

            $li.next ().removeClass ('collapsible-closed');
            $li.next ().find ('.'.concat ('command-output')).removeClass ('hidden');

            // add output
            var $holder = $li.next ().find ('.'.concat ('command-output'));
            var model = this.model;
            _.each (data.output, function (r) {
                $holder.append ('<li class="command-output-' + r.type + '">' + r.line + '</li>');
                model.get ('outputLines').push (r);
            });
        }
    });
}) (jQuery);