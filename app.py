import os
from flask import Flask, request, Response

app = Flask(__name__)

@app.route("/ssf", methods=["POST"])
def ssf():
    data = request.json
    if data and data.get("event") == "stream.verification":
        challenge = data.get("challenge")
        print("Verification challenge received:", challenge)
        return Response(challenge, status=200, mimetype="text/plain")
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render provides $PORT
    app.run(host="0.0.0.0", port=port)
