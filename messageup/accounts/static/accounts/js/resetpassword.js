const form = document.querySelector('form');

form.addEventListener('submit', (event) => {
    event.preventDefault();

    const newPassword = form.querySelector('input[name="new_password"]').value;
    const confirmPassword = form.querySelector('input[name="confirm_password"]').value;
    if (newPassword !== confirmPassword) {
        alert('Passwords do not match!');
        return;
    }

    fetch('', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            new_password: newPassword,
            confirm_password: confirmPassword,
            token: window.location.pathname.split('/').filter(Boolean).pop()
        })
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                alert('Password reset successful!');
                window.location.href = '/accounts/login/';
            } else {
                alert(data.error);
            }
        });
});

function getCookie(name) {
    const cookie = document.cookie.split('; ').find((item) => item.startsWith(`${name}=`));
    return cookie ? decodeURIComponent(cookie.split('=').slice(1).join('=')) : null;
}