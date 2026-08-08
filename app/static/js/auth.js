async function submitAuth(endpoint, email, password) {
    try {
        const response = await fetch(endpoint, {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });


        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            showError(data.detail || `Request failed (${response.status})`);
            return;
        }
        // FastAPI sets the session cookie automatically.
        // Browser stores it because credentials:"include" is enabled.
        window.location.href = "/";

    }
    catch (error) {
        console.error(error);
        showError("Couldn't reach the server.");
    }
}



function showError(message) {
    const errorBox = document.getElementById("error-message");
    if (errorBox) {
        errorBox.textContent = message;
    }
}

const loginForm = document.getElementById("login-form");

if (loginForm) {

    loginForm.addEventListener(
        "submit",
        (event) => {
            event.preventDefault();
            const email = document.getElementById("login-email").value.trim();
            const password = document.getElementById("login-password").value;
            submitAuth("/auth/login",email,password);
        }
    );
}

const signupForm = document.getElementById("signup-form");
if (signupForm) {
    signupForm.addEventListener(
        "submit",
        (event) => {
            event.preventDefault();
            const email = document.getElementById("signup-email").value.trim();
            const password = document.getElementById("signup-password").value;
            submitAuth("/auth/signup",email,password);
        }
    );
}