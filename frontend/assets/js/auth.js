document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const res = await fetch('http://localhost:5000/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        if (!res.ok) throw new Error('Invalid credentials');
        const data = await res.json();
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        localStorage.setItem('user', JSON.stringify(data.user));

        const role = data.user.role;
        if (role === 'student') {
            window.location.href = 'student_portal.html';
        } else {
            window.location.href = 'dashboard.html';
        }
    } catch (err) {
        const errorEl = document.getElementById('error');
        errorEl.textContent = err.message;
        errorEl.classList.remove('hidden');
    }
});
