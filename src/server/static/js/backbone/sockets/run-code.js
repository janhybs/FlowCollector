/*global Backbone, jQuery, _, ENTER_KEY */
var app = app || {};

(function ($) {
    'use strict';

    /**
     * Simple class for handling incoming and outgoing sockets
     * @param options additional options
     * @returns {{connection: null, uponConnection: Array, url: string, connect: Function, relayEvents: Function, sendRunScriptRequest: Function, onConnect: Function, onDisconnect: Function, onDebug: Function, onCommandStart: Function, onCommandEnd: Function, onStdout: Function, onStderr: Function, initialize: Function}}
     * @constructor
     */
    app.Socket = function (options) {
        return {

            // socket connection
            connection: null,

            // array of function and arguments which should be called when connection is established
            uponConnection: [],

            // socket url
            url: "http://" + document.domain + ":" + location.port + "/",


            /**
             * Connect socket to server
             */
            connect: function () {
                this.connection = io.connect (this.url);

                // register events
                this.connection.on ('connect', this.onConnect);
                this.connection.on ('disconnect', this.onDisconnect);
                this.connection.on ('debug', this.onDebug);

                // relay command events
                this.relayEvents ('command_id',
                    'command-start', 'command-output', 'command-end'
                );

                // relay script events
                this.relayEvents ('script_id',
                    'script-start', 'script-end'
                );
            },


            /**
             * Method which to given section generates socket listeners specified in args
             *
             * upon event there is event triggered:
             *  - once as original event
             *  - once as original event with specified section argument (command_start:command_id_here)
             * @param section
             */
            relayEvents: function (section) {
                // convert to array and remove first element
                var args = Array.prototype.slice.call (arguments);
                args.shift ();

                _.each (arguments, function (event, index, args) {
                    var ctx = this;
                    this.connection.on (event,
                        function (data) {
                            ctx.trigger (event + ":" + data[section], data);
                            ctx.trigger (event, data);
                        });
                }, this);
            },

            /**
             * Method which sends run_code socket request to server right away if connection is established
             * or after establishing it
             * @param script_id
             * @returns {app.Socket}
             */
            sendRunScriptRequest: function (script_id) {
                //debug ('sendRunScriptRequest');
                if (this.connection === null) {
                    this.uponConnection = [this.sendRunScriptRequest, script_id];

                    this.connect ();
                    return this;
                }

                this.connection.emit ('run-code', {script_id: script_id});
                return this;
            },

            /**
             * Handler for on connect event
             */
            onConnect: function () {
                debugSocket ('CONNECTED');
                if (this.uponConnection && this.uponConnection.length > 0) {

                    var args = _.clone (this.uponConnection);
                    this.uponConnection = null;
                    var func = args.shift ();
                    func.apply (this, args);
                }

            },

            /**
             * Handler for on disconnect event
             */
            onDisconnect: function () {
                debugSocket ('DISCONNECTED');
            },

            /**
             * handler for debugging messages from server
             * @param msg
             */
            onDebug: function (msg) {
                debugSocket ('dbg');
                console.log (msg);
            },

            /**
             * bind function's 'this'
             */
            initialize: function () {
                _.bindAll (this,
                    'onConnect', 'onDisconnect', 'relayEvents',
                    'sendRunScriptRequest', 'connect'
                );
            }

        }
    };

    // create socket instance
    app.appSocket = new app.Socket ({});
    // extends instance by events
    _.extend (app.appSocket, Backbone.Events);
    // initialize socket
    app.appSocket.initialize ();


}) (jQuery);