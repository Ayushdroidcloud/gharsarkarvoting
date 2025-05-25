from flask import Flask, render_template, request, jsonify
import time

app = Flask(__name__)

# Global variables to simulate storage (reset on server restart)
votes = {}  # voterCode -> party
TIMER_DURATION = 10 * 60  # 10 minutes in seconds
start_time = None  # stores start timestamp in seconds


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/timer", methods=["GET", "POST"])
def timer():
    global start_time
    if request.method == "GET":
        # Return start time as epoch seconds, or 0 if not started
        return jsonify({"startTime": start_time or 0})
    else:
        # Start the timer (only if not started)
        if start_time is None:
            start_time = int(time.time())
        return jsonify({"startTime": start_time})


@app.route("/api/votes", methods=["GET", "POST", "DELETE"])
def api_votes():
    global votes
    if request.method == "GET":
        return jsonify(votes)
    elif request.method == "POST":
        data = request.json
        voter_code = data.get("voterCode")
        party = data.get("party")
        now = int(time.time())

        # Check if voting started
        if start_time is None or (now - start_time) > TIMER_DURATION:
            return jsonify({"error": "Voting time is over."}), 400

        if not voter_code or not party:
            return jsonify({"error": "Missing voterCode or party."}), 400

        if voter_code in votes:
            return jsonify({"error": "You have already voted."}), 400

        votes[voter_code] = party
        return jsonify({"message": "Vote saved."})

    elif request.method == "DELETE":
        votes = {}
        return jsonify({"message": "Votes cleared."})


@app.route("/api/winner")
def winner():
    counts = {"BBP": 0, "RSM": 0}
    for p in votes.values():
        if p in counts:
            counts[p] += 1
    if counts["BBP"] > counts["RSM"]:
        win = "Bhartiya Bacha Party (BBP)"
    elif counts["RSM"] > counts["BBP"]:
        win = "Rashtriya Siblings Morcha (RSM)"
    else:
        win = "It's a Tie"
    return jsonify({"winner": win, "counts": counts})


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

