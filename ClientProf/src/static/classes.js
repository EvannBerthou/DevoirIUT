var open = false;
function editable(classe) {
    if (!open){
        open = true;
        document.getElementById(classe).readOnly = false;
        document.getElementById("m_" + classe).style.display = "none";
        document.getElementById("e_" + classe).style.display = "inline";
    }
    else {
        alert("Vous ne pouvez modifier que un devoir à la fois !")
    }
}
