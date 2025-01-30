async function getSecret() {
    const resp = await fetch('/current_user_string', {
        method: 'GET',
    });

    if (!resp.ok) {
        alert('Not authenticated!');
        window.location.href = "login";
    }

    let json = await resp.json();

    return json.my_string;
}

document.addEventListener("DOMContentLoaded", async () => {
    const heading = document.querySelector("h1");

    const x = await getSecret();

    if (x === null) {
        alert('Not authenticated!');
        window.location.href = "login";
        return;
    }

    heading.textContent = `Your secret is: "${x}"!`;
});

