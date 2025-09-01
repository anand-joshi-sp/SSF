import os
import json
from flask import Flask, request, Response
import base64

app = Flask(__name__)

def decode_jwt(token):
    """
    Simple JWT decode (header + payload only, without signature validation).
    """
    try:
        header, payload, signature = token.split(".")
        # Add padding for base64 decode
        payload += "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload.encode()).decode()
        return json.loads(decoded)
    except Exception as e:
        return {"error": f"Failed to decode JWT: {str(e)}"}

@app.route("/ssf", methods=["POST"])
def ssf():
    try:
        raw_body = request.data.decode("utf-8").strip()
        print("📩 Raw request body:", raw_body)

        # Case 1: Verification event (JSON body)
        if raw_body.startswith("{"):
            data = request.get_json(force=True, silent=True)
            if data and data.get("event") == "stream.verification":
                challenge = data.get("challenge")
                print("✅ Verification challenge received:", challenge)
                return Response(
                    response=challenge,
                    status=202,
                    headers={"Content-Type": "text/plain; charset=utf-8"}
                )
            print("📩 Received JSON SSF event:", data)
            return Response("OK", status=202, headers={"Content-Type": "text/plain; charset=utf-8"})

        # Case 2: Real SSF event (JWT body)
        print("🔑 Received SET token (encoded):", raw_body)
        decoded = decode_jwt(raw_body)
        print("📜 Decoded SET payload:", json.dumps(decoded, indent=2))

        return Response("Accepted", status=202, headers={"Content-Type": "text/plain; charset=utf-8"})

    except Exception as e:
        print("❌ Error handling request:", str(e))
        return Response(
            response="Internal Server Error",
            status=500,
            headers={"Content-Type": "text/plain; charset=utf-8"}
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render provides $PORT
    app.run(host="0.0.0.0", port=port)
