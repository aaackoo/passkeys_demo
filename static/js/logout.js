async function logout() {
    const resp = await fetch('/logout', {
        method: 'GET'
    });

    if (!resp.ok) {
        alert(`Server returned ${resp.status} - ${resp.statusText}`);
        throw new Error(`Server returned ${resp.status} - ${resp.statusText}`);
    }

    alert('Logged out');
    window.location.href = "/";
}