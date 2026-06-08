let selectedDate = "";
let selectedTime = "";
let selectedDoctor = ""; // Ensure it's empty at the start

// Select a psychologist and update UI
function selectPsychologist(event, doctorName) {
    selectedDoctor = doctorName;

    // Remove 'selected' class from all psychologist cards
    document.querySelectorAll(".psychologist-card").forEach(card => card.classList.remove("selected"));
    
    // Add 'selected' class to the clicked card
    event.currentTarget.classList.add("selected");

    // Update the displayed psychologist name in the UI
    document.getElementById("selected-psychologist").innerText = selectedDoctor;

    console.log("Selected Doctor:", selectedDoctor); // Debugging
}

// Select a date
function selectDate() {
    selectedDate = document.getElementById("appointment-date").value;
    console.log("Selected Date:", selectedDate);
}

// Select a time
function selectTime(button) {
    document.querySelectorAll(".time-button").forEach(btn => btn.classList.remove("selected"));
    button.classList.add("selected");
    selectedTime = button.innerText;
    console.log("Selected Time:", selectedTime);
}

// Handle form submission
document.getElementById("appointmentForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    let name = document.getElementById("name").value;
    let email = document.getElementById("email").value;
    let phone = document.getElementById("phone").value;
    selectedDate = document.getElementById("appointment-date").value;
    selectedTime = document.querySelector(".time-button.selected")?.innerText;

    if (!selectedDoctor) {
        alert("Please select a psychologist.");
        return;
    }
    if (!selectedDate || !selectedTime) {
        alert("Please select a date and time.");
        return;
    }

    let requestData = { name, email, phone, doctor: selectedDoctor, mode: "manual", date: selectedDate, time: selectedTime };
    console.log("Sending Data:", requestData);

    try {
        let response = await fetch("http://127.0.0.1:5000/book_appointment", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestData)
        });

        let result = await response.json();
        console.log("Server Response:", result);
        document.getElementById("response-message").innerText = result.message || "Error booking appointment.";
    } catch (error) {
        console.error("Error:", error);
        document.getElementById("response-message").innerText = "Failed to connect to the server.";
    }
});

// Listen for changes in date picker
document.getElementById("appointment-date").addEventListener("change", selectDate);
