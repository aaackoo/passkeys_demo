import {
    create,
    parseCreationOptionsFromJSON,
} from '/static/js/webauthn-json.browser-ponyfill.js';

async function registerBegin(username, myString) {
    const resp = await fetch('/register/begin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username, my_string: myString })
    });

    if (!resp.ok) {
        if (resp.status === 401) {
            alert('User already exists');
            return;
        }
        alert(`Unidentified error: ${resp.status} - ${resp.statusText}`);
        throw new Error(`Server returned ${resp.status} - ${resp.statusText}`);
    }

    let json = await resp.json();
    let options = parseCreationOptionsFromJSON(json);

    let response = await create(options);
    let result = await fetch('/register/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(response)
    });

    if (!result.ok) {
        if (result.status === 409) {
            alert('No register in progress');
            return;
        }
        alert(`Unidentified error: ${result.status} - ${result.statusText}`);
        throw new Error(`Server returned ${result.status} - ${result.statusText}`);
    }

    let stat = result.ok ? 'ok' : 'failed';
    alert('Registration ' + stat);
}

document.getElementById('registerForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const secret = document.getElementById('secret').value;

    registerBegin(username, secret);
});