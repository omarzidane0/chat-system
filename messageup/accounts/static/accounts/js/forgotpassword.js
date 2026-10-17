const form = document.querySelector('form');
const alertBox = document.getElementById('alertBox');

form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const email = document.getElementById('email').value;

    try {
        const response = await fetch('/accounts/forgot-password/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (response.ok) {
            alertBox.textContent = data.message;
            alertBox.className = 'alert success';
        } else {
            alertBox.textContent = data.error || 'An error occurred.';
            alertBox.className = 'alert error';
        }
    } catch (error) {
        alertBox.textContent = 'An error occurred.';
        alertBox.className = 'alert error';
    }

    alertBox.hidden = false;
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}