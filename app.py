import os
from flask import Flask, request, Response

app = Flask(__name__)

@app.route("/ssf", methods=["POST"])
def ssf():
    try:
        data = request.get_json(force=True, silent=True)

        # Handle verification event
        if data and data.get("event") == "stream.verification":
            challenge = data.get("challenge")
            print("✅ Verification challenge received:", challenge)
            return Response(
                response=challenge,
                status=202,
                headers={"Content-Type": "text/plain; charset=utf-8"}
            )

        # Handle all other SSF events
        print("📩 Received SSF event:", data)
        return Response(
            response="OK",
            status=202,
            headers={"Content-Type": "text/plain; charset=utf-8"}
        )

    except Exception as e:
        print("❌ Error handling request:", str(e))
        return Response(
            response="Internal Server Error",
            status=500,
            headers={"Content-Type": "text/plain; charset=utf-8"}
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT
    app.run(host="0.0.0.0", port=port)

