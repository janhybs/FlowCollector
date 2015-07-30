var app = app || {};

(function () {
    'use strict';

    // Job Model
    // ----------


    /**
     * Job class
     * defines object storing scripts. Each job belong to one user and can have multiple scripts associated with
     * this instance
     *
     * script field is no accessible by standard 'get' method but simply by instance.script
     *
     */
    app.Job = Backbone.Model.extend ({


        // default url on server for api requests
        urlRoot: '/api/jobs/',

        // Default attributes
        defaults: {
            id: '',
            name: '',
            status: '',
            settings: {},
            user: {}
        },

        /**
         * Create collection of Scripts upon init
         */
        initialize: function () {
            this.scripts = new app.ScriptCollection (this.list ? this.list : [], {parse: true});
            if (this.list) delete this.list;
            return this;
        },

        /**
         * Post-parsing processing
         *
         * In this part script fields are converted to ScriptCollection and are deleted from response
         * @param response
         * @returns {Object}
         */
        parse: function (response) {
            // force initialization
            if (!this.scripts)
                this.initialize ();

            if (_.has (response, "scripts")) {
                this.list = response.scripts;
                this.list.sort(function (a, b) {
                    return a.start_at - b.start_at;
                });
                delete response.scripts;


                if (this.scripts)
                    this.scripts.reset (this.list, {parse: true});
            }

            return response;
        },

        /**
         * Json serialization of this instance
         *
         * script fields is always present even if as emtpy array ([])
         * @returns {Object}
         */
        toJSON: function () {
            var json = _.clone (this.attributes);
            json.scripts = this.scripts ? this.scripts.toJSON () : [];
            return json;
        }
    });

}) ();
