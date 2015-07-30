var app = app || {};

(function () {
    'use strict';


    /**
     * Script class
     * defines object storing commands. Each script belong to one job and can have multiple commands associated with
     * this instance
     *
     * commands field is no accessible by standard 'get' method but simply by instance.commands
     *
     */
    app.Script = Backbone.Model.extend ({

        // load data
        urlRoot: '/api/scripts/',

        defaults: {
            id: '',
            exit_code: 666,
            start_at: 0,
            duration: null
        },

        /**
         * Create collection of Commands upon init
         */
        initialize: function () {
            this.commands = new app.CommandCollection (this.list ? this.list : [], {parse: true});
            if (this.list) delete this.list;
        },

        /**
         * Post-parsing processing
         *
         * In this part commands fields are converted to CommandCollection and are deleted from response
         * @param response
         * @returns {Object}
         */
        parse: function (response) {
            if (_.has (response, "commands")) {
                this.list = response.commands;
                delete response.commands;

                if (this.commands)
                    this.commands.reset (this.list, {parse: true});
            }

            return response;
        },

        /**
         * Json serialization of this instance
         *
         * commands fields is always present even if as emtpy array ([])
         * also added representation of start_at, duration, exit_code fields
         *
         * all commands joined together with newlines and everything is stored in commandsRaw
         * @returns {Object}
         */
        toJSON: function () {
            var json = _.clone (this.attributes);
            json.commands = this.commands ? this.commands.toJSON () : [];
            json.startAtRepr = json.start_at ? formatDate (json.start_at) : false;
            json.durationRepr = json.duration ? (json.duration / 1000.0).toString ().concat (' ms') : false;
            json.exitCodeRepr = json.exit_code !== null && json.exit_code != 666 ? json.exit_code.toString () : false;
            json.commandsRaw = '';
            _.each (json.commands, function (command) {
                json.commandsRaw += command.source_code + '\n';
            });
            return json;
        }
    });
}) ();
