let token = "";  // GLOBAL TOKEN

function toggleRegister() {
    const usernameInput = document.getElementById("usernameInput");
    const registerBtn = document.getElementById("registerBtn");
    const toggleBtn = document.getElementById("toggleBtn");
    
    if (usernameInput.style.display === "none") {
        usernameInput.style.display = "inline-block";
        registerBtn.style.display = "inline-block";
        toggleBtn.textContent = "Cancel";
    } else {
        usernameInput.style.display = "none";
        registerBtn.style.display = "none";
        toggleBtn.textContent = "Register";
    }
}

function register() {
    const email = document.getElementById("userIdInput").value.trim();
    const username = document.getElementById("usernameInput").value.trim();
    
    if (!email || !username) {
        alert("Please enter both email and username");
        return;
    }

    fetch("/auth/register?email=" + encodeURIComponent(email) + 
          "&username=" + encodeURIComponent(username), {
        method: "POST"
    })
    .then(res => {
        if (!res.ok) {
            return res.text().then(text => {
                throw new Error(text || "HTTP " + res.status);
            });
        }
        return res.text();
    })
    .then(jwt => {
        token = jwt;  // STORE TOKEN
        alert("Registration successful! You are now logged in.");
        document.getElementById("result").textContent = "Registered and logged in successfully! You can now call services.";
        toggleRegister(); // Hide registration fields
    })
    .catch(err => {
        const errorMsg = err.message || err;
        alert("Registration failed: " + errorMsg);
        document.getElementById("result").textContent = "Registration error: " + errorMsg;
    });
}

function login() {
    const email = document.getElementById("userIdInput").value.trim();
    
    if (!email) {
        alert("Please enter an email address");
        return;
    }

    fetch("/auth/login?email=" + encodeURIComponent(email), {
        method: "POST"
    })
    .then(res => {
        if (!res.ok) {
            return res.text().then(text => {
                throw new Error(text || "HTTP " + res.status);
            });
        }
        return res.text();
    })
    .then(jwt => {
        token = jwt;  // STORE TOKEN
        alert("Login successful!");
        document.getElementById("result").textContent = "Logged in successfully! You can now call services.";
    })
    .catch(err => {
        const errorMsg = err.message || err;
        if (errorMsg.includes("404") || errorMsg.includes("not found")) {
            alert("User not found. Please register first.");
            document.getElementById("result").textContent = "User not found. Click 'Register' to create an account.";
        } else {
            alert("Login failed: " + errorMsg);
            document.getElementById("result").textContent = "Login error: " + errorMsg;
        }
    });
}

function callService(service) {
    if (!token) {
        alert("Please login first!");
        document.getElementById("result").textContent = "Error: Please login before calling services.";
        return;
    }
    
    let url = "";

    if (service === "users") url = "/users";
    if (service === "marketplace") url = "/listings";
    if (service === "transactions") {
        // For transactions, we need a transaction ID
        const transactionId = prompt("Enter Transaction ID:");
        if (!transactionId || transactionId.trim() === "") {
            document.getElementById("result").textContent = "Error: Transaction ID is required";
            return;
        }
        url = "/transactions/" + transactionId.trim();
    }

    if (!url) {
        document.getElementById("result").textContent = "Error: Unknown service";
        return;
    }

    fetch(url, {
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(res => {
        if (!res.ok) {
            return res.text().then(text => {
                throw new Error(text || "HTTP " + res.status);
            });
        }
        return res.json();
    })
    .then(data => {
        document.getElementById("result").textContent =
            JSON.stringify(data, null, 2);
    })
    .catch(err => {
        document.getElementById("result").textContent =
            "Error connecting to " + service + ": " + err;
    });
}
