function processNew(curE, newE) {
    curE.classList.remove('cur');
    curE.classList.add('hidden');
    newE.classList.remove('hidden');
    newE.classList.add('cur');
}


function next() {
    var cur = document.getElementsByClassName('cur')[0];
    var nextSibling = cur.nextElementSibling;
    if (nextSibling) {
        processNew(cur, nextSibling);
    }
}

function back() {
    var cur = document.getElementsByClassName('cur')[0];
    var previousSibling = cur.previousElementSibling;
    if (previousSibling) {
        processNew(cur, previousSibling);
    }
}

(($, window, document) => {
    "use strict";
    // Your code here
    $(document).ready(function () {
        $("#next_btn").click(function () {
            next();
        });
        $("#back_btn").click(function () {
            back();
        });
    }
    )
})(jQuery, window, document)
