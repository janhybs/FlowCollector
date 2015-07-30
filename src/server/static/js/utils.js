var now = Date.now ();

function debug (msg) {
    var time = (Date.now () - now).toString ();
    while (time.length < 5) time = " " + time;
    console.log (time + ': ' + msg);
}

function debugSocket (msg) {
    debug ('[s]: ' + msg);
}

function formatDate (date) {
    date = date instanceof Date ? date : new Date (date);
    return date.toLocaleDateString () + ' ' + date.toLocaleTimeString ();
}


jQuery.fn.extend ({
    hidden: function () {
        return this.each (function () {
            $ (this).addClass ('hidden');
        });
    },
    visible: function () {
        return this.each (function () {
            $ (this).removeClass ('hidden');
        });
    }
});