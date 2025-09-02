import sys
import os
import json
from flask import Flask, request, Response
import base64

# Flush logs immediately
sys.stdout.reconfigure(line_buffering=True)

app = Flask(__name__)

def decode_jwt(token):
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
    headers = dict(request.headers)
    raw_body = request.get_data(as_text=True).strip()

    print("📑 Headers:", headers)
    print("📩 Raw body (len={}): {}".format(len(raw_body), raw_body))

    # Verification flow
    if raw_body.startswith("{"):
        try:
            data = request.get_json(force=True, silent=True)
            print("📜 Parsed JSON:", json.dumps(data, indent=2))
            if data and data.get("event") == "stream.verification":
                challenge = data.get("challenge")
                print("✅ Challenge:", challenge)
                return Response(challenge, status=202, content_type="text/plain; charset=utf-8")
        except Exception as e:
            print("❌ JSON parse error:", str(e))

    # Real SSF event (assume JWT)
    if raw_body:
        print("🔑 Encoded JWT:", raw_body)
        decoded = decode_jwt(raw_body)
        print("📜 Decoded JWT:", json.dumps(decoded, indent=2))

    return Response("Accepted", status=202, content_type="text/plain; charset=utf-8")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
