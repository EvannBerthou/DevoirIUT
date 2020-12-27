var open = false;
function editable(e) {
    if (!open){
        open = true;
        let elem = document.getElementsByClassName(e.value);
        document.getElementById("save_button_" + e.value).style.display = 'block';
        document.getElementById("button_" + e.value).style.display = 'none';
        document.getElementById("selection_classe_"+e.value).style.display='block';
        document.getElementById("classes_"+e.value).style.display='none';

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


var ouvert = false;
function afficherClasses(e){
    ouvert = !ouvert;
    let value=e.attributes[1].value;
    let selected=document.getElementsByClassName("classe_devoir_"+value);
    let options=document.getElementsByClassName("option_"+value);
    for (let k=0;k!=options.length;k++){
        for(let i =0;i!=selected.length;i++){
            if (selected[i].childNodes[0].data==options[k].name){
                options[k].checked=true;
            }   
        }
    }
    document.getElementById("classes").style.display = (ouvert === true) ? "block" : "none";
}
