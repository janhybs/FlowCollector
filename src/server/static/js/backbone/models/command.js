var app = app || {};

(function () {
    'use strict';

    /**
     * Command class
     * defines one simple statement along with information about execution
     *
     * Each command must have source code (which is statement)
     * optionally there is output (array of object (i.e. output line + type)) exit_code and duration
     */
    app.Command = Backbone.Model.extend ({
        defaults: {
            id: '',
            duration: null,
            outputLines: [],
            exit_code: null,
            source_code: null
        },

        /**
         * whether is source code valie (is not empty)
         * @returns {boolean}
         */
        isValid: function () {
            return this.get ('source_code').trim ().length > 0;
        },

        /**
         * Post-parsing processing
         * @param response
         * @returns {Object}
         */
        parse: function (response) {
            return response;
        },

        /**
         * Json serialization of this instance
         *
         * Additionaly there are attributes added such as representation od duration and exit_code
         * @returns {Object}
         */
        toJSON: function () {
            var json = _.clone (this.attributes);

            json.hasData = json.outputLines.length > 0;
            json.durationRepr = json.duration > 200 ? json.duration + ' s' : false;
            json.exitCodeRepr = json.exit_code !== null && json.exit_code != 0 ? 'exit: ' + json.exit_code : false;
            return json;
        }
    });
}) ();
