/*global Backbone, jQuery, _, ENTER_KEY */
var app = app || {};

(function ($) {
    'use strict';

    // The Application
    // ---------------

    // renders the full list of todo items calling TodoView for each one.
    app.JobView = Backbone.View.extend ({
        el: '#job-view',

        jobTemplate: _.template ($ ('#job-template').html ()),


        /**
         * Add listeners and clears children
         */
        initialize: function () {
            this.scriptViews = [];
            this.model.on ('change', this.render, this);
            this.listenTo (this.model.scripts, 'reset', this.onCollectionChange);
            this.listenTo (this.model.scripts, 'change', this.onCollectionChange);
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
            _.each (this.scriptViews, function (view) {
                view.destroy ();
            });
            this.scriptViews = [];
        },

        // default listeners
        events: {
            'click .create-script': 'createScript',
            'dblclick .job-title': 'editJob',
            'click .delete-job': 'deleteJob',
            'keypress .job-title-edit': 'editKeypress',
            'keydown .job-title-edit': 'editKeydown',
            'blur .job-title-edit': 'hideEdit'
        },

        /**
         * Method for entering into edit mode
         * @param ev
         */
        editJob: function (ev) {
            this.$ ('.job-title').hidden ();
            this.$ ('.job-title-edit').visible ();

            this.$ ('.job-title-edit').focus ();
            this.$ ('.job-title-edit').val (this.model.get ('name'));
        },

        /**
         * Method which is called when editing is over
         * @param ev
         */
        confirmEdit: function (ev) {
            this.$ ('.job-title').visible ();
            this.$ ('.job-title-edit').hidden ();

            var value = this.$ ('.job-title-edit').val ();
            if (value.trim ().length == 0)
                return;

            this.model.set ({name: value});
            Backbone.sync ('update', this.model);
        },

        /**
         * Aborting changes
         * @param ev
         */
        hideEdit: function (ev) {
            this.$ ('.job-title').visible ();
            this.$ ('.job-title-edit').hidden ();
        },

        /**
         * Delete entire job
         * @param ev
         */
        deleteJob: function (ev) {
            var that = this;
            Backbone.sync ('delete', this.model, {
                success: function (data) {
                    app.jobs.remove (that.model);
                    that.model.set('id', '');

                    if (app.jobs.models.length == 0) {
                        app.appView.render();
                    } else {
                        var job_id = app.jobs.models[0].id;
                        app.appRouter.navigate ('job/' + job_id, {trigger: true});
                    }

                    app.jobs.fetch ();
                }
            });
        },


        /**
         * handler for keypress while in editing mode
         * @param e
         */
        editKeypress: function (e) {
            if (e.which === 13) {
                this.confirmEdit ();
            }
        },

        /**
         * handler for keypress while in editing mode
         * @param e
         */
        editKeydown: function (e) {
            if (e.which === 27) {
                //this.hideEdit ();
            }
        },

        /**
         * Method sends request to server to 'create' new script
         */
        createScript: function () {
            var model = new app.Script ({job_id: this.model.get ('id'), commandsNew: 'echo "Hello world!"'});
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
        },

        /**
         * If collection has changed redraw all views
         */
        onCollectionChange: function () {
            _.each (this.scriptViews, function (view) {
                view.render ();
            })
        },

        /**
         * Method for rendering this view
         * Also draws all scripts when called
         * @returns {app.JobView}
         */
        render: function () {
            if (this.model.get('id').trim () == "") {
                $ ('#job-list-wrapper').removeClass ('col-md-4');
                $ ('#job-list-wrapper').addClass ('col-md-12');
                this.$el.html ('');
                return this;
            }

            $ ('#job-list-wrapper').addClass ('col-md-4');
            $ ('#job-list-wrapper').removeClass ('col-md-12');
            window.vv = this;


            this.$el.html (this.jobTemplate (this.model.toJSON ()));
            this.$scripts = this.$ ('.job-scripts');

            this.addAll ();

            // todo more specific listener
            if (this.model.isLoading)
                this.$el.addClass ('disabled');
            else
                this.$el.removeClass ('disabled');

            return this;
        },


        /**
         * Method for rendering one ScriptView
         * @param script
         */
        addOne: function (script) {
            var view = new app.ScriptView ({model: script});
            this.scriptViews.push (view);
            this.$scripts.append (view.render ().el);
        },

        /**
         * Method for rendering all ScriptViews
         */
        addAll: function () {
            this.destroyChildren ();
            this.$scripts.html ('');
            this.model.scripts.each (this.addOne, this);
        }
    });
}) (jQuery);