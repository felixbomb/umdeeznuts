from flask import Flask, jsonify, render_template
from script import get_upcoming_departures
import config

app = Flask(__name__)
@app.route("/api/departures")
def departures():
    data = get_upcoming_departures()
    return jsonify(data)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)