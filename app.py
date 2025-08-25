from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

# In-memory storage
streams = {}
access_tokens = {}

# Token endpoint (with scope enforcement)
@app.route('/oauth/token', methods=['POST'])
def token():
    client_id = request.form.get("client_id")
    client_secret = request.form.get("client_secret")
    grant_type = request.form.get("grant_type")
    scope = request.form.get("scope", "")

    if client_id == "test-client-id" and client_secret == "test-client-secret" \
            and grant_type == "client_credentials" and "ssf.manage" in scope.split():
        token = str(uuid.uuid4())
        access_tokens[token] = True
        return jsonify({
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": 3600
        })
    return jsonify({"error": "invalid_client_or_scope"}), 401

# Auth check with scope validation
def check_auth():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False
    token = auth_header.split(" ")[1]
    return token in access_tokens

# Create SSF Stream
@app.route('/api/v1/ssf/stream', methods=['POST'])
def create_stream():
    if not check_auth():
        return jsonify({"error": "unauthorized"}), 401

    data = request.json or {}
    stream_id = str(uuid.uuid4())
    stream_data = {
        "stream_id": stream_id,
        "delivery": data.get("delivery"),
        "format": data.get("format", "iss_sub"),
        "iss": "https://ssf-6g58.onrender.com",
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

# Get all streams or by query param
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
    return jsonify(list(streams.values())), 200

# Get specific stream by path param
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

# Well-known SSF Configuration (Okta-style, Render URL)
@app.route('/.well-known/ssf-configuration', methods=['GET'])
def ssf_config():
    return jsonify({
        "configuration_endpoint": "https://ssf-6g58.onrender.com/api/v1/ssf/stream",
        "delivery_methods_supported": [
            "https://schemas.openid.net/secevent/risc/delivery-method/push",
            "urn:ietf:rfc:8935"
        ],
        "issuer": "https://ssf-6g58.onrender.com",
        "jwks_uri": "https://ssf-6g58.onrender.com/oauth2/v1/keys",
        "spec_version": "1_0-ID3",
        "verification_endpoint": "https://ssf-6g58.onrender.com/api/v1/ssf/stream/verification",
        "authorization_schemes": [
            {
                "spec_urn": "urn:ietf:rfc:6749"
            }
        ],
        "default_subjects": "ALL"
    })

# JWKS endpoint simulation (Okta-style)
@app.route('/oauth2/v1/keys', methods=['GET'])
def jwks():
    # Dummy RSA public key (replace with real if needed)
    return jsonify({
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "kid": "test-key-id",
                "alg": "RS256",
                "n": "sXchZXFSpXgmJAjlJm5bRrqlh1X1XoMEBG6M7m9G2Oft4T3HBylWllO9sUpKxYbiNbi3sZT_xCgR9Stt9XbI4bQnTk1IiwSK9DMySVH8Pu4O_0TInJlXGvjh8UeVYhG4J-cq0pXZ5o2b3zMxeIr9U9-vr7v6kH6vRloObVvn8WQ",
                "e": "AQAB"
            }
        ]
    })
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

