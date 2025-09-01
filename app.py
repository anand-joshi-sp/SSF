import os
import json
from flask import Flask, request, Response
import base64

app = Flask(__name__)

def decode_jwt(token):
    """Decode JWT (header + payload, ignore signature)."""
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return {"error": "Not a JWT"}
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        decoded = base64.urlsafe_b64decode(payload.encode()).decode()
        return json.loads(decoded)
    except Exception as e:
        return {"error": f"Failed to decode: {str(e)}"}

@app.route("/ssf", methods=["POST"])
def ssf():
    try:
        # Log headers
        print("📑 Headers:", dict(request.headers))

        # Log raw body
        raw_body = request.data.decode("utf-8").strip()
        print("📩 Raw body:", raw_body)

        # If verification event (JSON with challenge)
        if raw_body.startswith("{"):
            data = request.get_json(force=True, silent=True)
            print("📜 Parsed JSON body:", json.dumps(data, indent=2))
            if data and data.get("event") == "stream.verification":
                challenge = data.get("challenge")
                print("✅ Verification challenge received:", challenge)
                return Response(challenge, status=202, content_type="text/plain; charset=utf-8")
            return Response("OK", status=202, content_type="text/plain; charset=utf-8")

        # Otherwise assume JWT (SET token)
        print("🔑 Encoded token (raw):", raw_body)
        decoded = decode_jwt(raw_body)
        print("📜 Decoded payload:", json.dumps(decoded, indent=2))

        return Response("Accepted", status=202, content_type="text/plain; charset=utf-8")

    except Exception as e:
        print("❌ Error handling request:", str(e))
        return Response("Internal Server Error", status=500, content_type="text/plain; charset=utf-8")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
