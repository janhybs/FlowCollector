var app = app || {};

$ (function () {
    'use strict';


    /**
     * Simple router class which listens on url change and process thees changes accordingly by listeners
     */
    app.AppRouter = Backbone.Router.extend({

        noRoute:  true,

        // default routes
        routes: {
            "job/:job_id":  "loadJob",
            "*anoything": "lastHook" // last resort hook which catches everything (even nothing)
        },

        /**
         * Event handler called when job_id is changed in url
         * Upon change job model is changed and fetched
         * @param job_id
         * @param page
         */
        loadJob: function(job_id, page) {
            this.job_id = job_id;

            this.trigger('jobIdChange', this.job_id);

            // changde model
            app.job.id = job_id
            app.job.isLoading = true;
            app.job.isBroken = false;
            app.jobView.render();

            // update it
            app.job.fetch ({
                success: function () {
                    app.job.isLoading = false;
                    app.job.isBroken = false;
                    app.jobView.render();
                },
                error: function () {
                    app.job.isLoading = false;
                    app.job.isBroken = true;
                    app.jobView.render();
                }
            });
        },

        // set flag that there is not job_id
        lastHook: function (page) {
            this.job_id = false;
        }

    });
});
