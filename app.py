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
