document.addEventListener("DOMContentLoaded", () => {

    console.log("MediLens Loaded");

});


function confirmDelete(){

    return confirm(
        "Are you sure you want to delete this record?"
    );

}


function searchMedicine(){

    let input = document.getElementById("medicineSearch");

    let filter = input.value.toLowerCase();

    let cards = document.getElementsByClassName("medicine-card");

    for(let i = 0; i < cards.length; i++){

        let title = cards[i]
            .getElementsByTagName("h2")[0];

        if(title){

            let value = title.innerText.toLowerCase();

            if(value.indexOf(filter) > -1){

                cards[i].style.display = "";

            }

            else{

                cards[i].style.display = "none";

            }

        }

    }

}