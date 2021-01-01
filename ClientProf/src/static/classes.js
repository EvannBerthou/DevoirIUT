var open = false;
var modal, close;
var modal_id, modal_nom, modal_select, modal_submit;

function init() {
    modal_id = document.getElementById('modal_id');
    modal_nom = document.getElementById('modal_nom');
    modal_select = document.getElementById('modal_select');
    modal_submit = document.getElementById('modal_submit');

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
    modal_nom.value = nom;
    for (let i = 0; i < modal_select.options.length; i++) {
        let opt = modal_select.options[i];
        opt.selected = false;
        for (let j = 0; j < actifs.length; j++) {
            if (opt.value === actifs[j]) {
                opt.selected = true;
                break;
            }
        }
    }
    modal_submit.textContent = "Modifier";
}

function clear_modal_values() {
    modal_submit.textContent = "Ajouter";
}

function open_modal(args) {
    if (args !== undefined) {
        set_modal_values(args);
    }
    else {
        clear_modal_values();
    }
    modal.style.display = "block";
}
