function requestNotificationPermission(){
    if("Notification" in window && Notification.permission === "default"){
        Notification.requestPermission();
    }
}

function checkDueReminders(){

    const cards = document.querySelectorAll(".reminder-card");

    const now = new Date();

    const currentHours = String(now.getHours()).padStart(2, "0");
    const currentMinutes = String(now.getMinutes()).padStart(2, "0");
    const currentTime = `${currentHours}:${currentMinutes}`;

    cards.forEach(card => {

        const reminderTime = card.dataset.time;
        const isActive = card.dataset.active === "true";
        const medicineName = card.dataset.medicine;
        const alreadyNotified = card.dataset.notified === "true";

        if(isActive && reminderTime === currentTime){

            card.classList.add("due-now");

            if(!alreadyNotified){
                sendDueNotification(medicineName, reminderTime);
                card.dataset.notified = "true";
            }

        } else {
            card.classList.remove("due-now");
            card.dataset.notified = "false";
        }

    });

}

function sendDueNotification(medicineName, time){

    if("Notification" in window && Notification.permission === "granted"){
        new Notification("Medication Reminder", {
            body: `Time to take ${medicineName} (${time})`,
            icon: "/static/images/favicon.png"
        });
    }

}

document.addEventListener("DOMContentLoaded", () => {

    requestNotificationPermission();
    checkDueReminders();

    setInterval(checkDueReminders, 20000);

});