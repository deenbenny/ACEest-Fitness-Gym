"""ACEest Fitness & Gym - workout tracking API."""
from flask import Flask, jsonify, request

app = Flask(__name__)

workouts = []


@app.route("/")
def home():
    return jsonify(message="Welcome to ACEest Fitness & Gym"), 200


@app.route("/health")
def health():
    return jsonify(status="ok"), 200


@app.route("/workouts", methods=["GET"])
def get_workouts():
    return jsonify(workouts=workouts), 200


@app.route("/add_workout", methods=["POST"])
def add_workout():
    data = request.get_json(silent=True) or {}
    workout = data.get("workout")
    duration = data.get("duration")

    if not workout or duration is None:
        return jsonify(error="Both 'workout' and 'duration' are required"), 400

    if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration <= 0:
        return jsonify(error="'duration' must be a positive number"), 400

    entry = {"id": len(workouts) + 1, "workout": workout, "duration": duration}
    workouts.append(entry)
    return jsonify(message="Workout added", workout=entry), 201


@app.route("/delete_workout/<int:workout_id>", methods=["DELETE"])
def delete_workout(workout_id):
    global workouts
    before = len(workouts)
    workouts = [w for w in workouts if w["id"] != workout_id]
    if len(workouts) == before:
        return jsonify(error="Workout not found"), 404
    return jsonify(message="Workout deleted"), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
