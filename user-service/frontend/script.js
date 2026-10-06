const API_URL = "http://127.0.0.1:5001/api/v1";

function showMessage(message) {
    document.getElementById("message").innerText = message;
}


// ==========================================
// REGISTER
// ==========================================

async function registerUser() {

    const name = document.getElementById("registerName").value;
    const email = document.getElementById("registerEmail").value;
    const password = document.getElementById("registerPassword").value;

    try {

        const response = await fetch(`${API_URL}/users/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: name,
                email: email,
                password: password
            })
        });

        const data = await response.json();

        showMessage(data.message || data.error);

    } catch (error) {

        showMessage("Unable to connect to User Service.");

    }
}


// ==========================================
// LOGIN
// ==========================================

async function loginUser() {

    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;

    try {

        const response = await fetch(`${API_URL}/users/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {

            localStorage.setItem("access_token", data.access_token);

            showMessage("Login successful!");

        } else {

            showMessage(data.error);

        }

    } catch (error) {

        showMessage("Unable to connect to User Service.");

    }
}


// ==========================================
// GET PROFILE
// ==========================================

async function getProfile() {

    const token = localStorage.getItem("access_token");

    if (!token) {
        showMessage("Please login first.");
        return;
    }

    try {

        const response = await fetch(`${API_URL}/users/me`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        const data = await response.json();

        if (response.ok) {

            document.getElementById("profile").innerHTML = `
                <strong>Name:</strong> ${data.user.name}<br>
                <strong>Email:</strong> ${data.user.email}<br>
                <strong>Role:</strong> ${data.user.role}
            `;

            showMessage("Profile loaded successfully.");

        } else {

            showMessage(data.msg || data.error);

        }

    } catch (error) {

        showMessage("Unable to connect to User Service.");

    }
}


// ==========================================
// LOGOUT
// ==========================================

function logout() {

    localStorage.removeItem("access_token");

    document.getElementById("profile").innerHTML = "";

    showMessage("Logged out successfully.");
}