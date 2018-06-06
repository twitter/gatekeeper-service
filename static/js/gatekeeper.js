function typeaheadInit(strs) {
    return function findMatches(q, cb) {
        var matches, substringRegex;
        matches = [];
        substringRegex = new RegExp(q, 'i');
        $.each(strs, function(i, str) {
            if (substringRegex.test(str)) {
                matches.push(str);
            }
        });
        cb(matches);
    };
}

function typeaheadRun(typeaheadId, sourceName, source) {
    $(typeaheadId + ' .typeahead').typeahead(
        {
            hint: true,
            highlight: true,
            minLength: 0
        },
        {
            limit: 20,
            name: sourceName,
            source: typeaheadInit(source)
        }
    );
}

function typeaheadSubmitFormOnSelect(typeaheadId, formId) {
    $(typeaheadId).on('typeahead:selected', function () {
        $(formId).submit();
    });
}

function selectAllCheckboxes(selectAllId, formOptionsId) {
    $(selectAllId).on('click', function () {
        if (this.checked == true) {
            $(formOptionsId).find('input[type="checkbox"]').prop('checked', true);
            $('.collapse').collapse('show');
        } else {
            $(formOptionsId).find('input[type="checkbox"]').prop('checked', false);
            $('.collapse').collapse('hide');
        }
    });
}

function selectDefaultCheckboxes(defaultCheckboxes) {
    for (var i=0; i<defaultCheckboxes.length; i++) {
      $('#' + defaultCheckboxes[i]).prop('checked', true);
    }
}

function progressBar(progressBarId, progressId, progress) {
    $(progressBarId).css("width", progress + "%");
    $(progressId).attr("aria-valuenow", progress + "%");
}

function showLoadingState(buttonId) {
    $(buttonId).on('click', function () {
        $(this).button('loading');
    });
}

function disableEnterKey(formId) {
    $(formId).bind("keypress", function(e) {
        if (e.keyCode == 13) {
            return false;
        }
    });
}

function enableButtons() { $("button").prop("disabled", false); }
function disableButtons() { $("button").prop("disabled", true); }
