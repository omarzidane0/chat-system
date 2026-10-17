const form = document.querySelector('form');

form.addEventListener('submit', (event) => {
    event.preventDefault();

    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    if (password !== confirmPassword) {
        alert('Passwords do not match!');
        return;
    }

    fetch('/accounts/register_p/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username: document.getElementById('username').value,
            password,
            email: document.getElementById('email').value
        })
    })
        .then((response) => response.json())
        .then((data) => {
            const alertBox = document.getElementById('alertBox');
            if (data.error) {
                alertBox.className = 'alert error';
                alertBox.textContent = data.error;
            } else {
                alertBox.className = 'alert success';
                alertBox.textContent = data.message;
                setTimeout(() => {
                    window.location.href = '/accounts/login/';
                }, 2000);
            }
            alertBox.hidden = false;
        })
        .catch((error) => console.error('Error:', error));
});