const form = document.querySelector('form');

form.addEventListener('submit', (event) => {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const alertBox = document.getElementById('alertBox');

    if (!username || !password) {
        alert('Please fill in both fields.');
        return;
    }

    fetch('/accounts/login_p/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.message) {
                alertBox.className = 'alert success';
                alertBox.textContent = 'Login successful!';
                alertBox.hidden = false;
                window.location.href = data.href;
            } else {
                alertBox.className = 'alert error';
                alertBox.textContent = data.error;
                alertBox.hidden = false;
            }
        })
        .catch((error) => console.error('Error:', error));
});