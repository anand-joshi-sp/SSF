from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

# In-memory store
streams = {}
access_tokens = {}
token_scopes = {}

# Token endpoint
@app.route('/oauth/token', methods=['POST'])
def token():
    client_id = request.form.get("client_id")
    client_secret = request.form.get("client_secret")
    grant_type = request.form.get("grant_type")
    scope = request.form.get("scope", "")

    if client_id == "test-client-id" and client_secret == "test-client-secret" and grant_type == "client_credentials":
        token = str(uuid.uuid4())
        access_tokens[token] = True
        token_scopes[token] = scope.split()
        return jsonify({
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": scope
        })
    return jsonify({"error": "invalid_client"}), 401

# Auth + Scope check
def check_auth(required_scope="ssf.manage"):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return False
    token = auth.split(" ")[1]
    if token not in access_tokens:
        return False
    if required_scope not in token_scopes.get(token, []):
        return False
    return True

# Create stream
@app.route('/api/v1/ssf/stream', methods=['POST'])
def create_stream():
    if not check_auth():
        return jsonify({"error": "unauthorized"}), 401
    data = request.json
    stream_id = str(uuid.uuid4())
    stream_data = {
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
    streams[stream_id] = stream_data
    return jsonify(stream_data), 201

# Get all streams or specific via query param
@app.route('/api/v1/ssf/stream', methods=['GET'])
def list_streams():
    if not check_auth():
        return jsonify({"error": "unauthorized"}), 401
    stream_id = request.args.get("stream_id")
    if stream_id:
        stream = streams.get(stream_id)
        if not stream:
            return jsonify({"error": "not found"}), 404
        return jsonify(stream), 200
    else:
        return jsonify(list(streams.values())), 200

# Get specific stream via path param
@app.route('/api/v1/ssf/stream/<stream_id>', methods=['GET'])
def get_stream(stream_id):
    if not check_auth():
        return jsonify({"error": "unauthorized"}), 401
    stream = streams.get(stream_id)
    if not stream:
        return jsonify({"error": "not found"}), 404
    return jsonify(stream), 200

# Delete stream
@app.route('/api/v1/ssf/stream/<stream_id>', methods=['DELETE'])
def delete_stream(stream_id):
    if not check_auth():
        return jsonify({"error": "unauthorized"}), 401
    if stream_id in streams:
        del streams[stream_id]
        return '', 204
    return jsonify({"error": "not found"}), 404

# Well-known SSF config (no auth required)
@app.route('/.well-known/ssf-configuration', methods=['GET'])
def ssf_config():
    return jsonify({
        "issuer": "https://mock-idp.com",
        "jwks_uri": "https://mock-idp.com/oauth2/v1/keys",
        "token_endpoint": "http://localhost:5000/oauth/token",
        "scopes_supported": ["ssf.manage"],
        "response_types_supported": ["token"]
    })

if __name__ == '__main__':
    app.run(debug=True)
