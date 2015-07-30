/*global Backbone */
var app = app || {};

(function () {
	'use strict';

    /**
     * Job collection
     * collection for storing Job instances
     */
	app.JobCollection = Backbone.Collection.extend({
		model: app.Job,
		url: "/api/jobs",

		comparator: 'name'
	});

    /**
     * Script collection
     * collection for storing Script instances
     */
	app.ScriptCollection = Backbone.Collection.extend ({
		model: app.Script
	});

    /**
     * Command collection
     * collection for storing Command instances
     */
	app.CommandCollection = Backbone.Collection.extend ({
		model: app.Command
	});

})();