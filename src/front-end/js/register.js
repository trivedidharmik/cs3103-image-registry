document.addEventListener("DOMContentLoaded", function() {
    document.querySelector("form").addEventListener("submit", async (e) => {
        e.preventDefault();

        const username = document.getElementById("username").value;
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const errorBox = document.getElementById("error-box");

        const response = await fetch("/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                username: username,
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (response.status === 200 && data.redirect) {
            errorBox.classList.add('d-none');
            window.location.href = data.redirect;
        } else {
            errorBox.textContent = data.message;
            errorBox.classList.remove("d-none");
        }
    });
});