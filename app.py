from flask import Flask, jsonify, request, render_template, redirect, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure SQLite database location
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///portfolio.db"
# To silence the modification tracking warning overhead
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Define the Project model
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    tech = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tech": self.tech,
        }


# Automatically create the database tables if they don't exist
with app.app_context():
    db.create_all()


# --- HTML Frontend Routes ---


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/projects")
def get_projects_html():
    projects = db.session.scalars(db.select(Project)).all()
    return render_template("projects.html", projects=projects)


@app.route("/add", methods=["GET", "POST"])
def add_project_form():
    if request.method == "POST":
        # Using .get() prevents KeyError crashes if a field is missing
        name = request.form.get("name")
        description = request.form.get("description")
        tech = request.form.get("tech")

        if not name or not description or not tech:
            return "Missing required fields", 400

        new_project = Project(name=name, description=description, tech=tech)
        db.session.add(new_project)
        db.session.commit()
        return redirect("/projects")

    return render_template("add_project.html")


# --- JSON API Routes ---


# GET all projects as JSON (Useful if you want to connect a frontend framework later)
@app.route("/api/projects", methods=["GET"])
def get_projects_json():
    projects = db.session.scalars(db.select(Project)).all()
    return jsonify([project.to_dict() for project in projects])


# POST - add a new project via JSON API
@app.route("/api/projects", methods=["POST"])
def add_project_api():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()

    # Simple validation payload check
    required_fields = ["name", "description", "tech"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    new_project = Project(
        name=data["name"], description=data["description"], tech=data["tech"]
    )
    db.session.add(new_project)
    db.session.commit()
    return jsonify(new_project.to_dict()), 201


# DELETE a project safely
@app.route("/api/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    project = db.session.get(Project, project_id)

    # If the project doesn't exist, handle it safely instead of crashing
    if not project:
        return jsonify({"error": "Project not found"}), 404

    db.session.delete(project)
    db.session.commit()
    return jsonify({"message": f"Project {project_id} successfully deleted"})


if __name__ == "__main__":
    app.run(debug=True)
