import psycopg2
import os

from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy

from fido2.server import Fido2Server
from fido2.webauthn import (
    UserVerificationRequirement,
    PublicKeyCredentialRpEntity,
    PublicKeyCredentialUserEntity,
    AttestedCredentialData
)

import fido2.features

fido2.features.webauthn_json_mapping.enabled = True

# -----------------------------------------------------
# Flask configuration
# -----------------------------------------------------
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")

# -----------------------------------------------------
# Database configuration
# postgreSQL
# -----------------------------------------------------
credentials = []
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -----------------------------------------------------
# Relaying Party (RP) configuration
# -----------------------------------------------------
# RP_ID = "dev.local"  # DEBUG
RP_ID = "supej.me"  # DEPLOY
RP_NAME = "Passkeys Demo"
rp = PublicKeyCredentialRpEntity(name=RP_NAME, id=RP_ID)

# -----------------------------------------------------
# Server configuration
# -----------------------------------------------------
fido2_server = Fido2Server(rp)

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"))
    return conn

def execute_cmd(cmd):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(cmd)
    conn.commit()
    cur.close()
    conn.close()

def insert_user(username, my_string):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO users (username, my_string, credentials)'
                'VALUES (%s, %s, %s)',
                (username, my_string, None))
    conn.commit()
    cur.close()
    conn.close()

def set_credentials(username, credential_data):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE users SET credentials = %s WHERE username = %s',
                (psycopg2.Binary(bytes(credential_data)), username))
    conn.commit()
    cur.close()
    conn.close()

def user_exists(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT EXISTS(SELECT 1 FROM users WHERE username = %s)', (username,))
    exists = cur.fetchone()[0]
    cur.close()
    conn.close()

    if exists:
        return True
    return False

def get_credentials(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT credentials FROM users WHERE username = %s', (username,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    
    if result:
        return result[0]
    
    return None

def get_my_string(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT my_string FROM users WHERE username = %s', (username,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    return result[0]

# -----------------------------------------------------
# HTML Templates
# -----------------------------------------------------
@app.route("/")
def index():
    return render_template('/index.html')

@app.route('/register')
def register():
    return render_template('/register.html')

@app.route('/login')
def authenticate():
    return render_template('/login.html')

@app.route('/secret')
def secret():
    return render_template('/secret.html')

@app.route("/logout")
def logout():
    session.pop("state")
    session.pop("user_id")
    session.pop("logged_in_user", None)
    return render_template("/logout.html")

# -----------------------------------------------------
# Registration
# -----------------------------------------------------
@app.route("/register/begin", methods=["POST"])
def register_begin():
    """
    Return registration_data for the user to register, or error message.
    """
    data = request.json
    username = data.get("username")
    my_string = data.get("my_string")

    if user_exists(username):
        return jsonify({"status": "failed", "reason": "User already exists"}), 401

    insert_user(username, my_string)

    try:
        registration_data, state = fido2_server.register_begin(
            PublicKeyCredentialUserEntity(
                id=b"user_id",
                name=username,
                display_name=username,
            ),
            credentials,
            user_verification=UserVerificationRequirement.PREFERRED,
            authenticator_attachment=None,
            resident_key_requirement=None,
        )

        session["state"] = state
        session["user_id"] = username

        return jsonify(dict(registration_data))
    except Exception as e:
        return jsonify({"status": "failed", "reason": str(e)}), 400

@app.route("/register/complete", methods=["POST"])
def register_complete():
    """
    Return status and error message.
    """
    data = request.get_json()

    state = session.get("state")
    username = session.get("user_id")

    if not state or not username:
        return jsonify({"status": "failed", "reason": "No login in progress"}), 409

    try:
        auth_data = fido2_server.register_complete(
            state,
            data
        )

        set_credentials(username, auth_data.credential_data)

        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "failed", "reason": str(e)}), 400

# -----------------------------------------------------
# Login
# -----------------------------------------------------
@app.route("/login/begin", methods=["POST"])
def login_begin():
    """
    Return auth_data for the user to authenticate, or error message.
    """
    data = request.json
    username = data.get("username")

    if not user_exists(username):
        return jsonify({"status": "failed", "reason": "User not found"}), 404

    credentials = get_credentials(username)

    if credentials == None:
        return jsonify({"status": "failed", "reason": "Credentials not found"}), 404

    attest = AttestedCredentialData(bytes(credentials))

    try:
        auth_data, state = fido2_server.authenticate_begin([attest])
        session["state"] = state
        session["user_id"] = username

        return jsonify(dict(auth_data))
    except Exception as e:
            return jsonify({"status": "failed", "reason": str(e)}), 400

@app.route("/login/complete", methods=["POST"])
def login_complete():
    """
    Return status and error message.
    """
    data = request.get_json()

    state = session.get("state")
    username = session.get("user_id")

    if not state or not username:
        return jsonify({"status": "failed", "reason": "No login in progress"}), 409

    credentials = get_credentials(username)

    if credentials == None:
        return jsonify({"status": "failed", "reason": "Credentials not found"}), 404
    
    attest = AttestedCredentialData(bytes(credentials))

    try:
        fido2_server.authenticate_complete(
            state,
            [attest],
            data,
        )
        session["logged_in_user"] = username
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "failed", "reason": str(e)}), 400

# -----------------------------------------------------
# Get current user's custom string
# -----------------------------------------------------
@app.route("/current_user_string", methods=["GET"])
def get_current_user_string():
    """
    Return the my_string for the currently logged-in user (if any).
    """
    username = session.get("logged_in_user")
    if username:
        if user_exists(username):
            secret = get_my_string(username)
            return jsonify({"my_string": secret})

    return jsonify({"my_string": None})
    
# -----------------------------------------------------
# Check if the user is logged in
# -----------------------------------------------------
@app.route("/check_login", methods=["GET"])
def logged_in_check():
    """
    Return object with logged_in bool and username of logged-in user (if any).
    """
    username = session.get("logged_in_user")
    if username:
        if user_exists(username):
            return jsonify({"logged_in": True, "user": username})

    return jsonify({"logged_in": False})

# -----------------------------------------------------
# Run the Flask app
# -----------------------------------------------------
if __name__ == "__main__":
    print("Starting Flask app...")
    db.create_all()
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )
