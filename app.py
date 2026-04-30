from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello Gaurab! Your Flask server is running."

@app.route("/about")
def about():
    return jsonify({
        "name": "Gaurab Kunwar",
        "role": "Python Developer",
        "skills": ["Python", "Flask", "Git"],
        "github": "github.com/gaurab-kunwar"
    })

@app.route("/projects")
def projects():
    return jsonify([
        {
            "name": "Portfolio API",
            "description": "A REST API built with Flask",
            "tech": ["Python", "Flask"]
        }
    ])

if __name__ == "__main__":
    app.run(debug=True)