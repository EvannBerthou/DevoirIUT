var open = false;
function editable(e) {
    if (!open){
        open = true;
        let elem = document.getElementsByClassName(e.value);
        document.getElementById("save_button_" + e.value).style.visibility = 'visible';
        document.getElementById("button_" + e.value).style.visibility = 'hidden';
        for(let i = 0; i != elem.length; i++) {
            elem[i].readOnly = false;
            if (elem[i].name == 'date') {
                elem[i].type = 'date';
            }
        }
    }
    else {
        alert("Vous ne pouvez modifier que un devoir à la fois !")
    }
}
