import os
from flask import Flask, request, Response

app = Flask(__name__)

@app.route("/ssf", methods=["POST"])
def ssf():
    try:
        data = request.get_json(force=True, silent=True)
        if data and data.get("event") == "stream.verification":
            challenge = data.get("challenge")
            print("✅ Received verification challenge:", challenge)
            # Respond exactly with the challenge, plain text
            return Response(challenge, status=200, mimetype="text/plain")

        # For all other SSF events
        print("📩 Received SSF event:", data)
        return Response("OK", status=200, mimetype="text/plain")

    except Exception as e:
        print("❌ Error handling request:", str(e))
        return Response("Internal Server Error", status=500, mimetype="text/plain")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render provides $PORT
    app.run(host="0.0.0.0", port=port)
