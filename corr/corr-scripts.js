function getKnowledge(idxLs, $) {
    let knowledge = [];
    let idx = idxLs.split(',');
    for (let i in idx) {
        knowledge.push($('#knowledge-' + idx[i]).clone());
        if (i > 2) {
            return knowledge
        }
    };
    return knowledge
}

(($, window, document) => {
    "use strict";
    // Your code here
    $(document).ready(function () {
        $(".gen-content").on("click", this, (e) => {
            let veryHigh = e.currentTarget.getAttribute('veryHigh');
            let high = e.currentTarget.getAttribute('high');
            let med = e.currentTarget.getAttribute('med');
            let allKnowledge = []
            if (veryHigh) {
                allKnowledge.push(veryHigh)
            }
            if (high) {
                allKnowledge.push(high)
            }
            if (med) {
                allKnowledge.push(med)
            }

            var knowledge = getKnowledge(allKnowledge.join(','), $);
            console.log(allKnowledge.join(','));
            // moveToKnowledge($);
            let placeholder = $("#placeholder");
            placeholder.empty()
            for (let k in knowledge) {
                placeholder.append(knowledge[k]);
                placeholder.append('<br>');
            }
        })
    }
    )
})(jQuery, window, document)
