import {
    get,
    parseRequestOptionsFromJSON,
} from '/static/js/webauthn-json.browser-ponyfill.js';

async function loginBegin(username) {
    const resp = await fetch('/login/begin', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username })
    });
  
    if (!resp.ok) {
        if (resp.status === 400) {
            alert('User does not exist');
            return;
        }
        alert(`Unidentified error: ${resp.status} - ${resp.statusText}`);
        throw new Error(`Server returned ${resp.status} - ${resp.statusText}`);
    }
  
    let json = await resp.json();
    let opt = parseRequestOptionsFromJSON(json);
    
    let response = await get(opt);
    let result = await fetch('/login/complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(response)
    });

    if (!result.ok) {
        if (result.status === 409) {
            alert('No login request found');
            return;
        }
        if (result.status === 404) {
            alert('Credentials for a given user dont exist');
            return;
        }
        alert(`Unidentified error: ${result.status} - ${result.statusText}`);
        throw new Error(`Server returned ${result.status} - ${result.statusText}`);
    }
  
    let stat = result.ok ? 'ok' : 'failed';
    alert('Login ' + stat);
    if (stat === 'ok') {
        window.location.href = "secret";
    }
}

async function loginStatus() {
    const response = await fetch("/check_login");
    const data = await response.json();

    if (!data.logged_in) { return }
    window.location.href = "secret";
}

document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const username = document.getElementById('loginUsername').value;

    loginBegin(username);
});

loginStatus();