/*global Backbone, jQuery, _, ENTER_KEY */
var app = app || {};

(function ($) {
    'use strict';

    // The Application
    // ---------------

    // renders the full list of todo items calling TodoView for each one.
    app.ScriptView = Backbone.View.extend ({
        tagName: 'div',

        jobTemplate: _.template ($ ('#script-template').html ()),

        initialize: function () {
            this.model.on ('sync', this.onSync, this);
            this.commandViews = [];
            this.commandCompleted = 0;

            this.listenTo (app.appSocket, 'script-start:' + this.model.id, this.onScriptStart);
            this.listenTo (app.appSocket, 'script-end:' + this.model.id, this.onScriptEnd);
            this.listenTo (app.appSocket, 'command-end', this.onCommandEnd);
        },

        /**
         * Method which destroys whole view and its children if any
         */
        destroy: function () {
            this.remove ();
            this.destroyChildren ();
        },

        /**
         * Method which destroys views children if any
         */
        destroyChildren: function () {
            _.each (this.commandViews, function (view) {
                view.destroy ();
            });
            this.commandViews = [];
        },

        // bind events
        events: {
            'click .run-script': 'runScript',
            'click .edit-script': 'editScript',
            'click .delete-script': 'deleteScript',
            'click .save-changes': 'saveChanges',
            'click .abort-changes': 'abortChanges'
        },


        /**
         * Method for rendering entire script along with comamnds
         * @returns {app.ScriptView}
         */
        render: function () {
            this.$el.html (this.jobTemplate (this.model.toJSON ()));
            this.$commands = this.$el.find ('.script-commands');

            this.addAll ();
            return this;
        },

        /**
         * Method for rendering one CommandView
         * @param script
         */
        addOne: function (command) {
            if (!command.isValid ())
                return this;

            var view = new app.CommandView ({model: command});
            this.commandViews.push (view);
            this.$commands.append (view.render ().el);
            return this;
        },

        /**
         * Method for rendering all CommandView
         */
        addAll: function () {
            this.destroyChildren ();
            this.$commands.html ('');
            this.model.commands.each (this.addOne, this);
        },

        /**
         * Method which sends socket to server with request to run code
         * Also prepares gui for run
         * @param ev
         */
        runScript: function (ev) {
            this.$ (' .script-commands .source').addClass ('queued');
            this.$ (' .stdout-stderr pre').html ('');
            app.appSocket.sendRunScriptRequest (this.model.id);
        },

        /**
         * Method which switches view to edit mode
         * @param ev
         */
        editScript: function (ev) {
            this.$ ('.script-commands').hidden ();
            this.$ ('.script-info').hidden ();
            this.$ ('.script-details').hidden ();
            this.$ ('.script-editable-commands').visible ();
        },

        /**
         * Method called when editing is was aborted
         * @param ev
         */
        abortChanges: function (ev) {
            this.$ ('.script-commands').visible ();
            this.$ ('.script-info').visible ();
            this.$ ('.script-details').visible ();
            this.$ ('.script-editable-commands').hidden ();
        },

        /**
         * Deletes current script
         * @param ev
         */
        deleteScript: function (ev) {
            Backbone.sync ('delete', this.model, {
                success: function (data) {
                    app.job.fetch ();
                },
                error: function () {
                    console.log ('model NOT removed');
                }
            });
        },

        /**
         * Method which saves changes and sends edits to server
         * Also fetches new object
         * @param ev
         */
        saveChanges: function (ev) {
            this.$ ('.script-commands').visible ();
            this.$ ('.script-info').visible ();
            this.$ ('.script-details').visible ();
            this.$ ('.script-editable-commands').hidden ();

            var raw = this.$ ('.script-editable-commands textarea').val ();

            // virgin script will be edited
            if (this.model.get ('exit_code') == 666) {
                var that = this;
                this.model.set ({commandsNew: raw});
                Backbone.sync ('update', this.model, {
                    success: function (data) {
                        that.model.fetch ();
                    },
                    error: function () {
                        console.log ('model NOT updated');
                    }
                });
            } else {
                // executed scripts will be added
                var model = new app.Script ({commandsNew: raw, job_id: this.model.get ('job_id')});
                Backbone.sync ('create', model, {
                    success: function (data) {
                        //app.job.isLoading = true;
                        //app.job.isBroken = false;
                        //app.jobView.render();
                        //
                        //app.job.fetch ({
                        //    success: function () {
                        //        app.job.isLoading = false;
                        //        app.job.isBroken = false;
                        //        app.jobView.render();
                        //    },
                        //    error: function () {
                        //        app.job.isLoading = false;
                        //        app.job.isBroken = true;
                        //        app.jobView.render();
                        //    }
                        //});
                        app.job.fetch ();
                    },
                    error: function () {
                        console.log ('model NOT created');
                    }
                });
            }

        },

        /**
         * After changes are done sync is triggered which will re-render this view
         */
        onSync: function () {
            this.render ();
        },

        /**
         * socket callback method called when this script has been started
         * @param data socket event data
         */
        onScriptStart: function (data) {
            this.$ ('.progress').removeClass ('hidden');
            this.$ ('.progress-bar').css ('width', '0%').attr ('aria-valuenow', 0);
            this.commandCompleted = 0;
        },

        /**
         * socket callback method called when this script has ended
         * @param data socket event data
         */
        onScriptEnd: function (data) {
            this.$ ('.progress').addClass ('hidden');
            this.model.set ({exit_code: data.exit_code, duration: data.duration, start_at: data.start_at});
        },

        /**
         * socket callback method called when EVERY command ends
         *
         * Requires filtering incoming data object to see if data object is meant to this script
         * Updates progress bar after each event has ended
         * @param data socket event data
         */
        onCommandEnd: function (data) {
            // event is not for me
            if (data.script_id != this.model.id) return;

            var value = (++this.commandCompleted / this.commandViews.length) * 100;
            value = value > 100 ? 100 : value < 0 ? 0 : value;
            this.$ ('.progress-bar').css ('width', value + '%').attr ('aria-valuenow', value);
        }
    });
}) (jQuery);