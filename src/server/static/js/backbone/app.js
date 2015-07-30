var app = app || {};

$ (function () {
    'use strict';


    //$.ajax('http://localhost/jsapp/data/job-1.json', function ())
    //console.log (app.ScriptCollection.url)



    // global instance of 'main job'
    app.job = new app.Job ();
    // global jobs instance
    app.jobs = new app.JobCollection();

    // create one main job view
    app.jobView = new app.JobView ({model: app.job})


    // create global router instance
    app.appRouter = new app.AppRouter();

    // kick things off by creating the `App`
    app.appView = new app.AppView();


    Backbone.history.start();
});