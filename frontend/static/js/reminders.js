// Highlights reminders that are due right now, re-checking every 20 seconds.
// Compares each reminder card's stored time against the current browser time.

function checkDueReminders(){

    const cards = document.querySelectorAll(".reminder-card");

    const now = new Date();

    const currentHours = String(now.getHours()).padStart(2, "0");
    const currentMinutes = String(now.getMinutes()).padStart(2, "0");
    const currentTime = `${currentHours}:${currentMinutes}`;

    cards.forEach(card => {

        const reminderTime = card.dataset.time;
        const isActive = card.dataset.active === "true";

        if(isActive && reminderTime === currentTime){
            card.classList.add("due-now");
        } else {
            card.classList.remove("due-now");
        }

    });

}

document.addEventListener("DOMContentLoaded", () => {

    checkDueReminders();

    setInterval(checkDueReminders, 20000);

});