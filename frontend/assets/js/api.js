async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem('access_token');
    if (!token) { window.location.href = '../index.html'; return; }
    const headers = { 'Authorization': 'Bearer ' + token, ...options.headers };
    if (options.body) {
        headers['Content-Type'] = 'application/json';
    }
    const response = await fetch(url, { ...options, headers });
    if (response.status === 401) {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
            const res = await fetch('/api/auth/refresh', {
                method: 'POST',
                headers: { 'Authorization': 'Bearer ' + refreshToken }
            });
            if (res.ok) {
                const data = await res.json();
                localStorage.setItem('access_token', data.access_token);
                return fetchWithAuth(url, options);
            }
        }
        window.location.href = '../index.html';
    }
    return response.json();
}
