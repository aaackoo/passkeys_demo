# Passkeys demo app by Adam Šupej

My app is a Flask-based web application that implements **passkeys authentication** using **FIDO2 WebAuthn**. It demonstrates registration and authentication flow using passkeys, storing user credentials in a PostgreSQL database. Each user has some kind of secret message which he would like to store somewhere so no one could see it :). Here you can do so!

---

## Table of Contents
- [Deployment](#deployment)
- [Routes](#routes)
- [Usage](#usage)
- [Deployment](#deployment)

---
## Deployment
This app has been deployed to a domain `supej.me` which is being hosted on an ARM hetzner cloud server. Server hosts it’s own postgreSQL database.

## Routes

### 1. HTML Views
| Route           | Method | Description         |
|----------------|--------|---------------------|
| `/`            | GET    | Renders `index.html` |
| `/register`    | GET    | Renders `register.html` |
| `/login`       | GET    | Renders `login.html` |
| `/secret`      | GET    | Renders `secret.html` |
| `/logout`      | GET    | Logs out the user |

### 2. API Endpoints
| Route                  | Method | Description |
|------------------------|--------|-------------|
| `/register/begin`      | POST   | Initiates user registration |
| `/register/complete`   | POST   | Completes registration with passkey |
| `/login/begin`         | POST   | Initiates authentication |
| `/login/complete`      | POST   | Completes authentication |
| `/current_user_string` | GET    | Returns stored string for logged-in user |
| `/check_login`         | GET    | Checks if user is logged in |

---

## Usage
Access the app at: `supej.me`

### Registering a User
1. Navigate to `/register`
2. Enter a **username** and **secret** to store.
3. Follow the **passkey registration flow**.

### Logging In
1. Navigate to `/login`
2. Enter your **username**.
3. Authenticate using your passkey.