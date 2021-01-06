var open = false;
var modal, close;
var modal_id, modal_nom, modal_prenom, modal_mail, modal_mdp, modal_submit;

function init() {
    modal_id = document.getElementById('modal_id');
    modal_nom = document.getElementById('modal_nom');
    modal_prenom = document.getElementById('modal_prenom');
    modal_mail = document.getElementById('modal_mail');
    modal_mdp = document.getElementById('modal_mdp');
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
    const [id, nom, prenom, mail] = args
    modal_id.value = id;
    modal_nom.value = nom;
    modal_prenom.value = prenom;
    modal_mail.value = mail;
    modal_mdp.value = "";
    modal_submit.textContent = "Modifier";
}

function clear_modal_values() {
    modal_id.value = "";
    modal_nom.value = "";
    modal_prenom.value = "";
    modal_mail.value = "";
    modal_mdp.value = "";
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
