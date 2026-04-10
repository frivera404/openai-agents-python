"""
WorkerA API Server

- Accepts POST requests at /api/webhook
- Logs events to a local SQLite database (workera.db)
- Handles event types: sale, contact, agent event
- Ready for systeme.io, Stripe, OpenAI webhooks
- Minimal, extensible, and secure (verifies secret if provided)

Instructions:
1. Install dependencies: pip install flask python-dotenv
2. Create a .env file with: WORKER_WEBHOOK_SECRET=your_secret_here (optional)
3. Run: python workerA_api_server.py

"""
import os
import sqlite3
import requests
from datetime import datetime
from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
WORKER_WEBHOOK_SECRET = os.getenv("WORKER_WEBHOOK_SECRET") or os.getenv("WEBHOOK_SECRET")
WORKER_WEBHOOK_URL = os.getenv("WORKER_WEBHOOK_URL")
CLAWCODE_API_URL = os.getenv("CLAWCODE_API_URL")
DB_FILE = "workera.db"

# Homepage route
@app.route("/", methods=["GET"])
def home():
    return "<h2>WorkerA API is running</h2><p>POST to /api/webhook to log events.</p>", 200

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create required tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            provider TEXT,
            event_type TEXT,
            payload TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            name TEXT,
            email TEXT,
            source TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS workera_api_content (
            type TEXT,
            key TEXT,
            value TEXT,
            description TEXT
        )
        """
    )
    conn.commit()
    conn.close()

@app.route("/api/webhook", methods=["POST"])
def webhook():
    if WORKER_WEBHOOK_SECRET:
        secret = request.headers.get("X-Webhook-Secret")
        if secret != WORKER_WEBHOOK_SECRET:
            abort(401, description="Invalid secret.")
    data = request.get_json(force=True, silent=True)
    if not data:
        abort(400, description="Invalid JSON payload.")
    provider = request.headers.get("X-Provider", "unknown")
    event_type = data.get("event", data.get("type", "unknown"))
    payload = str(data)
    # Log event to database
    conn = get_db()
    conn.execute(
        "INSERT INTO events (timestamp, provider, event_type, payload) VALUES (?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), provider, event_type, payload)
    )
    # If new contact, add to contacts table
    if event_type in ["new_contact", "contact.created"]:
        name = data.get("name") or data.get("full_name") or data.get("contact", {}).get("name")
        email = data.get("email") or data.get("contact", {}).get("email")
        source = provider
        conn.execute(
            "INSERT INTO contacts (created_at, name, email, source) VALUES (?, ?, ?, ?)",
            (datetime.utcnow().isoformat(), name, email, source)
        )
    conn.commit()
    conn.close()
    
    # If configured, forward command-type events to an upstream CLAWCODE_API_URL
    try:
        is_command = False
        # common command indicators
        if isinstance(data, dict):
            if data.get("type") == "command" or data.get("event") == "command":
                is_command = True
            if "command" in data or data.get("action") == "run_command":
                is_command = True

        if CLAWCODE_API_URL and is_command:
            headers = {"Content-Type": "application/json"}
            # forward secret as header if present (downstream services expect it)
            if WORKER_WEBHOOK_SECRET:
                headers["X-Webhook-Secret"] = WORKER_WEBHOOK_SECRET
            # Forward in a non-blocking safe manner with a short timeout
            try:
                requests.post(CLAWCODE_API_URL, json=data, headers=headers, timeout=5)
            except Exception:
                # Don't fail the webhook if forwarding fails; just continue
                pass

    except Exception:
        # keep webhook resilient; do not expose internal errors
        pass

    return jsonify({"status": "ok"})


@app.route("/api/integrations/wordpress/domain-connect", methods=["POST"])
def wp_domain_connect():
    """Proxy a Domain Connect request to WordPress and log the result."""
    payload = request.get_json(force=True, silent=True)
    if not payload:
        abort(400, description="Invalid JSON payload.")

    # Determine endpoint from DB or fallback
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT value FROM workera_api_content WHERE type = ? AND key = ?",
        ("integration", "wordpress_domain_connect")
    )
    row = cur.fetchone()
    endpoint = row[0] if row and row[0] else os.getenv("WORDPRESS_DOMAIN_CONNECT_URL", "https://public-api.wordpress.com/rest/v1.3/domain-connect")

    headers = {"Content-Type": "application/json"}
    token = os.getenv("WP_API_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        try:
            resp_body = resp.json()
        except ValueError:
            resp_body = resp.text
        status_code = resp.status_code
    except Exception as e:
        # Log the error and return
        conn.execute(
            "INSERT INTO events (timestamp, provider, event_type, payload) VALUES (?, ?, ?, ?)",
            (datetime.utcnow().isoformat(), "wordpress", "domain_connect.error", str(e))
        )
        conn.commit()
        conn.close()
        return jsonify({"error": str(e)}), 502

    # Log response to events table
    conn.execute(
        "INSERT INTO events (timestamp, provider, event_type, payload) VALUES (?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), "wordpress", "domain_connect.response", str(resp_body))
    )
    conn.commit()
    conn.close()

    return jsonify({"status": status_code, "response": resp_body}), status_code

if __name__ == "__main__":
    # Ensure DB tables exist before starting
    init_db()
    app.run(host="0.0.0.0", port=5000)
