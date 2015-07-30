var app = app || {};

(function ($) {
    'use strict';

    /**
     * Overall view for whole application
     */
    app.AppView = Backbone.View.extend ({

        el: '#job-list',
        current_id: '',

        noJobsTemplate: _.template ($ ('#no-jobs-template').html ()),

        events: {},

        /**
         * Method for updating styles based on url
         * @param current_id
         */
        updateStyles: function (current_id) {
            this.current_id = current_id;

            $ (".job-link").removeClass ('selected');
            $ (".job-link[data-job-id='" + this.current_id + "']").addClass ('selected');
        },

        /**
         * Add listeners and fetch jobs
         */
        initialize: function () {

            this.$list = $ ('#job-list');
//
            this.listenTo (app.jobs, 'add', this.addOne);
            this.listenTo (app.jobs, 'reset', this.addAll);
            this.listenTo (app.jobs, 'remove', this.addAll);
            this.listenTo (app.job, 'change', this.refreshList);
            this.listenTo (app.appRouter, 'jobIdChange', this.onJobIdChange);

            this.refreshList ();
        },

        refreshList: function () {
            var that = this;
            app.jobs.fetch ({
                reset: true,
                success: function () {
                    // check jobs obtained
                    if (app.jobs.length == 0) {
                        // todo no jobs found, create one
                        that.render ();
                        return;
                    }

                    // check current url
                    if (app.appRouter.job_id === false) {
                        // on empty route, set id of first received job_id
                        var job_id = app.jobs.models[0].id;
                        app.appRouter.navigate ('job/' + job_id, {trigger: true});
                    } else {
                        // trigger job id change after render is complete
                        app.appRouter.trigger ('jobIdChange', app.appRouter.job_id);
                    }
                }
            });
        },

        /**
         * Handler for url job id change
         * @param job_id
         */
        onJobIdChange: function (job_id) {
            this.updateStyles (job_id);
        },

        /**
         * Method which renders no jobs if there are no jobs
         */
        render: function () {
            if (app.jobs.length == 0) {
                this.$el.html (this.noJobsTemplate ({}));
                app.jobView.render ();
            }
        },

        /**
         * Method for rendering one JobPeekView
         * @param job
         */
        addOne: function (job) {
            var view = new app.JobPeekView ({model: job});
            this.$list.append (view.render ().el);
        },

        /**
         * Method for rendering all JobPeekViews
         */
        addAll: function () {
            this.$list.html ('');
            app.jobs.each (this.addOne, this);
        }
    });

}) (jQuery);