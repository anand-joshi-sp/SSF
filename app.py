from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

# In-memory storage
streams = {}
access_tokens = {}

# OAuth Token Endpoint with scope validation
@app.route('/oauth/token', methods=['POST'])
def token():
    client_id = request.form.get("client_id")
    client_secret = request.form.get("client_secret")
    grant_type = request.form.get("grant_type")
    scope = request.form.get("scope")

    if (client_id == "test-client-id" and
        client_secret == "test-client-secret" and
        grant_type == "client_credentials" and
        scope == "ssf.manage"):

        token = str(uuid.uuid4())
        access_tokens[token] = True
        return jsonify({
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": 3600
        })

    return jsonify({"error": "invalid_client"}), 401

# Authentication Check
def check_auth():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False
    token = auth_header.split(" ")[1]
    return token in access_tokens

# Create Stream
@app.route('/api/v1/ssf/stream', methods=['POST'])
def create_stream():
    if not check_auth():
        return jsonify({"error": "unauthorized"}), 401
    data = request.json
    stream_id = str(uuid.uuid4())
    streams[stream_id] = {
        "stream_id": stream_id,
        "delivery": data.get("delivery"),
        "format": data.get("format", "iss_sub"),
        "iss": "https://mock-idp.com",
        "aud": data.get("delivery", {}).get("endpoint_url"),
        "events_supported": [
            "https://schemas.openid.net/secevent/caep/event-type/session-revoked",
            "https://schemas.openid.net/secevent/caep/event-type/credential-change"
        ],
        "events_requested": data.get("events_requested", []),
        "events_delivered": [],
        "min_verification_interval": 900
    }
    return jsonify(streams[stream_id]), 201

# Get Streams
@app.route('/api/v1/ssf/stream', methods=['GET'])
def list_streams():
    if not check_auth():
        return jsonify({"error": "unauthorized"}), 401
    return jsonify(list(streams.values())), 200

# Delete Stream
@app.route('/api/v1/ssf/stream/<stream_id>', methods=['DELETE'])
def delete_stream(stream_id):
    if not check_auth():
        return jsonify({"error": "unauthorized"}), 401
    if stream_id in streams:
        del streams[stream_id]
        return '', 204
    return jsonify({"error": "not found"}), 404

# Well-known Config
@app.route('/.well-known/ssf-configuration', methods=['GET'])
def ssf_config():
    return jsonify({
        "issuer": "https://mock-idp.com",
        "token_endpoint": "https://<your-app>.onrender.com/oauth/token",
        "scopes_supported": ["ssf.manage"]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
