var open = false;
var modal, close;
var modal_id, modal_nom, $modal_select, modal_submit;

function init() {
    modal_id = document.getElementById('modal_id');
    modal_nom = document.getElementById('modal_nom');
    modal_submit = document.getElementById('modal_submit');

    var $select = $("#modal_select").selectize({
        sortField: 'text'
    });
    modal_select = $select[0].selectize;

    modal = document.getElementById("myModal");
    close = document.getElementById("modal_close");

    close.onclick = function() {
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
}

function set_modal_values(args) {
    const [nom, actifs] = args
    modal_id.value = nom;
    modal_nom.value = nom;
    console.log(actifs);
    modal_select.setValue(actifs, true)
    modal_submit.textContent = "Modifier";
}

function clear_modal_values() {
    modal_submit.textContent = "Ajouter";
}

function open_modal(args) {
    modal_select.clear();
    if (args !== undefined) {
        set_modal_values(args);
    }
    else {
        clear_modal_values();
    }
    modal.style.display = "block";
}
